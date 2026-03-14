from py2neo import Graph, Node, NodeMatcher, RelationshipMatcher
from Neo4j import disease, alias, symptom, drug, check, population
from Neo4j.config import neo4j as config_neo4j


class DataSearch:
    def __init__(self):
        # 1  self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.graph = Graph(config_neo4j['url'], auth=(config_neo4j['username'], config_neo4j['password']))
        self.node_matcher = NodeMatcher(self.graph)
        self.rel_matcher = RelationshipMatcher(self.graph)
        self.disease = disease.Disease()
        self.alias = alias.Alias()
        self.symptom = symptom.Symptom()
        self.drug = drug.Drug()
        self.check = check.Check()
        self.population = population.Population()

    #
    def search(self, entity, attr_type):
        entity_name = entity[0]
        entity_type = entity[1]
        attr = attr_type
        if entity_type == "dis_sym":
            a = self.disease.search(attr, entity_name)
            if a is not None:
                return a
            else:
                b = self.symptom.search(attr, entity_name)
                return b
        elif entity_type == "ali_sym":
            a = self.alias.search(attr, entity_name)
            if a != "":
                return a
            else:
                b = self.symptom.search(attr, entity_name)
                return b
        elif entity_type == "disease":
            return self.disease.search(attr, entity_name)
        elif entity_type == "alias":
            return self.alias.search(attr, entity_name)
        elif entity_type == "symptom":
            return self.symptom.search(attr, entity_name)
        elif entity_type == "drug":
            return self.drug.search(attr, entity_name)
        elif entity_type == "check":
            return self.check.search(attr, entity_name)
        elif entity_type == "population":
            return self.population.search(attr, entity_name)


if __name__ == '__main__':
    handler = DataSearch()
