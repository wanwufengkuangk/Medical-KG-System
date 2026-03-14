import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
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

print(f"1.1 正在进行严格的实体对齐...")


def extract_kg_disease(text):
    text = str(text)
    for d in kg_diseases:
        if d in text:
            return d
    return None


merged_df['extracted_disease'] = merged_df['answer'].apply(extract_kg_disease)
labeled_df = merged_df.dropna(subset=['extracted_disease']).copy()

# 【优化1：提高门槛，保证每个类都有足够的数据让模型学透】
MIN_SAMPLES = 50
disease_counts = labeled_df['extracted_disease'].value_counts()
valid_diseases = disease_counts[disease_counts >= MIN_SAMPLES].index.tolist()

final_train_df = labeled_df[labeled_df['extracted_disease'].isin(valid_diseases)].copy()
final_train_df.rename(columns={'extracted_disease': 'label'}, inplace=True)
print(f"清洗完毕！提取到 {len(final_train_df)} 条高质量训练数据，精选 {len(valid_diseases)} 种核心疾病！")

print("========== 2. 中文分词与强力去噪 ==========")
# 【优化2：加入基础停用词表，去除噪音干扰】
stop_words = set(
    ["的", "了", "呢", "啊", "怎么", "请问", "医生", "大夫", "患者", "感觉", "最近", "一直", "是什么", "怎么办",
     "谢谢"])


def clean_and_cut(text):
    words = jieba.cut(str(text))
    return [w for w in words if w not in stop_words and len(w.strip()) > 0]


final_train_df['words'] = final_train_df['question'].apply(clean_and_cut)

# 扩大词表，抓取更多细节
all_words = [word for words in final_train_df['words'] for word in words]
word_counts = Counter(all_words)
# 去掉只出现过1次的生僻词
vocab = {word: i + 2 for i, (word, count) in enumerate(word_counts.most_common(12000)) if count > 1}
vocab['<PAD>'] = 0
vocab['<UNK>'] = 1

MAX_LEN = 100  # 再次加长序列以容纳更多关键症状


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
X_tensor = torch.tensor(X_data, dtype=torch.long)
y_tensor = torch.tensor(y_data, dtype=torch.long)
dataset = TensorDataset(X_tensor, y_tensor)
dataloader = DataLoader(dataset, batch_size=64, shuffle=True)  # 减小 batch_size，让梯度更新更频繁

print("========== 4. 定义重装版 TextCNN 模型 ==========")


class HeavyTextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes):
        super(HeavyTextCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)

        # 【优化3：加宽网络，提取更丰富的 N-gram 特征】
        num_filters = 256
        self.conv1 = nn.Conv2d(1, num_filters, (2, embed_dim))
        self.conv2 = nn.Conv2d(1, num_filters, (3, embed_dim))
        self.conv3 = nn.Conv2d(1, num_filters, (4, embed_dim))
        self.conv4 = nn.Conv2d(1, num_filters, (5, embed_dim))  # 新增提取极长句特征

        self.dropout = nn.Dropout(0.6)  # 极高 dropout 防止死记硬背

        # 256 * 4 = 1024
        self.fc1 = nn.Linear(1024, 512)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.embedding(x).unsqueeze(1)

        x1 = F.max_pool1d(F.relu(self.conv1(x)).squeeze(3), x.size(2) - 1).squeeze(2)
        x2 = F.max_pool1d(F.relu(self.conv2(x)).squeeze(3), x.size(2) - 2).squeeze(2)
        x3 = F.max_pool1d(F.relu(self.conv3(x)).squeeze(3), x.size(2) - 3).squeeze(2)
        x4 = F.max_pool1d(F.relu(self.conv4(x)).squeeze(3), x.size(2) - 4).squeeze(2)

        x = torch.cat((x1, x2, x3, x4), 1)
        x = self.dropout(x)

        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        out = self.fc2(x)
        return out


VOCAB_SIZE = len(vocab)
EMBED_DIM = 200  # 提升词向量维度
NUM_CLASSES = len(label_list)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🔥 火力全开，使用设备: {device}")

model = HeavyTextCNN(VOCAB_SIZE, EMBED_DIM, NUM_CLASSES).to(device)

# 【优化4：带标签平滑的交叉熵，防止模型过于自信导致过拟合】
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
# 加入 weight_decay 进行 L2 正则化
optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-4)

print("========== 5. 开始极限训练 ==========")
epochs = 20  # 如果嫌慢可以改成 15
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for batch_X, batch_y in dataloader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)

        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch [{epoch + 1}/{epochs}], Loss: {total_loss / len(dataloader):.4f}")

print("========== 6. 保存重装模型 ==========")
torch.save(model.to('cpu').state_dict(), 'textcnn_model.pth')
print(f"✅ 模型训练完毕！")