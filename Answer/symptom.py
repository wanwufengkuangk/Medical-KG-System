from py2neo import Graph, Node, NodeMatcher, RelationshipMatcher


class Symptom:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687", auth=("neo4j", '123456'))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.type = ""
        self.name = ""

    def search(self, search_type, symptom_name):
        self.type = search_type
        self.name = symptom_name
        if self.type == "brief":
            return self.brief()
        elif self.type == "cause":
            return self.cause()
        elif self.type == "check":
            return self.check()
        elif self.type == "diagnose":
            return self.diagnose()
        elif self.type == "prevent":
            return self.prevent()
        elif self.type == "disease":
            return self.disease()
        elif self.type == "symptom":
            return self.symptom()
        else:
            return ""

    def symptom_info(self):

        return

    def symptom_info_brief(self):

        return

    # 关系
    def disease(self):
        cql = f"match(p:symptom)-[]->(n:disease) where p.name='{self.name}' " \
            f"return n.name as disease"
        data = []
        for disease in self.graph.run(cql).data():
            data.append(disease['disease'])
        # print("disease", data)
        return data

    def symptom(self):
        cql = f"match(p:symptom)-[]->(n:symptom) where p.name='{self.name}' " \
            f"return n.name as symptom"
        data = []
        for symptom in self.graph.run(cql).data():
            data.append(symptom['symptom'])
        # cql = f"match(n:symptom)-[]->(p:symptom) where p.name='{self.name}' " \
        #     f"return n.name as symptom"
        # data.extend(self.graph.run(cql).data())
        # print("symptom", data)
        return data

    # 属性
    def brief(self):
        cql = f"match(n:symptom) where n.name='{self.name}' return n.brief as brief"
        data = self.graph.run(cql).data()[0]['brief'].split('\n')[0]
        # print("brief", data)
        return data

    def cause(self):
        cql = f"match(n:symptom) where n.name='{self.name}' return n.cause as cause"
        data = self.graph.run(cql).data()[0]['cause']
        # print("cause", data)
        return data

    def check(self):
        cql = f"match(n:symptom) where n.name='{self.name}' return n.check as check"
        data = self.graph.run(cql).data()[0]['check']
        # print("check", data)
        return data

    def diagnose(self):
        cql = f"match(n:symptom) where n.name='{self.name}' return n.diagnose as diagnose"
        data = self.graph.run(cql).data()[0]['diagnose']
        # print("diagnose", data)
        return data

    def prevent(self):
        cql = f"match(n:symptom) where n.name='{self.name}' return n.prevent as prevent"
        data = self.graph.run(cql).data()[0]['prevent']
        # print("prevent", data)
        return data


if __name__ == '__main__':
    handler = Symptom()
    handler.search("", "失眠")
    handler.disease()
    handler.symptom()
    handler.brief()
    handler.cause()
    handler.check()
    handler.diagnose()
    handler.prevent()
