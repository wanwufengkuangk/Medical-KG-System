#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File     : xywy_analyze_info.py
# @Time     : 20-2-17 上午9:10
# @Author   : zkx
# @Email    : zkx9810@163.com
# @Site     : https://zkx98.github.io
# @Software : PyCharm
import os
import requests
import re
from bs4 import BeautifulSoup
import json


# 分析疾病页面
def analyze_disease_info(disease_id):
    response = requests.get(f'http://3g.jib.xywy.com/il_sii_{disease_id}.html', timeout=(3, 7))
    if response.status_code == 200:
        # 设置编码方式
        response.encoding = 'utf-8'
        # 创建Beautiful Soup对象
        soup = BeautifulSoup(response.text, 'html.parser')
        # 返回参数 疾病信息，常用药物链接，相关疾病症状链接，相关疾病链接
        disease_info = {}
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
                symptoms = re.split('\n', symptoms.text.strip('\n\r\t '))
                disease_info["相关症状"] = symptoms
                # 相关疾病
                relate_diseases = disease_xz[11].select('.fl')[1]
                relate_diseases = re.split('\n', relate_diseases.text.strip('\n\r\t '))
                disease_info["相关疾病"] = relate_diseases
            return disease_info
        except Exception as e:
            with open('error.txt', 'a') as f:
                f.write(f'analyze_disease_info:http://3g.jib.xywy.com/il_sii_{disease_id}.html\n{e}\n')
            return None
    else:
        return None


# 分析药物页面
def analyze_drug_info(drug_id):
    """
    分析药物页面信息
    :param drug_id:药物页面链接
    :return: 字典型药物信息
    """
    response = requests.get(f'http://3g.yao.xywy.com/goods/{drug_id}.htm', timeout=(3, 7))
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
                if data[0].select('h5')[0].text == h5[0]:
                    for data in data:
                        if len(h5) and data.select('h5')[0].text in h5:
                            h5.remove(data.select('h5')[0].text)
                            drug_info[data.select('h5')[0].text] = data.select('p')[0].text
                    # 返回字典型药物信息
                    return drug_info
                else:
                    return None
            else:
                return None
        except Exception as e:
            with open('error.txt', 'a') as f:
                f.write(f'analyze_drug_info:http://3g.yao.xywy.com/goods/{drug_id}.htm\n{e}')
            return None
    else:
        return None


# 分析症状页面
def analyze_symptom_info(symptom_id):
    response = requests.get(f'http://3g.jib.xywy.com/zzk_{symptom_id}.html', timeout=(3, 7))
    if response.status_code == 200:
        # 设置编码方式
        response.encoding = 'utf-8'
        # 创建Beautiful Soup对象
        soup = BeautifulSoup(response.text, 'html.parser')
        # 概述, 病因, 检查, 诊断, 预防, 可能患有的疾病, 常见症状
        symptom_info = {}
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
            symptom_info["可能患有的疾病"] = diseases
            # 常见症状
            r_symptoms = []
            for a in data[6].select('a'):
                r_symptoms.append(a.text.strip(' '))
            symptom_info["常见症状"] = r_symptoms
            return symptom_info
        except Exception as e:
            with open('error.txt', 'a') as f:
                f.write(f'analyze_symptom_info:http://3g.jib.xywy.com/zzk_{symptom_id}.html\n{e}')
            return None
    else:
        return None


# 简版，偷懒版：直接从 id0-id最大值 循环
if __name__ == '__main__':
    # files = ['info_diseases.json', 'info_drugs.json', 'info_symptoms.json']
    # for file in files:
    #     if os.path.exists(file):
    #         os.remove(file)
    # for i in range(1000, 10000):
    #     print(i)
    #     for j in range(3):
    #         try:
    #             if j == 0:
    #                 info = analyze_disease_info(i)
    #             elif j == 1:
    #                 info = analyze_drug_info(i)
    #             else:
    #                 info = analyze_symptom_info(i)
    #             if info is not None:
    #                 with open(f"{files[j]}", "a+") as f:
    #                     f.write(json.dumps(info) + '\n')
    #         except Exception as e:
    #             with open('error.txt', 'a') as f:
    #                 f.write(f'xywy_analyze_info_2:{j} id={i}\n')
    print(analyze_disease_info(169))

