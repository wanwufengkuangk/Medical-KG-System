import requests
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from py2neo import Graph, Node, Relationship, NodeMatcher
import json
import re


# 将疾病信息写入数据库
def write_info(disease_name, population_name):
    graph = Graph("bolt://localhost:7687", username="neo4j", password='1998')
    node_matcher = NodeMatcher(graph)
    try:
        # 疾病名称
        disease = node_matcher.match("disease").where(f"_.name = '{disease_name}'").first()
        # 此疾病节点还未创建
        if disease is None:
            disease = Node('disease', name=disease_name)
            graph.create(disease)
        # 好发人群 susceptible_population
        population = node_matcher.match("population").where(f"_.name = '{population_name}'").first()
        if population is None:
            population = Node('population', name=population_name)
        disease_population = Relationship(disease, 'disease_population', population)
        graph.create(disease_population)



    except Exception as e:
        print(f"{disease_name}, {population}, {e}")
        return False

# 获取疾病id
def population():
    """
    从寻医问药按首字母查询疾病页面获取爬取所有疾病链接
    :return: 一个包含所有疾病链接的集合
    """
    # 疾病请求地址
    url = "http://jib.api.xywy.com/GetJibInfo/getJibInfoByCrowdType"
    # 疾病请求参数 dict类型
    parameter = {
        "callback": "jsoncallback",
        "typeid": "",
        "page": "9",
        "pageSize": "100"
    }
    #
    population_list = ['', '男性', '女性', '老年', '儿童', '孕产']

    # 所有疾病的链接
    diseases_id = set()
    # 按首字母A-Z爬取疾病链接
    for typeid in range(4, 6):
        # 修改请求字母
        parameter["typeid"] = typeid
        #
        while True:
            print(f'get_diseases_id:{typeid},{parameter["page"]}')
            # 请求参数dict格式转url格式
            url_parameter = urlencode(parameter)
            # 获取链接返回的内容
            data = requests.get(url + "?" + url_parameter).text
            # print(type(data), data)
            # 查找疾病的id
            data = re.findall(r'name":"(.+?)",', data)
            # 获取疾病id个数不为0
            if len(data) != 0:
                for data in data:
                    data = re.sub(r'1\\/3', '', data)
                    # print(re.sub(r'1\\/3', '', data), population_list[typeid])
                    write_info(data, population_list[typeid])
                # 请求页数 + 1 继续循环进行下页请求
                parameter["page"] = int(parameter["page"]) + 1
            # 获取疾病id个数为0
            else:
                break
        # 重置请求页数
        parameter["page"] = 1
    # 返回疾病id集合
    return diseases_id


population()