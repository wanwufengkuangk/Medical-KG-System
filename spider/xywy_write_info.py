#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File     : xywy_write_info.py
# @Time     : 20-2-17 上午9:10
# @Author   : zkx
# @Email    : zkx9810@163.com
# @Site     : https://zkx98.github.io
# @Software : PyCharm
from py2neo import Graph, Node, Relationship, NodeMatcher
import json
import re


# 将疾病信息写入数据库
def write_disease_info(disease_info):
    graph = Graph("bolt://localhost:7687", username="neo4j", password='1998')
    node_matcher = NodeMatcher(graph)
    try:
        # 疾病名称
        if disease_info.get('疾病名称') is not None:
            disease = node_matcher.match("disease").where(f"_.name = '{disease_info['疾病名称']}'").first()
            # 此疾病节点还未创建
            if disease is None:
                disease = Node('disease', name=disease_info['疾病名称'])
                graph.create(disease)
        # # 疾病类型
        # if disease_info.get('疾病类型') is not None:
        #     kind = node_matcher.match("kind").where(f"_.name = '{disease_info['疾病类型']}'").first()
        #     # 此类型节点还未创建
        #     if kind is None:
        #         kind = Node('kind', name=disease_info['疾病类型'])
        #     kind_disease = Relationship(kind, 'kind_disease', disease)
        #     graph.create(kind_disease)
        # # 疾病别名
        # if disease_info.get('疾病别名') is not None:
        #     # disease['alias'] = disease_info['疾病别名']
        #     # graph.push(disease)
        #     for bieming in disease_info['疾病别名']:
        #         alias = node_matcher.match("alias").where(f"_.name = '{bieming}'").first()
        #         # 此别名节点还未创建
        #         if alias is None:
        #             alias = Node('alias', name=bieming)
        #             graph.create(alias)
        #         disease_alias = Relationship(disease, 'disease_alias', alias)
        #         graph.create(disease_alias)
        # # 疾病简介
        # if disease_info.get('疾病简介') is not None:
        #     disease['brief'] = disease_info['疾病简介']
        #     graph.push(disease)
        # # 挂什么科
        # if disease_info.get('挂什么科') is not None:
        #     departments = []
        #     for keshi in disease_info['挂什么科']:
        #         department = node_matcher.match("department").where(f"_.name = '{keshi}'").first()
        #         if department is None:
        #             department = Node('department', name=keshi)
        #             graph.create(department)
        #         department_disease = Relationship(department, 'dept_contain_disease', disease)
        #         graph.create(department_disease)
        #         departments.append(department)
        #     for i in range(len(departments) - 1):
        #         keshi = disease_info['挂什么科'][i]
        #         department_department = Relationship(departments[i], 'dept_contain_dept', departments[i + 1])
        #         graph.create(department_department)
        # 需做检查
        # if disease_info.get('需做检查') is not None:
        #     # disease['check'] = disease_info['需做检查']
        #     # graph.push(disease)
        #     for jiancha in disease_info['需做检查']:
        #         check = node_matcher.match("check").where(f"_.name = '{jiancha}'").first()
        #         if check is None:
        #             check = Node('check', name=jiancha)
        #             graph.create(check)
        #         disease_check = Relationship(disease, 'disease_check', check)
        #         graph.create(disease_check)
        # # 治疗方法 disease_method
        # if disease_info.get('治疗方法') is not None:
        #     disease['method'] = disease_info['治疗方法']
        #     graph.push(disease)
        #     # for fangfa in disease_info['治疗方法']:
        #     #     method = node_matcher.match("method").where(f"_.name = '{fangfa}'").first()
        #     #     if method is None:
        #     #         method = Node('method', name=fangfa)
        #     #         graph.create(method)
        #     #     disease_method = Relationship(disease, 'disease_method', method)
        #     #     graph.create(disease_method)
        # # 常用药物 disease_drug
        # if disease_info.get('常用药物') is not None:
        #     for yaowu in disease_info['常用药物']:
        #         # 去药物名中的空格和制药公司
        #         name = yaowu.split(' ')
        #         if len(name) == 2:
        #             print(name)
        #             yaowu = name[1]
        #         # ####
        #         drug = node_matcher.match("drug").where(f"_.name = '{yaowu}'").first()
        #         if drug is None:
        #             drug = Node('drug', name=yaowu)
        #             graph.create(drug)
        #         disease_drug = Relationship(disease, 'disease_drug', drug)
        #         graph.create(disease_drug)
        # # 一般费用
        # if disease_info.get('一般费用') is not None:
        #     disease['fee'] = disease_info['一般费用']
        #     graph.push(disease)
        # # 传染性 disease_infect
        # if disease_info.get('传染性') is not None:
        #     disease['infect'] = disease_info['传染性']
        #     graph.push(disease)
        #     # for chuanran in disease_info['传染性']:
        #     #     infect = node_matcher.match("infect").where(f"_.name = '{chuanran}'").first()
        #     #     if infect is None:
        #     #         infect = Node('infect', name=chuanran)
        #     #         graph.create(infect)
        #     #     disease_infect = Relationship(disease, 'disease_infect', infect)
        #     #     graph.create(disease_infect)
        # # 治愈周期
        # if disease_info.get('治愈周期') is not None:
        #     disease['cure_period'] = disease_info['治愈周期']
        #     graph.push(disease)
        # # 治愈率
        # if disease_info.get('治愈率') is not None:
        #     disease['cure_rate'] = disease_info['治愈率']
        #     graph.push(disease)
        #     # for zhiyulv in disease_info['治愈率']:
        #     #     cure_rate = node_matcher.match("cure_rate").where(f"_.name = '{zhiyulv}'").first()
        #     #     if cure_rate is None:
        #     #         cure_rate = Node('cure_rate', name=zhiyulv)
        #     #     disease_cure_rate = Relationship(disease, 'disease_cure_rate', cure_rate)
        #     #     graph.create(disease_cure_rate)
        # # 患病比例 disease_proportion
        # if disease_info.get('患病比例') is not None:
        #     disease['proportion'] = disease_info['患病比例']
        #     graph.push(disease)
        #     # for bili in disease_info['治愈率']:
        #     #     proportion = node_matcher.match("proportion").where(f"_.name = '{bili}'").first()
        #     #     if proportion is None:
        #     #         proportion = Node('proportion', name=bili)
        #     #     disease_proportion = Relationship(disease, 'disease_proportion', proportion)
        #     #     graph.create(disease_proportion)
        # # 好发人群 susceptible_population
        # if disease_info.get('好发人群') is not None:
        #     disease['population'] = disease_info['好发人群']
        #     graph.push(disease)
        #     # for renqun in disease_info['好发人群']:
        #     #     population = node_matcher.match("population").where(f"_.name = '{renqun}'").first()
        #     #     if population is None:
        #     #         population = Node('population', name=renqun)
        #     #     disease_population = Relationship(disease, 'disease_population', population)
        #     #     graph.create(disease_population)
        # # 相关症状 relate_symptoms
        # if disease_info.get('相关症状') is not None:
        #     for zz in disease_info['相关症状']:
        #         symptom = node_matcher.match("symptom").where(f"_.name = '{zz}'").first()
        #         if symptom is None:
        #             symptom = Node('symptom', name=zz)
        #         disease_symptom = Relationship(disease, 'disease_symptom', symptom)
        #         graph.create(disease_symptom)
        # # 相关疾病
        # if disease_info.get('相关疾病') is not None:
        #     for jib in disease_info['相关疾病']:
        #         r_disease = node_matcher.match("disease").where(f"_.name = '{jib}'").first()
        #         if r_disease is None:
        #             r_disease = Node('disease', name=jib)
        #         disease_r_disease = Relationship(disease, 'disease_r_disease', r_disease)
        #         graph.create(disease_r_disease)
        return True
    except Exception as e:
        with open('error.txt', 'a') as f:
            f.write(f"write_disease_info:{disease_info['疾病名称']}\n{e}\n")
        return False
    return True


# 将药品信息写入数据库
def write_drug_info(drug_info):
    graph = Graph("bolt://localhost:7687", username="neo4j", password='1998')
    node_matcher = NodeMatcher(graph)
    try:
        # 通用名称
        if drug_info.get('通用名称') is not None:
            # 去药物名中的空格和制药公司 2020/4/9
            name = drug_info['通用名称'].split(' ')
            if len(name) == 2:
                print(name)
                drug_info['通用名称'] = name[1]
            # ####
            drug = node_matcher.match("drug").where(f"_.name = '{drug_info['通用名称']}'").first()
            # 此节点还未创建
            if drug is None:
                drug = Node('drug', name=drug_info['通用名称'])
                graph.create(drug)
        # 功能主治
        if drug_info.get('功能主治') is not None:
            drug['function'] = drug_info['功能主治']
            graph.push(drug)
        # 用法用量
        if drug_info.get('用法用量') is not None:
            drug['usage'] = drug_info['用法用量']
            graph.push(drug)
        # 剂型
        if drug_info.get('剂型') is not None:
            # 去除剂型后的()内容 2020/4/10
            name = re.sub(r"⑴", '', drug_info['剂型'])
            name = re.sub(r"\)⑵丸剂\(", ' ', name)
            name = re.sub(r"（", '(', name)
            name = re.sub(r"）", ')', name)
            name = re.sub(r"[ 、，,或/;]", ' ', name)
            if name.find('(') != -1:
                drug_info['剂型'] = name[:name.find('(')]
                form_ex = name[name.find('(')+1:name.find(')')]
                form_ex = ','.join(form_ex.split(' '))
                drug['form_ex'] = form_ex
                graph.push(drug)
            drug_info['剂型'] = drug_info['剂型'].strip()
            # ###
            form = node_matcher.match('form').where(f"_.name = '{drug_info['剂型']}'").first()
            if form is None:
                form = Node('form', name=drug_info['剂型'])
            form_drug = Relationship(form, 'form_drug', drug)
            graph.create(form_drug)
        # 成份
        if drug_info.get('成份') is not None:
            drug['component'] = drug_info['成份']
            graph.push(drug)
        # 不良反应
        if drug_info.get('不良反应') is not None:
            drug['effects'] = drug_info['不良反应']
            graph.push(drug)
        # 禁忌
        if drug_info.get('禁忌') is not None:
            drug['avoid'] = drug_info['禁忌']
            graph.push(drug)
        # 注意事项
        if drug_info.get('注意事项') is not None:
            drug['matters'] = drug_info['注意事项']
            graph.push(drug)
        return True
    except Exception as e:
        with open('error.txt', 'a', encoding='utf-8') as f:
            f.write(f'write_drug_info:{drug_info["通用名称"]}\n{e}\n')
        return False
    return True


# 将症状信息写入数据库
def write_symptom_info(symptom_info):
    graph = Graph("bolt://localhost:7687", username="neo4j", password='1998')
    node_matcher = NodeMatcher(graph)
    try:
        # 症状
        if symptom_info.get('症状') is not None:
            symptom = node_matcher.match("symptom").where(f"_.name = '{symptom_info['症状']}'").first()
            # 此节点还未创建
            if symptom is None:
                symptom = Node('symptom', name=symptom_info['症状'])
                graph.create(symptom)
        # 概述
        if symptom_info.get('概述') is not None:
            print(symptom_info['概述'])
            symptom['brief'] = symptom_info['概述']
            graph.push(symptom)
        # 病因
        if symptom_info.get('病因') is not None:
            symptom['cause'] = symptom_info['病因']
            graph.push(symptom)
        # 检查
        if symptom_info.get('检查') is not None:
            symptom['check'] = symptom_info['检查']
            graph.push(symptom)
        # 诊断
        if symptom_info.get('诊断') is not None:
            symptom['diagnose'] = symptom_info['诊断']
            graph.push(symptom)
        # 预防
        if symptom_info.get('预防') is not None:
            symptom['prevent'] = symptom_info['预防']
            graph.push(symptom)
        # 可能患有的疾病
        if symptom_info.get('可能患有的疾病') is not None:
            for jib in symptom_info['可能患有的疾病']:
                disease = node_matcher.match('disease').where(f"_.name = '{jib}'").first()
                if disease is None:
                    disease = Node('disease', name=jib)
                symptom_disease = Relationship(symptom, 'symptom_disease', disease)
                graph.create(symptom_disease)
        # 常见症状
        if symptom_info.get('常见症状') is not None:
            for zz in symptom_info['常见症状']:
                r_symptom = node_matcher.match('symptom').where(f"_.name = '{zz}'").first()
                if r_symptom is None:
                    r_symptom = Node('symptom', name=zz)
                symptom_r_symptom = Relationship(symptom, 'r_symptom', r_symptom)
                graph.create(symptom_r_symptom)
        return True
    except Exception as e:
        with open('error.txt', 'a') as f:
            f.write(f"write_symptom_info:{symptom_info['症状']}\n{e}\n")
        return False
    return True


if __name__ == '__main__':
    for line in open('info_diseases.json', 'r'):
        write_disease_info(json.loads(line))
    # for line in open('info_drugs.json', 'r'):
    #     write_drug_info(json.loads(line))
    # for line in open('info_symptoms.json', 'r'):
    #     write_symptom_info(json.loads(line))
    # data = \
    #     write_disease_info(data)
