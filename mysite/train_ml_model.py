# train_ml_model.py (优化版：朴素贝叶斯 + 稀疏矩阵)
from py2neo import Graph
import pandas as pd
from sklearn.naive_bayes import MultinomialNB  # 换成了朴素贝叶斯算法
from sklearn.preprocessing import MultiLabelBinarizer
import joblib

print("1. 正在连接 Neo4j 数据库...")
graph = Graph("http://localhost:7474", auth=("neo4j", "666666")) # 确保密码是正确的

print("2. 正在提取疾病与症状的关联数据...")
query = """
MATCH (d:disease)-[:disease_symptom]->(s:symptom)
RETURN d.name AS disease, collect(s.name) AS symptoms
"""
data = graph.run(query).data()

if not data:
    print("❌ 错误：未能从数据库中提取到数据，请检查。")
    exit()

print(f"成功提取了 {len(data)} 种疾病的症状特征！")

print("3. 正在构建特征矩阵 (开启稀疏矩阵优化内存)...")
df = pd.DataFrame(data)
# 【防爆内存的核心】：sparse_output=True 让矩阵变成稀疏存储，内存占用骤降 99%！
mlb = MultiLabelBinarizer(sparse_output=True)
X = mlb.fit_transform(df['symptoms'])
y = df['disease']

print("4. 正在训练 朴素贝叶斯 (Naive Bayes) 模型...")
clf = MultinomialNB()
clf.fit(X, y)

print("5. 正在保存模型文件...")
# 保存的模型名字也改一下
joblib.dump(clf, 'nb_model.pkl')
joblib.dump(mlb.classes_, 'symptoms_list.pkl')

print("✅ 恭喜！机器学习模型训练完成！已生成 nb_model.pkl 和 symptoms_list.pkl")