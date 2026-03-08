#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File     : xywy_analyze_info.py
# @Time     : 20-2-17 上午9:10
# @Author   : zkx
# @Email    : zkx9810@163.com
# @Site     : https://zkx98.github.io
# @Software : PyCharm


import requests
import re
from bs4 import BeautifulSoup
import json


# 分析疾病页面
def analyze_disease_info(disease_id):
    response = requests.get(f'http://3g.jib.xywy.com/il_sii_{disease_id}.html')
    if response.status_code == 200:
        # 设置编码方式
        response.encoding = 'utf-8'
        # 创建Beautiful Soup对象
        soup = BeautifulSoup(response.text, 'html.parser')
        # 返回参数 疾病信息，常用药物链接，相关疾病症状链接，相关疾病链接
        disease_info = {}
        drugs_id = set()
        symptoms_id = set()
        diseases_id = set()
        try:
            # **************************************************疾病概述**************************************************
            # 疾病名称, 疾病类型, 疾病别名, 疾病简介
            disease_gs = soup.select('.Disease-box')[0]
            # 疾病名称
            disease_title = disease_gs.select('em')
            if len(disease_title) == 1:
                disease_info["疾病名称"] = disease_title[0].text
            # 疾病类型
            disease_type = disease_gs.select('span')
            if len(disease_type) == 1:
                disease_info["疾病类型"] = disease_type[0].text
            # 疾病别名
            disease_alias = disease_gs.select('.Disease-alias')
            if len(disease_alias) == 1:
                disease_alias = re.sub(r'别名：', '', disease_alias[0].text)
                disease_alias = re.split('，', disease_alias.strip('，'))
                disease_info["疾病别名"] = disease_alias
            # 疾病简介
            disease_brief = disease_gs.select('.Disease-brief')[0].select('p')
            if len(disease_brief) != 0:
                brief = []
                for p in disease_brief:
                    brief.append(p.text.lstrip('\r\n'))
                disease_brief = '\n'.join(brief)
                disease_info["疾病简介"] = disease_brief
                # **************************************************到院就诊须知**************************************************
                # 挂什么科, 需做检查, 治疗方法, 常用药物, 一般费用, 传染性, 治愈周期, 治愈率, 患病比例, 好发人群, 相关症状, 相关疾病
                disease_xz = soup.find_all(attrs={'class': 'clearfix'})[1:13]
                # 挂什么科
                department = disease_xz[0].select('.fl')[1]
                department = re.split('\u2003', department.text.strip('\u2003'))
                disease_info["挂什么科"] = department
                # 需做检查
                check = disease_xz[1].select('.fl')[1]
                check = re.split('  \xa0', check.text.strip('  \xa0'))
                disease_info["需做检查"] = check
                # 治疗方法
                method = disease_xz[2].select('.fl')[1]
                method = re.split('  \xa0', method.text.strip('  \xa0'))
                disease_info["治疗方法"] = method
                # 常用药物
                drug = disease_xz[3].select('.fl')[1]
                for drug_id in drug.select('a'):
                    drugs_id.update(re.findall(r'goods/(.+?).htm', drug_id['href']))
                drug = re.split('\n ', drug.text.strip('\n\r\t '))
                disease_info["常用药物"] = drug
                # 一般费用
                cost = disease_xz[4].select('.fl')[1]
                disease_info["一般费用"] = cost.text
                # 传染性
                infect = disease_xz[5].select('.fl')[1]
                infect = re.split('  ', infect.text.strip('  '))
                disease_info["传染性"] = infect
                # 治愈周期
                cure_period = disease_xz[6].select('.fl')[1]
                disease_info["治愈周期"] = cure_period.text.strip('\n\r\t ')
                # 治愈率
                cure_rate = disease_xz[7].select('.fl')[1]
                cure_rate = re.findall(r"\d+\.?\d*%", cure_rate.text)
                disease_info["治愈率"] = cure_rate
                # 患病比例
                proportion = disease_xz[8].select('.fl')[1]
                proportion = re.findall(r"\d+\.?\d*%", proportion.text)
                disease_info["患病比例"] = proportion
                # 好发人群
                population = disease_xz[9].select('.fl')[1]
                population = re.split(' ', population.text.strip(' '))
                disease_info["好发人群"] = population
                # 相关症状
                symptoms = disease_xz[10].select('.fl')[1]
                for symptom_id in symptoms.select('a'):
                    symptoms_id.update(re.findall(r'zzk_(.+?).html', symptom_id['href']))
                symptoms = re.split('\n', symptoms.text.strip('\n\r\t '))
                disease_info["相关症状"] = symptoms
                # 相关疾病
                relate_diseases = disease_xz[11].select('.fl')[1]
                for disease_id in relate_diseases.select('a'):
                    diseases_id.update(re.findall(r'il_sii_(.+?).html', disease_id['href']))
                relate_diseases = re.split('\n', relate_diseases.text.strip('\n\r\t '))
                disease_info["相关疾病"] = relate_diseases
            return [disease_info, drugs_id, symptoms_id, diseases_id]
        except Exception as e:
            print(f'analyze_disease_info:http://3g.jib.xywy.com/il_sii_{disease_id}.html\n{e}')
    else:
        return None
    return None


# 分析药物页面
def analyze_drug_info(drug_id):
    """
    分析药物页面信息
    :param drug_id:药物页面链接
    :return: 字典型药物信息
    """
    response = requests.get(f'http://3g.yao.xywy.com/goods/{drug_id}.htm')
    if response.status_code == 200:
        # 设置编码方式
        response.encoding = 'utf-8'
        # 创建Beautiful Soup对象
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            if len(soup.select('.search-box')) == 0:
                data = soup.select('.drugs-info-box')[0].select('li')
                h5 = ['通用名称', '功能主治', '用法用量', '剂型', '成份', '不良反应', '禁忌', '注意事项']
                drug_info = {}
                for info in data:
                    if len(h5) and info.select('h5')[0].text in h5:
                        h5.remove(info.select('h5')[0].text)
                        drug_info[info.select('h5')[0].text] = info.select('p')[0].text
                # 返回字典型药物信息
                return drug_info
            else:
                return None
        except Exception as e:
            print(f'analyze_drug_info:http://3g.yao.xywy.com/goods/{drug_id}.htm\n{e}')
            return None
    else:
        return None

# 分析症状页面
def analyze_symptom_info(symptom_id):
    response = requests.get(f'http://3g.jib.xywy.com/zzk_{symptom_id}.html')
    if response.status_code == 200:
        # 设置编码方式
        response.encoding = 'utf-8'
        # 创建Beautiful Soup对象
        soup = BeautifulSoup(response.text, 'html.parser')
        # 概述, 病因, 检查, 诊断, 预防, 可能患有的疾病, 常见症状
        symptom_info = {}
        diseases_id = set()
        symptoms_id = set()
        try:
            data = soup.select('.sec-box ')[:7]
            # 症状
            symptom_info["症状"] = data[0].select('em')[0].text.strip(' ')
            # 概述, 病因, 检查, 诊断, 预防
            h2 = ['概述', '病因', '检查', '诊断', '预防']
            for i in range(5):
                ps = data[i].select('p')
                if len(ps) != 0:
                    dic = []
                    for p in ps:
                        dic.append(p.text.strip('\r\n '))
                    p = '\n'.join(dic)
                    symptom_info[h2[i]] = p
            # 可能患有的疾病
            diseases = []
            for a in data[5].select('a'):
                diseases.append(a.select('p')[0].text.strip(' '))
                diseases_id.add(re.findall(r'il_sii_(.+?).html', a['href'])[0])
            symptom_info["可能患有的疾病"] = diseases
            # 常见症状
            r_symptoms = []
            for a in data[6].select('a'):
                r_symptoms.append(a.text.strip(' '))
                symptoms_id.add(re.findall(r'zzk_(.+?).html', a['href'])[0])
            symptom_info["常见症状"] = r_symptoms
            # # 病因
            # symptom_cause = data[1].select('p')
            # if len(symptom_cause) != 0:
            #     cause = []
            #     for p in symptom_cause:
            #         cause.append(p.text.strip('\r\n '))
            #     symptom_cause = '\n'.join(cause)
            #     symptom_info["病因"] = symptom_cause
            # # 检查
            # symptom_inspect = data[2].select('p')
            # if len(symptom_inspect) != 0:
            #     inspect = []
            #     for p in symptom_inspect:
            #         inspect.append(p.text.strip('\r\n '))
            #     symptom_inspect = '\n'.join(inspect)
            #     symptom_info["检查"] = symptom_inspect
            # # 诊断
            # symptom_diagnose = data[3].select('p')
            # if len(symptom_diagnose) != 0:
            #     diagnose = []
            #     for p in symptom_diagnose:
            #         diagnose.append(p.text.strip('\r\n '))
            #     symptom_diagnose = '\n'.join(diagnose)
            #     symptom_info["诊断"] = symptom_diagnose
            # # 预防
            # symptom_prevent = data[4].select('p')
            # if len(symptom_prevent) != 0:
            #     prevent = []
            #     for p in symptom_prevent:
            #         prevent.append(p.text.strip('\r\n '))
            #     symptom_prevent = '\n'.join(prevent)
            #     symptom_info["预防"] = symptom_prevent
            return [symptom_info, diseases_id, symptoms_id]
        except Exception as e:
            print(f'analyze_symptom_info:http://3g.jib.xywy.com/zzk_{symptom_id}.html\n{e}')
        return None
    else:
        return None


if __name__ == '__main__':
    # 获取疾病id
    with open('id_diseases.txt', 'r') as f:
        diseases_id = re.split('\n', f.read())
        print(diseases_id)
    # for line in open('diseases_info.txt', 'r'):
    #     print(type(json.loads(line)), json.loads(line))
    #     # print(type(line))
    #     print(json.loads(line)['疾病名称'])
    # diseases_id = [3135, 9748, 4891, 4764]
    for id in range(10000):
        info = analyze_disease_info(id)
        if info is not None:
            # 疾病信息
            print(info[0])
            with open("info_diseases.json", "a+") as f:
                f.write(json.dumps(info[0]) + '\n')
            # if write_disease_info(info[0]) is False:
            #     print(f'http://3g.jib.xywy.com/il_sii_{id}.html')
    # # 获取药品id
    # drugs_id = get_drugs_id()
    # with open("id_drugs.txt", "w") as f:
    #     f.write('\n'.join(drugs_id))
    # # 获取症状id
    # symptoms_id = get_symptoms_id()
    # with open("id_symptoms.txt", "w") as f:
    #     f.write('\n'.join(symptoms_id))
    #
    # diseases_finish = set()
    # drugs_finish = set()
    # symptoms_finish = set()
    # lens = [len(diseases_id), len(drugs_id), len(symptoms_id)]
    # while len(diseases_id) or len(drugs_id) or len(symptoms_id):
    #     # **************************************************疾病**************************************************
    #     # 疾病页面解析
    #     # diseases_id = [3135, 9748, 4891, 4764]
    #     if len(diseases_id) != 0:
    #         id = diseases_id.pop()
    #         diseases_finish.add(id)
    #         info = analyze_disease_info(id)
    #         if info is not None:
    #             # 疾病信息
    #             # print(info[0])
    #             if write_disease_info(info[0]) is False:
    #                 print(f'http://3g.jib.xywy.com/il_sii_{id}.html')
    #             # 药物链接
    #             for drug_id in info[1]:
    #                 # print(drug_id)
    #                 if drug_id not in drugs_finish:
    #                     drugs_id.add(drug_id)
    #             # 症状链接
    #             for symptom_id in info[2]:
    #                 # print(symptom_id)
    #                 if symptom_id not in symptoms_finish:
    #                     symptoms_id.add(symptom_id)
    #             # 疾病链接
    #             for disease_id in info[3]:
    #                 # print(disease_id)
    #                 if disease_id not in diseases_finish:
    #                     diseases_id.add(disease_id)
    #     # **************************************************药物**************************************************
    #     # 分析药物页面信息
    #     # drugs_id = [130194, 996, 59426, 666, 999]
    #     if len(drugs_id) != 0:
    #         id = drugs_id.pop()
    #         drugs_finish.add(id)
    #         info = analyze_drug_info(id)
    #         if info is not None:
    #             if write_drug_info(info) is False:
    #                 print(f'http://3g.yao.xywy.com/goods/{id}.htm')
    #         # else:
    #         #     print(id)
    #     # **************************************************症状**************************************************
    #     # 分析症状页面信息
    #     # symptoms_id = [6819, 4515, 5605, 4057]
    #     if len(symptoms_id) != 0:
    #         id = symptoms_id.pop()
    #         symptoms_finish.add(id)
    #         symptom_info = analyze_symptom_info(id)
    #         if symptom_info is not None:
    #             # 症状信息
    #             if write_symptom_info(symptom_info[0]) is False:
    #                 print(f'http://3g.jib.xywy.com/zzk_{id}.html')
    #             # 可能患病疾病链接
    #             for disease_id in symptom_info[1]:
    #                 # print(disease_id)
    #                 if disease_id not in diseases_finish:
    #                     diseases_id.add(disease_id)
    #             # 常见症状链接
    #             for symptom_id in symptom_info[2]:
    #                 # print(symptom_id)
    #                 if symptom_id not in symptoms_finish:
    #                     symptoms_id.add(symptom_id)
    # print('length of diseases:' + str(lens[0]) + len(diseases_finish))
    # print('length of drugs:' + str(lens[1]) + len(drugs_finish))
    # print('length of symptoms:' + str(lens[2]) + len(symptoms_finish))

