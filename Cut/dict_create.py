from py2neo import Graph, NodeMatcher
import os
from Neo4j.config import neo4j as config_neo4j


graph = Graph(config_neo4j['url'], username=config_neo4j['username'], password=config_neo4j['password'])
matcher = NodeMatcher(graph)

dict_dir = os.path.dirname(__file__) + '/dict/'
# 字典路径
dict_file_path = {'disease_symptom': dict_dir + 'dis_sym.txt',
                  'alias_symptom': dict_dir + 'ali_sym.txt',
                  'disease': dict_dir + 'disease.txt',
                  'alias': dict_dir + 'alias.txt',
                  'symptom': dict_dir + 'symptom.txt',
                  'drug': dict_dir + 'drug.txt',
                  'check': dict_dir + 'check.txt',
                  'population': dict_dir + 'population.txt',
                  'department': dict_dir + 'department.txt'}


# 创建disease_symptom和disease词典
def disease_dict():
    disease = matcher.match('disease')
    for disease in disease:
        if matcher.match('symptom').where(f"_.name='{disease['name']}'").first() is not None:
            with open(dict_file_path['disease_symptom'], 'a', encoding='utf-8') as f:
                print('disease_symptom', disease['name'])
                f.write(f"{disease['name']}\n")
        else:
            with open(dict_file_path['disease'], 'a', encoding='utf-8') as f:
                f.write(f"{disease['name']}\n")
                print('disease', disease['name'])


# 创建alias_symptom和alias词典
def alias_dict():
    alias = matcher.match('alias')
    for alias in alias:
        if matcher.match('symptom').where(f"_.name='{alias['name']}'").first() is not None:
            # print(alias['name'])
            with open(dict_file_path['alias_symptom'], 'a', encoding='utf-8') as f:
                f.write(f"{alias['name']}\n")
                print('alias_symptom', alias['name'])
        else:
            with open(dict_file_path['alias'], 'a', encoding='utf-8') as f:
                f.write(f"{alias['name']}\n")
                print('alias', alias['name'])


# 创建symptom词典
def symptom_dict():
    with open(dict_file_path['disease_symptom'], 'r', encoding='utf-8') as f:
        disease_symptom = f.read().strip().split('\n')
    with open(dict_file_path['alias_symptom'], 'r', encoding='utf-8') as f:
        alias_symptom = f.read().strip().split('\n')
    symptom = matcher.match('symptom')
    for symptom in symptom:
        if symptom not in disease_symptom and symptom not in alias_symptom:
            with open(dict_file_path['symptom'], 'a', encoding='utf-8') as f:
                f.write(f"{symptom['name']}\n")
                print('symptom', symptom['name'])


# 创建药物词典
def drug_dict():
    drug = matcher.match('drug')
    for drug in drug:
        with open(dict_file_path['drug'], 'a', encoding='utf-8') as f:
            f.write(f"{drug['name']}\n")
            print('drug', drug['name'])


# 创建检查项目词典
def check_dict():
    check = matcher.match('check')
    for check in check:
        with open(dict_file_path['check'], 'a', encoding='utf-8') as f:
            f.write(f"{check['name']}\n")
            print('check', check['name'])


# 创建人群词典
def population_dict():
    population = matcher.match('population')
    for population in population:
        with open(dict_file_path['population'], 'a', encoding='utf-8') as f:
            f.write(f"{population['name']}\n")
            print('population', population['name'])


# 创建科室词典
def department_dict():
    department = matcher.match('department')
    for department in department:
        with open(dict_file_path['department'], 'a', encoding='utf-8') as f:
            f.write(f"{department['name']}\n")
            print('department', department['name'])
