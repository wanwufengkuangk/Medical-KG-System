import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import jieba
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from matplotlib.font_manager import FontProperties

print("========== 1. 加载并准备测试数据 ==========")
try:
    q_df = pd.read_csv('dataset/question.csv')
    a_df = pd.read_csv('dataset/answer.csv')
except FileNotFoundError:
    print("找不到 CSV 文件，请检查路径。")
    exit()

merged_df = pd.merge(a_df, q_df, on='question_id')
merged_df.rename(columns={'content_x': 'answer', 'content_y': 'question'}, inplace=True)

# 加载我们在训练时保存的字典
try:
    vocab = joblib.load('text_vocab.pkl')
    label_dict = joblib.load('text_labels.pkl')
except FileNotFoundError:
    print("请先运行 train_textcnn.py 生成字典文件！")
    exit()

# 反向映射字典
idx2label = {v: k for k, v in label_dict.items()}
valid_diseases = list(label_dict.keys())


def extract_kg_disease(text):
    text = str(text)
    for d in valid_diseases:
        if d in text: return d
    return None


merged_df['label'] = merged_df['answer'].apply(extract_kg_disease)
final_df = merged_df.dropna(subset=['label']).copy()

# 文本编码与分词
stop_words = set(
    ["的", "了", "呢", "啊", "怎么", "请问", "医生", "大夫", "患者", "感觉", "最近", "一直", "是什么", "怎么办",
     "谢谢"])
MAX_LEN = 100


def encode_text(text):
    words = [w for w in jieba.cut(str(text)) if w not in stop_words and len(w.strip()) > 0]
    seq = [vocab.get(w, vocab['<UNK>']) for w in words]
    if len(seq) < MAX_LEN:
        seq += [vocab['<PAD>']] * (MAX_LEN - len(seq))
    else:
        seq = seq[:MAX_LEN]
    return seq


print("正在对所有文本进行编码转换...")
X_data = np.array([encode_text(text) for text in final_df['question']])
y_data = np.array([label_dict[label] for label in final_df['label']])

print("========== 2. 划分训练集与测试集 (8:2) ==========")
# 这里最关键！把数据打散，20% 留作考试用，绝对不让模型提前看到
# X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

# 1. 第一次划分：先分出 20% 作为最终的“高考卷 (Test Set)”
X_train_val, X_test, y_train_val, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

# 2. 第二次划分：从剩下的 80% 中，再分出 25% 作为“模拟考卷 (Val Set)” (相当于原始数据的 20%)
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, random_state=42)



# ====== 定义模型结构 (与训练时保持绝对一致) ======
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
        x = self.dropout(torch.cat((x1, x2, x3, x4), 1))
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        out = self.fc2(x)
        return out


VOCAB_SIZE = len(vocab)
EMBED_DIM = 200
NUM_CLASSES = len(label_dict)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print("========== 3. 开始过拟合验证训练 ==========")
# 重新初始化一个空模型
model = HeavyTextCNN(VOCAB_SIZE, EMBED_DIM, NUM_CLASSES).to(device)
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.Adam(model.parameters(), lr=0.0005, weight_decay=1e-4)

train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.long), torch.tensor(y_train, dtype=torch.long))
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

test_dataset = TensorDataset(torch.tensor(X_test, dtype=torch.long), torch.tensor(y_test, dtype=torch.long))
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

train_losses, test_losses = [], []
train_accs, test_accs = [], []

epochs = 15  # 测试 15 轮看趋势
for epoch in range(epochs):
    # --- 训练阶段 ---
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

    # --- 测试阶段 (不更新梯度) ---
    model.eval()
    test_loss, test_correct, test_total = 0, 0, 0
    y_true_all, y_pred_all = [], []
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)

            test_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            test_total += batch_y.size(0)
            test_correct += (predicted == batch_y).sum().item()

            y_true_all.extend(batch_y.cpu().numpy())
            y_pred_all.extend(predicted.cpu().numpy())

    test_losses.append(test_loss / len(test_loader))
    test_accs.append(test_correct / test_total)

    print(
        f"Epoch [{epoch + 1}/{epochs}] | Train Loss: {train_losses[-1]:.4f}, Train Acc: {train_accs[-1]:.2%} | Test Loss: {test_losses[-1]:.4f}, Test Acc: {test_accs[-1]:.2%}")

print("========== 4. 输出最终学术报告 ==========")
# 打印你在论文里需要的分类报告
print("\n【最终测试集评估报告】")
print(f"总体准确率 (Accuracy): {test_accs[-1]:.2%}")
# 为了防止打印太长，我们只显示前 15 种疾病的详细指标
target_names = [idx2label[i] for i in range(min(15, NUM_CLASSES))]
print(classification_report(y_true_all, y_pred_all, labels=range(len(target_names)), target_names=target_names))

print("========== 5. 绘制过拟合趋势图 ==========")
# 画图保存为图片，你可以直接插进毕业论文里
plt.figure(figsize=(12, 5))

# 损失曲线
plt.subplot(1, 2, 1)
plt.plot(range(1, epochs + 1), train_losses, label='Train Loss', marker='o')
plt.plot(range(1, epochs + 1), test_losses, label='Test Loss', marker='x', linestyle='--')
plt.title('Loss Curve (Check Overfitting)')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)

# 准确率曲线
plt.subplot(1, 2, 2)
plt.plot(range(1, epochs + 1), train_accs, label='Train Accuracy', marker='o')
plt.plot(range(1, epochs + 1), test_accs, label='Test Accuracy', marker='x', linestyle='--')
plt.title('Accuracy Curve')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('overfit_analysis_curve1.png')
print("✅ 评估曲线已保存为 overfit_analysis_curve.png，请查看项目根目录！")