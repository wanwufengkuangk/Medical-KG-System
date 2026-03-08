from py2neo import Graph, Node, NodeMatcher, RelationshipMatcher


class Department:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", '123456'))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.search_type = ""
        self.name = ""
        self.alpha_order = False

    def search(self, search_type, department_name, alpha_order=False):
        self.search_type = search_type
        self.name = department_name
        self.alpha_order = alpha_order
        if search_type == "disease":
            return self.disease()

    def disease(self):
        if self.alpha_order:
            cql = f"match(p:department)-[]->(n:disease) where p.name='{self.name}' " \
                f"with n.name as disease order by disease return disease limit 25"
        else:
            cql = f"match(p:department)-[]->(n:disease) where p.name='{self.name}' " \
                f"return n.name as disease order by n.proportion desc limit 25"
        data = self.graph.run(cql).data()
        # print(data)
        return data


if __name__ == '__main__':
    handler = Department()
    handler.search("disease", "外科", alpha_order=True)
