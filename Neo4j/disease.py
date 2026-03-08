from py2neo import Graph, NodeMatcher, RelationshipMatcher
from Neo4j.config import neo4j as config_neo4j


class Disease:
    def __init__(self):
        self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.search_type = ""
        self.name = ""

    def search(self, search_type, disease_name):
        self.search_type = search_type
        self.name = disease_name
        if search_type == "kind":
            return self.kind()
        elif search_type == "alias":
            return self.alias()
        elif search_type == "brief":
            return self.brief()
        elif search_type == "department":
            return self.department()
        elif search_type == "check":
            return self.check()
        elif search_type == "method":
            return self.method()
        elif search_type == "drug":
            return self.drug()
        elif search_type == "fee":
            return self.fee()
        elif search_type == "infect":
            return self.infect()
        elif search_type == "cure_period":
            return self.cure_period()
        elif search_type == "cure_rate":
            return self.cure_rate()
        elif search_type == "proportion":
            return self.proportion()
        elif search_type == "population":
            return self.population()
        elif search_type == "symptom":
            return self.symptom()
        elif search_type == "disease":
            return self.disease()
        else:
            return None

    # 关系
    def alias(self):
        """
        查询疾病的别名
        :return: 别名列表
        """
        cql = f"match(p:disease)-[]->(n:alias) where p.name='{self.name}' " \
            f"return n.name as alias"
        data = []
        for alias in self.graph.run(cql).data():
            data.append(alias['alias'])
        # print(data)
        return data

    def kind(self):
        """
        查询疾病的类型
        :return: 类型字符串
        """
        cql = f"match(n:kind)-[]->(p:disease) where p.name='{self.name}' return n.name as kind"
        data = []
        for kind in self.graph.run(cql).data():
            data.append(kind['kind'])
        data = ' '.join(data)
        # print(data)
        return data

    def department(self):
        """
        查询疾病所在科室
        :return: 科室列表
        """
        cql = f"match(n:department)-[]->(p:disease) where p.name='{self.name}' return n.name as department"
        data = []
        for department in self.graph.run(cql).data():
            data.append(department['department'])
        if len(data) == 2:
            cql = f"match(n:department)-[r]->(p:department)" \
                f"where n.name='{data[0]}' and p.name='{data[1]}' return r"
            if len(self.graph.run(cql).data()) == 0:
                dept = data[0]
                data[0] = data[1]
                data[1] = dept
        # print(data)
        return data

    def disease(self):
        """
        查询疾病的并发症
        :return: 并发症列表
        """
        cql = f"match(p:disease)-[]->(n:disease) where p.name='{self.name}' " \
            f"return n.name as disease order by n.proportion desc"
        data = []
        for disease in self.graph.run(cql).data():
            data.append(disease['disease'])
        # print(data)
        return data

    def symptom(self):
        """
        查询疾病相关症状
        :return: 症状列表
        """
        cql = f"match(p:disease)-[]->(n:symptom) where p.name='{self.name}' return n.name as symptom"
        data = []
        for symptom in self.graph.run(cql).data():
            data.append(symptom['symptom'])
        # print(data)
        return data

    def drug(self):
        """
        查询疾病常用药物
        :return: 药物列表
        """
        cql = f"match(p:disease)-[]->(n:drug) where p.name='{self.name}' return n.name as drug"
        data = []
        for drug in self.graph.run(cql).data():
            data.append(drug['drug'])
        # print(data)
        return data

    # 属性
    def brief(self):
        """
        查询疾病简介
        :return: 以每段为一元素的简介列表
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.brief as brief"
        data = self.graph.run(cql).data()[0]['brief']
        if data is not None:
            data = data.split('\n')
            # print(data)
            return data
        else:
            return []

    def check(self):
        """
        查询疾病需做检查
        :return: 检查项目列表
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.check as check"
        data = self.graph.run(cql).data()[0]['check']
        if data is None:
            return []
        return data

    def method(self):
        """
        查询疾病所需治疗方法
        :return: 治疗方法列表
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.method as method"
        data = self.graph.run(cql).data()[0]['method']
        if data is None:
            return ''
        return data

    def fee(self):
        """
        查询疾病所需一般费用
        :return: 所需费用字符串
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.fee as fee"
        data = self.graph.run(cql).data()[0]['fee']
        if data is None:
            return ''
        return data

    def infect(self):
        """
        查询疾病的传染性
        :return:传染性 列表
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.infect as infect"
        data = self.graph.run(cql).data()[0]['infect']
        if data is None:
            return []
        data = ' '.join(data)
        return data

    def cure_period(self):
        """
        查询疾病的治愈周期
        :return: 治愈周期 字符串
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.cure_period as cure_period"
        data = self.graph.run(cql).data()[0]['cure_period']
        if data is None:
            return ''
        return data

    def cure_rate(self):
        """
        查询疾病的治愈率
        :return: 治愈率 字符串
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.cure_rate as cure_rate"
        data = self.graph.run(cql).data()[0]['cure_rate']
        if data is None:
            return ''
        data = '-'.join(data)
        return data

    def proportion(self):
        """
        查询疾病患病比例
        :return: 患病比例字符串
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.proportion as proportion"
        data = self.graph.run(cql).data()[0]['proportion']
        # if len(data) == 1 and data[0]['proportion'] is not None and len(data[0]['proportion']) == 2:
        #     print('2')
        if data is None:
            return ''
        data = '-'.join(data)
        return data

    def population(self):
        """
        查询疾病的好发人群
        :return: 好发人群 列表
        """
        cql = f"match(n:disease) where n.name='{self.name}' return n.population as population"
        data = self.graph.run(cql).data()[0]['population']
        if data is None:
            return ''
        data = '，'.join(data)
        return data

    # 页面

    def disease_info(self, disease_name):
        self.name = disease_name
        if self.node_matcher.match("disease").where(f"_.name = '{self.name}'").first() is None:
            return None
        data = dict()
        data['disease'] = self.name
        data['kind'] = ' '.join(self.kind())
        data['alias'] = ' '.join(self.alias())
        data['brief'] = self.brief()
        data['department'] = ' '.join(self.department())
        data['check'] = ' '.join(self.check())
        data['method'] = ' '.join(self.method())
        data['drug'] = self.drug()
        data['fee'] = self.fee()
        data['infect'] = ' '.join(self.infect())
        data['cure_period'] = self.cure_period()
        data['cure_rate'] = self.cure_rate()
        data['proportion'] = self.proportion()
        data['population'] = ' '.join(self.population())
        data['r_symptom'] = self.symptom()
        data['r_disease'] = self.disease()
        print(data)
        return data

    def disease_info_brief(self, disease_name):
        # data = {
        #     "疾病": f"{self.name}",
        #     "科室": "",
        #     "简介": "",
        #     "症状": ""
        # }
        self.name = disease_name
        data = dict()
        data['疾病'] = self.name
        data["科室"] = ' '.join(self.department())
        data['简介'] = ' '.join(self.brief())
        data['症状'] = '、'.join(self.symptom())
        return data

    def fuzzy_search(self, search_text):
        if search_text == '':
            cql = f"match(p:kind)-[]->(n:disease) where p.name='常见病' return n.name as name"
        else:
            cql = f"match(n:disease) where n.name=~'.*{search_text}.*' return n.name as name"
        diseases = []
        for disease in self.graph.run(cql).data():
            diseases.append(disease['name'])
        return diseases


if __name__ == '__main__':
    handler = Disease()
    # handler.search("", "癌症")
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

    handler.disease_info('感冒')
    handler.disease_info_brief('感冒')
    handler.fuzzy_search('感冒')
