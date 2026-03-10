from py2neo import Graph, NodeMatcher, RelationshipMatcher
from Neo4j import disease
from Neo4j.config import neo4j as config_neo4j


class Alias:
    def __init__(self):
        self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.search_type = ""
        self.name = ""
        self.disease = disease.Disease()

    def search(self, search_type, alias_name):
        self.search_type = search_type
        self.name = alias_name
        disease_name = self.disease_name()
        return self.disease.search(self.search_type, disease_name)

    # 关系
    def disease_name(self):
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
    handler = Alias()
    print(handler.search("cause", "头疼"))
    # # 打印每个国家2010年的人口数量
    #     for pop_dict in pop_data:
    #         country_name = pop_dict['Country Name']
    #         population = pop_dict['Value']
    #         print(country_name + ": " + population)
