from py2neo import Graph, NodeMatcher, RelationshipMatcher
from Neo4j import disease


class Alias:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", '123456'))
        # self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.search_type = ""
        self.name = ""

    def search(self, search_type, alias_name):
        self.search_type = search_type
        self.name = alias_name
        disease_name = self.disease()
        return disease.Disease.search(search_type, disease_name)

    # 关系
    def disease(self):
        """
        查询别名所对应的疾病
        :return: 疾病
        """
        cql = f"match(n:disease)-[]->(p:alias) where p.name='{self.name}' " \
            f"return n.name as disease"
        data = self.graph.run(cql).data()[0]['disease']
        # print(data)
        return data



if __name__ == '__main__':
    handler = Disease()
    handler.search("", "失眠")
    # # 关系
    # handler.alias()
    # handler.kind()
    # handler.department()
    # handler.disease()
    # handler.symptom()
    # handler.drug()
    # # 属性
    # handler.brief()
    # handler.check()
    # handler.method()
    # handler.fee()
    # handler.infect()
    # handler.cure_period()
    # handler.cure_rate()
    # handler.proportion()
    # handler.population()

    handler.disease_info()
    handler.disease_info_brief()
