from py2neo import Graph, Node, NodeMatcher, RelationshipMatcher

from Neo4j import disease
from Neo4j.config import neo4j as config_neo4j


class Symptom:
    def __init__(self):
        self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
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

    # 关系
    def disease(self):
        """
        查询症状可能患有的疾病
        :return: 疾病列表
        """
        cql = f"match(p:symptom)-[]->(n:disease) where p.name='{self.name}' " \
            f"return n.name as disease"
        data = []
        for disease in self.graph.run(cql).data():
            data.append(disease['disease'])
        # print("disease", data)
        return data

    def symptom(self):
        """
        查询症状常见症状
        :return: 症状列表
        """
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
        """
        查询症状简介
        :return: 列表
        """
        cql = f"match(n:symptom) where n.name='{self.name}' return n.brief as brief"
        data = self.graph.run(cql).data()[0]['brief']
        if data is None:
            return []
        else:
            data = data.split('\n')
            data = data[:int((len(data)/2))]
        return data

    def cause(self):
        """
        查询症状病因解析
        :return: 病因段落列表
        """
        cql = f"match(n:symptom) where n.name='{self.name}' return n.cause as cause"
        data = self.graph.run(cql).data()[0]['cause']
        if data is not None:
            data = data.split('\n')
        # print("cause", data)
        return data

    def check(self):
        """
        查询症状检查解析
        :return: 检查段落列表
        """
        cql = f"match(n:symptom) where n.name='{self.name}' return n.check as check"
        data = self.graph.run(cql).data()[0]['check']
        if data is not None:
            data = data.split('\n')
        # print("check", data)
        return data

    def diagnose(self):
        """
        查询症状诊断解析
        :return: 诊断段落列表
        """
        cql = f"match(n:symptom) where n.name='{self.name}' return n.diagnose as diagnose"
        data = self.graph.run(cql).data()[0]['diagnose']
        if data is not None:
            data = data.split('\n')
        # print("diagnose", data)
        return data

    def prevent(self):
        """
        查询症状预防措施
        :return: 预防段落列表
        """
        cql = f"match(n:symptom) where n.name='{self.name}' return n.prevent as prevent"
        data = self.graph.run(cql).data()[0]['prevent']
        if data is not None:
            data = data.split('\n')
        return data

    def symptom_info(self, symptom_name):
        self.name = symptom_name
        if self.node_matcher.match("symptom").where(f"_.name = '{self.name}'").first() is None:
            return None
        data = dict()
        data['symptom'] = self.name
        data['brief'] = self.brief()
        data['cause'] = self.cause()
        data['check'] = self.check()
        data['diagnose'] = self.diagnose()
        data['prevent'] = self.prevent()
        data['r_disease'] = []
        handler = disease.Disease()
        for jib in self.disease():
            data['r_disease'].append({'name': jib, 'r_symptom': ' '.join(handler.search('symptom', jib))})
        data['r_symptom'] = self.symptom()
        return data

    def symptom_info_brief(self, symptom_name):
        # data = {
        #     "症状": f"{self.name}",
        #     "概述": ""
        # }
        self.name = symptom_name
        data = dict()
        data['症状'] = self.name
        data['概述'] = ' '.join(self.brief())
        return data

    def fuzzy_search(self, search_text):
        cql = f"match(n:symptom) where n.name=~'.*{search_text}.*' return n.name as name"
        symptoms = []
        for symptom in self.graph.run(cql).data():
            symptoms.append(symptom['name'])
        return symptoms


if __name__ == '__main__':
    handler = Symptom()
    handler.search("", "头痛")
    handler.disease()
    handler.symptom()
    handler.brief()
    handler.cause()
    handler.check()
    handler.diagnose()
    handler.prevent()
    # handler.symptom_info('失眠')
