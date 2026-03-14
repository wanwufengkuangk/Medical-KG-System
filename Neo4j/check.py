from py2neo import Graph, Node, NodeMatcher, RelationshipMatcher
import json
from Neo4j.config import neo4j as config_neo4j


class Check:
    def __init__(self):
        self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.search_type = ""
        self.name = ""

    def search(self, search_type, check_name):
        self.search_type = search_type
        self.name = check_name
        if search_type == "disease":
            return self.disease()

    def disease(self):
        cql = f"match(n:disease)-[]->(p:check) where p.name='{self.name}' " \
            f"return n.name as disease order by n.proportion desc"
        data = []
        for disease in self.graph.run(cql).data():
            data.append(disease['disease'])
        # print(data)
        return data


if __name__ == '__main__':
    handler = Check()
    handler.search("disease", "全血细胞计数")
