from py2neo import Graph, Node, NodeMatcher, RelationshipMatcher
from Neo4j.config import neo4j as config_neo4j


class Drug:
    def __init__(self):
        self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.search_type = ""
        self.name = ""

    # 关系
    def disease(self):
        """
        查询药物相关疾病
        :return: 疾病列表
        """
        cql = f"match(n:disease)-[r:disease_drug]->(p:drug) where p.name='{self.name}' " \
            f"return n.name as disease order by n.proportion desc"
        data = []
        for disease in self.graph.run(cql).data():
            data.append(disease['disease'])
        # print(data)
        if data is None:
            return []
        else:
            return data

    def form(self):
        """
        查询药物剂型
        :return: 剂型列表
        """
        cql = f"match(n:form)-[r:form_drug]->(p:drug) where p.name='{self.name}' " \
            f"return n.name as form"
        data = []
        for form in self.graph.run(cql).data():
            data.append(form['form'])
        # print(data)
        if data is None:
            return []
        else:
            data = ' '.join(data)
            return data

    def function(self):
        """
        查询药物主要功能
        :return: 主要功能段落列表
        """
        cql = f"match(n:drug) where n.name='{self.name}' return n.function as function"
        data = self.graph.run(cql).data()[0]['function']
        if data is None:
            return ''
        else:
            data = data.split('\n')
            # print(data)
            return data

    def usage(self):
        """
        查询药物用法
        :return: 用法段落列表
        """
        cql = f"match(n:drug) where n.name='{self.name}' return n.usage as usage"
        data = self.graph.run(cql).data()[0]['usage']
        if data is None:
            return ''
        else:
            data = data.split('\n')
            # print(data)
            return data

    def component(self):
        """
        查询药物成份
        :return: 成份段落列表
        """
        cql = f"match(n:drug) where n.name='{self.name}' return n.component as component"
        data = self.graph.run(cql).data()[0]['component']
        if data is None:
            return ''
        else:
            data = data.split('\n')
            # print(data)
            return data

    def effects(self):
        """
        查询药物不良反应
        :return: 不良反应段落列表
        """
        cql = f"match(n:drug) where n.name='{self.name}' return n.effects as effects"
        data = self.graph.run(cql).data()[0]['effects']
        if data is None:
            return ''
        else:
            data = data.split('\n')
            # print(data)
            return data

    def avoid(self):
        """
        查询药物禁忌
        :return: 禁忌段落列表
        """
        cql = f"match(n:drug) where n.name='{self.name}' return n.avoid as avoid"
        data = self.graph.run(cql).data()[0]['avoid']
        if data is None:
            return ''
        else:
            data = data.split('\n')
            # print(data)
            return data

    def matters(self):
        """
        查询药物注意事项
        :return: 注意事项段落列表
        """
        cql = f"match(n:drug) where n.name='{self.name}' return n.matters as matters"
        data = self.graph.run(cql).data()[0]['matters']
        if data is None:
            return ''
        else:
            data = data.split('\n')
            # print(data)
            return data

    def search(self, search_type, drug_name):
        self.search_type = search_type
        self.name = drug_name
        if search_type == "disease":
            return self.disease()
        elif search_type == "form":
            return self.form()
        elif search_type == "function":
            return self.function()
        elif search_type == "usage":
            return self.usage()
        elif search_type == "component":
            return self.component()
        elif search_type == "effects":
            return self.effects()
        elif search_type == "avoid":
            return self.avoid()
        elif search_type == "matters":
            return self.matters()

    def drug_info(self, drug_name):
        self.name = drug_name
        if self.node_matcher.match("drug").where(f"_.name = '{self.name}'").first() is None:
            return None
        data = dict()
        data['通用名称'] = self.name
        data['功能主治'] = self.function()
        data['用法用量'] = self.usage()
        data['剂型'] = self.form()
        data['成份'] = self.component()
        data['不良反应'] = self.effects()
        data['禁忌'] = self.avoid()
        data['注意事项'] = self.matters()
        print(data)
        return data

    def drug_info_brief(self, drug_name):
        # data = {
        #     "通用名称": f"{self.name}",
        #     "功能主治": ""
        # }
        self.name = drug_name
        data = dict()
        data['通用名称'] = self.name
        data['功能主治'] = ' '.join(self.function())
        return data

    def fuzzy_search(self, search_text):
        cql = f"match(n:drug) where n.name=~'.*{search_text}.*' return n.name as name"
        drugs = []
        for drug in self.graph.run(cql).data():
            drugs.append(drug['name'])
        return drugs


if __name__ == '__main__':
    handler = Drug()
    handler.search("", "板蓝根颗粒")
    handler.disease()
    handler.form()
    handler.function()
    handler.usage()
    handler.component()
    handler.effects()
    handler.avoid()
    handler.matters()
    handler.drug_info('板蓝根颗粒')
