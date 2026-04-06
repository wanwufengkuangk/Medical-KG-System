import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import jieba
from collections import Counter
import joblib
import os

print("========== 1. 开始数据高质量预处理 ==========")

try:
    q_df = pd.read_csv('dataset/question.csv')
    a_df = pd.read_csv('dataset/answer.csv')
    disease_df = pd.read_csv('dataset/diseases.csv')
except FileNotFoundError:
    print("❌ 错误：找不到 dataset 文件夹下的相关 CSV 文件！")
    exit()

merged_df = pd.merge(a_df, q_df, on='question_id')
merged_df.rename(columns={'content_x': 'answer', 'content_y': 'question'}, inplace=True)

kg_diseases = disease_df['name'].dropna().tolist()
kg_diseases = list(set([d for d in kg_diseases if isinstance(d, str) and len(d) >= 2]))
kg_diseases.sort(key=len, reverse=True)

print("1.1 正在进行严格的实体对齐 (最长匹配去噪)...")


def extract_kg_disease(text):
    text = str(text)
    matches = [d for d in kg_diseases if d in text]
    if not matches:
        return None
    return max(matches, key=len)


merged_df['extracted_disease'] = merged_df['answer'].apply(extract_kg_disease)
labeled_df = merged_df.dropna(subset=['extracted_disease']).copy()

# 保持 200 的高阈值，只训练核心高发病
MIN_SAMPLES = 200
disease_counts = labeled_df['extracted_disease'].value_counts()
valid_diseases = disease_counts[disease_counts >= MIN_SAMPLES].index.tolist()

final_train_df = labeled_df[labeled_df['extracted_disease'].isin(valid_diseases)].copy()
final_train_df.rename(columns={'extracted_disease': 'label'}, inplace=True)
print(f"清洗完毕！提取到 {len(final_train_df)} 条高质量训练数据，精选 {len(valid_diseases)} 种核心疾病！")

print("========== 2. 中文分词与构建词表 ==========")
stop_words = set(
    ["的", "了", "呢", "啊", "怎么", "请问", "医生", "大夫", "患者", "感觉", "最近", "一直", "是什么", "怎么办",
     "谢谢"])


def clean_and_cut(text):
    words = jieba.cut(str(text))
    return [w for w in words if w not in stop_words and len(w.strip()) > 0]


final_train_df['words'] = final_train_df['question'].apply(clean_and_cut)

all_words = [word for words in final_train_df['words'] for word in words]
word_counts = Counter(all_words)
# 扩大词表到 15000，BiLSTM 更能捕捉生僻特征
vocab = {word: i + 2 for i, (word, count) in enumerate(word_counts.most_common(15000)) if count > 1}
vocab['<PAD>'] = 0
vocab['<UNK>'] = 1

# 序列长度加到 120，容纳更长的患者自述
MAX_LEN = 120


def encode_text(words):
    seq = [vocab.get(w, vocab['<UNK>']) for w in words]
    if len(seq) < MAX_LEN:
        seq += [vocab['<PAD>']] * (MAX_LEN - len(seq))
    else:
        seq = seq[:MAX_LEN]
    return seq


X_data = np.array([encode_text(w) for w in final_train_df['words']])

label_list = final_train_df['label'].unique().tolist()
label_dict = {label: idx for idx, label in enumerate(label_list)}
y_data = np.array([label_dict[label] for label in final_train_df['label']])

joblib.dump(vocab, 'text_vocab.pkl')
joblib.dump(label_dict, 'text_labels.pkl')

print("========== 3. 构建 PyTorch 数据集 ==========")
X_train, X_val, y_train, y_val = train_test_split(X_data, y_data, test_size=0.1, random_state=42)

# 注意这里强制指定了 dtype=torch.long 避免之前的报错
train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.long), torch.tensor(y_train, dtype=torch.long))
# 显卡够强，我们把 Batch Size 飙到 128
train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

val_dataset = TensorDataset(torch.tensor(X_val, dtype=torch.long), torch.tensor(y_val, dtype=torch.long))
val_loader = DataLoader(val_dataset, batch_size=256, shuffle=False)

print("========== 4. 定义 TextBiLSTM-Attention 高阶模型 ==========")


class TextBiLSTMAttention(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes):
        super(TextBiLSTMAttention, self).__init__()
        # 词嵌入层
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)

        # 双向 LSTM 层：抓取上下文时序特征 (Bidirectional=True)
        # 设定两层 LSTM (num_layers=2) 以提取更深层语义
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2,
                            bidirectional=True, batch_first=True, dropout=0.5)

        # 注意力机制权重参数
        self.w_omega = nn.Parameter(torch.Tensor(hidden_dim * 2, hidden_dim * 2))
        self.u_omega = nn.Parameter(torch.Tensor(hidden_dim * 2, 1))
        nn.init.uniform_(self.w_omega, -0.1, 0.1)
        nn.init.uniform_(self.u_omega, -0.1, 0.1)

        self.dropout = nn.Dropout(0.5)
        # 全连接层 (hidden_dim * 2 因为是双向)
        self.fc = nn.Linear(hidden_dim * 2, num_classes)

    def attention_net(self, x, query, mask=None):
        # x 维度: [batch_size, seq_len, hidden_dim*2]
        # 注意力得分计算
        u = torch.tanh(torch.matmul(x, self.w_omega))
        att = torch.matmul(u, self.u_omega)  # [batch_size, seq_len, 1]

        # 屏蔽掉 <PAD> 占位符的注意力权重
        if mask is not None:
            att = att.masked_fill(mask == 0, -1e9)

        att_score = F.softmax(att, dim=1)  # 得到每个词的权重分布

        # 将权重与 LSTM 输出加权求和，得到最终的句子级特征表示
        scored_x = x * att_score
        context = torch.sum(scored_x, dim=1)  # [batch_size, hidden_dim*2]
        return context, att_score

    def forward(self, x):
        # x: [batch_size, seq_len]
        mask = (x != 0).unsqueeze(-1)  # 找出非 padding 的实际单词

        embedded = self.embedding(x)  # [batch_size, seq_len, embed_dim]

        # LSTM 输出
        lstm_out, _ = self.lstm(embedded)  # lstm_out: [batch_size, seq_len, hidden_dim*2]

        # 经过 Attention 层提纯特征
        attn_out, _ = self.attention_net(lstm_out, query=None, mask=mask)

        # 经过 Dropout 与全连接层输出分类结果
        out = self.dropout(attn_out)
        out = self.fc(out)
        return out


VOCAB_SIZE = len(vocab)
EMBED_DIM = 256  # 维度翻倍
HIDDEN_DIM = 256  # LSTM 隐藏层维度
NUM_CLASSES = len(label_list)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🔥 核武器启动！当前使用设备: {device}")

model = TextBiLSTMAttention(VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM, NUM_CLASSES).to(device)

print("========== 5. 开始极速训练 (动态学习率+早停) ==========")

class_counts = np.bincount(y_train)
weights = 1.0 / (np.log1p(class_counts) + 1e-5)
weights = torch.tensor(weights, dtype=torch.float).to(device)

criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.1)
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

# 【高级技巧：余弦退火学习率】让模型在训练后期像微雕一样精细调整参数
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10, eta_min=0.0001)

best_val_loss = float('inf')
patience = 4
patience_counter = 0
best_model_state = None

epochs = 20
for epoch in range(epochs):
    model.train()
    train_loss = 0
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    scheduler.step()  # 学习率衰减
    avg_train_loss = train_loss / len(train_loader)

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for batch_X, batch_y in val_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            val_loss += loss.item()

    avg_val_loss = val_loss / len(val_loader)
    current_lr = optimizer.param_groups[0]['lr']

    print(
        f"Epoch [{epoch + 1}/{epochs}] | LR: {current_lr:.6f} | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")

    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        patience_counter = 0
        best_model_state = model.state_dict()
        print("  🌟 验证集 Loss 刷新历史最低，保存极品权重...")
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"🛑 连续 {patience} 轮未提升，触发早停机制，拯救显卡！")
            break

print("========== 6. 保存最终模型 ==========")
model.load_state_dict(best_model_state)
torch.save(model.to('cpu').state_dict(), 'bilstm_attention_model.pth')
print(f"✅ TextBiLSTM-Attention 模型训练大功告成！")