from py2neo import Graph, Node, NodeMatcher, RelationshipMatcher


class Population:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", '123456'))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.type = ""
        self.name = ""

    def search(self, search_type, population_name):
        self.type = search_type
        if population_name in ['男', '男性', '男人']:
            self.name = '男性'
        elif population_name in ['女', '女性', '女人']:
            self.name = '女性'
        elif population_name in ['老人', '老年', '老年人']:
            self.name = '老年'
        elif population_name in ['儿童', '小儿', '小孩', '孩子', '新生儿']:
            self.name = '儿童'
        elif population_name in ['孕产', '产妇', '产期', '孕妇', '孕期']:
            self.name = '孕产'
        if self.type == "disease":
            return self.disease()

    def disease(self):
        cql = f"match(n:disease)-[]->(p:population) where p.name='{self.name}' " \
            f"return n.name as disease order by n.proportion desc limit 25"
        data = []
        for disease in self.graph.run(cql).data():
            data.append(disease['disease'])
        # print(data)
        return data


if __name__ == '__main__':
    handler = Population()
    handler.search("disease", "小孩")
