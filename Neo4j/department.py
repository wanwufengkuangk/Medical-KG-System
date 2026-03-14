from py2neo import Graph
from Neo4j import disease
from Neo4j.config import neo4j as config_neo4j


class Department:
    def __init__(self):
        self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.search_type = ""
        self.name = ""
        self.alpha_order = True
        self.disease = disease.Disease()

    def search(self, search_type, department_name, alpha_order=False):
        self.search_type = search_type
        self.name = department_name
        self.alpha_order = alpha_order
        if search_type == "disease":
            return self.dept_disease()

    def dept_disease(self):
        if self.alpha_order:
            cql = f"match(p:department)-[]->(n:disease) where p.name='{self.name}' " \
                f"with n.name as disease order by disease return disease limit 25"
        else:
            cql = f"match(p:department)-[]->(n:disease) where p.name='{self.name}' " \
                f"return n.name as disease order by n.proportion desc limit 25"
        data = self.graph.run(cql).data()
        # print(data)
        return data

    def fuzzy_search(self, department_name, page=0, page_size=5, alpha_order=True):
        self.name = department_name
        self.alpha_order = alpha_order
        if department_name == '全部科室':
            cql = f"match(n:disease) return n.name as disease order by disease"
        elif self.alpha_order:
            cql = f"match(p:department)-[]->(n:disease) where p.name='{self.name}' " \
                f"with n.name as disease order by disease return disease"
        else:
            cql = f"match(p:department)-[]->(n:disease) where p.name='{self.name}' " \
                f"return n.name as disease order by n.proportion desc"
        diseases_name = self.graph.run(cql).data()
        data = []
        for disease_name in diseases_name[(page*page_size):min(((page+1)*page_size), len(diseases_name))]:
            print(disease_name['disease'])
            data.append(self.disease.disease_info_brief(disease_name['disease']))
        # print(data)
        return data


if __name__ == '__main__':
    handler = Department()
    handler.fuzzy_search("全部科室", 1, 5)
