from py2neo import Graph

# 这里的密码请写死成你 Neo4j 7474 里的那个，比如 12345678
PASSWORD = "666666"

# 1. 给 disease.py 用的字典格式
neo4j = {
    "url": "http://localhost:7474",
    "username": "neo4j",
    "password": PASSWORD
}

# 2. 给 views.py 或其它地方可能直接用的变量名
graph = Graph("http://localhost:7474", auth=("neo4j", PASSWORD))
neo4j_obj = graph

print(">>> 数据库配置统一加载成功")