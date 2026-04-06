import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import jieba
from collections import Counter
import joblib
import matplotlib.pyplot as plt

print("========== 1. 加载并准备测试数据 ==========")
try:
    q_df = pd.read_csv('dataset/question.csv')
    a_df = pd.read_csv('dataset/answer.csv')
    disease_df = pd.read_csv('dataset/diseases.csv')
except FileNotFoundError:
    print("找不到 CSV 文件，请检查路径。")
    exit()

merged_df = pd.merge(a_df, q_df, on='question_id')
merged_df.rename(columns={'content_x': 'answer', 'content_y': 'question'}, inplace=True)

kg_diseases = disease_df['name'].dropna().tolist()
kg_diseases = list(set([d for d in kg_diseases if isinstance(d, str) and len(d) >= 2]))
kg_diseases.sort(key=len, reverse=True)


def extract_kg_disease(text):
    text = str(text)
    matches = [d for d in kg_diseases if d in text]
    if not matches: return None
    return max(matches, key=len)


merged_df['extracted_disease'] = merged_df['answer'].apply(extract_kg_disease)
labeled_df = merged_df.dropna(subset=['extracted_disease']).copy()

# 保持和训练一致的 200 阈值
MIN_SAMPLES = 200
disease_counts = labeled_df['extracted_disease'].value_counts()
valid_diseases = disease_counts[disease_counts >= MIN_SAMPLES].index.tolist()

final_df = labeled_df[labeled_df['extracted_disease'].isin(valid_diseases)].copy()
final_df.rename(columns={'extracted_disease': 'label'}, inplace=True)

stop_words = set(
    ["的", "了", "呢", "啊", "怎么", "请问", "医生", "大夫", "患者", "感觉", "最近", "一直", "是什么", "怎么办",
     "谢谢"])


def clean_and_cut(text):
    words = jieba.cut(str(text))
    return [w for w in words if w not in stop_words and len(w.strip()) > 0]


final_df['words'] = final_df['question'].apply(clean_and_cut)

all_words = [word for words in final_df['words'] for word in words]
word_counts = Counter(all_words)
vocab = {word: i + 2 for i, (word, count) in enumerate(word_counts.most_common(12000)) if count > 1}
vocab['<PAD>'] = 0
vocab['<UNK>'] = 1

MAX_LEN = 100


def encode_text(words):
    seq = [vocab.get(w, vocab['<UNK>']) for w in words]
    if len(seq) < MAX_LEN:
        seq += [vocab['<PAD>']] * (MAX_LEN - len(seq))
    else:
        seq = seq[:MAX_LEN]
    return seq


X_data = np.array([encode_text(w) for w in final_df['words']])
label_list = final_df['label'].unique().tolist()
label_dict = {label: idx for idx, label in enumerate(label_list)}
idx2label = {v: k for k, v in label_dict.items()}
y_data = np.array([label_dict[label] for label in final_df['label']])

print("========== 2. 划分严谨的三集 (Train / Val / Test) ==========")
# 第一次划分：留出 20% 作为最终的高考卷
X_temp, X_test, y_temp, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)
# 第二次划分：剩下的分出 20% 作为模拟卷
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)


class HeavyTextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes):
        super(HeavyTextCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        num_filters = 256
        self.conv1 = nn.Conv2d(1, num_filters, (2, embed_dim))
        self.conv2 = nn.Conv2d(1, num_filters, (3, embed_dim))
        self.conv3 = nn.Conv2d(1, num_filters, (4, embed_dim))
        self.conv4 = nn.Conv2d(1, num_filters, (5, embed_dim))
        self.dropout = nn.Dropout(0.6)
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
EMBED_DIM = 200
NUM_CLASSES = len(label_list)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = HeavyTextCNN(VOCAB_SIZE, EMBED_DIM, NUM_CLASSES).to(device)

class_counts = np.bincount(y_train)
weights = 1.0 / (np.log1p(class_counts) + 1e-5)
weights = torch.tensor(weights, dtype=torch.float).to(device)
criterion = nn.CrossEntropyLoss(weight=weights, label_smoothing=0.1)
optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-4)

train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.long), torch.tensor(y_train, dtype=torch.long))
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

val_dataset = TensorDataset(torch.tensor(X_val, dtype=torch.long), torch.tensor(y_val, dtype=torch.long))
val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)

test_dataset = TensorDataset(torch.tensor(X_test, dtype=torch.long), torch.tensor(y_test, dtype=torch.long))
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

train_losses, val_losses = [], []
train_accs, val_accs = [], []
epochs = 20

print("========== 3. 开始模型验证训练 ==========")
for epoch in range(epochs):
    model.train()
    train_loss, train_correct, train_total = 0, 0, 0
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        train_total += batch_y.size(0)
        train_correct += (predicted == batch_y).sum().item()

    train_losses.append(train_loss / len(train_loader))
    train_accs.append(train_correct / train_total)

    model.eval()
    val_loss, val_correct, val_total = 0, 0, 0
    with torch.no_grad():
        for batch_X, batch_y in val_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)

            val_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            val_total += batch_y.size(0)
            val_correct += (predicted == batch_y).sum().item()

    val_losses.append(val_loss / len(val_loader))
    val_accs.append(val_correct / val_total)

    print(f"Epoch [{epoch + 1}/{epochs}] | Train Acc: {train_accs[-1]:.2%} | Val Acc: {val_accs[-1]:.2%}")

print("\n========== 4. 在测试集上输出最终报告 (含 Top-3) ==========")
model.eval()
y_true_all, y_pred_all = [], []
top3_correct = 0
total_samples = 0

with torch.no_grad():
    for batch_X, batch_y in test_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        outputs = model(batch_X)

        # Top-1 预测 (用于分类报告)
        _, predicted = torch.max(outputs.data, 1)
        y_true_all.extend(batch_y.cpu().numpy())
        y_pred_all.extend(predicted.cpu().numpy())

        # 【核心优化4】：计算 Top-3 Accuracy
        _, top3_preds = torch.topk(outputs.data, 3, dim=1)
        for i in range(batch_y.size(0)):
            if batch_y[i] in top3_preds[i]:
                top3_correct += 1
        total_samples += batch_y.size(0)

print("\n【最终绝密测试集评估报告】")
print(f"🥇 Top-1 准确率 (Accuracy): {accuracy_score(y_true_all, y_pred_all):.2%}")
print(f"🥉 Top-3 准确率 (Top-3 Acc): {top3_correct / total_samples:.2%}")

target_names = [idx2label[i] for i in range(min(20, NUM_CLASSES))]
print("\n📊 详细分类报告 (部分展示):")
print(classification_report(y_true_all, y_pred_all, labels=range(len(target_names)), target_names=target_names,
                            zero_division=0))

print("========== 5. 绘制过拟合趋势图 ==========")
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(range(1, epochs + 1), train_losses, label='Train Loss', marker='o')
plt.plot(range(1, epochs + 1), val_losses, label='Validation Loss', marker='x', linestyle='--')
plt.title('Loss Curve (Check Overfitting)')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(range(1, epochs + 1), train_accs, label='Train Accuracy', marker='o')
plt.plot(range(1, epochs + 1), val_accs, label='Validation Accuracy', marker='x', linestyle='--')
plt.title('Accuracy Curve')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('overfit_analysis_curve.png')
print("✅ 评估曲线已保存为 overfit_analysis_curve.png！")