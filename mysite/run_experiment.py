# run_experiment.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MultiLabelBinarizer
from py2neo import Graph
import joblib
import warnings
warnings.filterwarnings("ignore") # 忽略一些不影响结果的警告

print("--- 开始毕业设计核心实验 ---")

# 1. 加载数据
print("1. 正在从 Neo4j 加载数据...")
graph = Graph("http://localhost:7474", auth=("neo4j", "666666")) # 确保密码正确
query = "MATCH (d:disease)-[:disease_symptom]->(s:symptom) RETURN d.name AS disease, collect(s.name) AS symptoms"
data = graph.run(query).data()
df = pd.DataFrame(data)

print(f"成功加载 {len(df)} 条疾病数据。")

# 2. 特征工程
print("2. 正在进行特征转换...")
mlb = MultiLabelBinarizer(sparse_output=True)
X = mlb.fit_transform(df['symptoms'])
y = df['disease']

# 3. 划分数据集 (70% 训练，30% 测试)
print("3. 正在划分训练集与测试集...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 4. 加载你训练好的模型
print("4. 正在加载已训练的朴素贝叶斯模型...")
try:
    clf = joblib.load('nb_model.pkl')
except FileNotFoundError:
    print("错误：找不到 nb_model.pkl 模型文件！请先运行 train_ml_model.py。")
    exit()

# 5. 在测试集上进行预测
print("5. 正在对 30% 的测试数据进行预测评估...")
y_pred = clf.predict(X_test)

# 6. 计算并打印评估指标
print("\n--- 智能诊断模块实验评估报告 ---")
accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ 模型总体准确率 (Accuracy): {accuracy:.2%}\n")

print("📊 详细分类报告 (Precision, Recall, F1-Score):")
# target_names 可以限制只显示部分疾病，None 则显示全部
report = classification_report(y_test, y_pred, target_names=None)
print(report)
print("------------------------------------")