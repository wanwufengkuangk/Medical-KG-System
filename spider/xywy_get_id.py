#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File     : xywy_get_id.py
# @Time     : 20-2-17 上午9:10
# @Author   : zkx
# @Email    : zkx9810@163.com
# @Site     : https://zkx98.github.io
# @Software : PyCharm

import requests
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup


# 获取疾病id
def get_diseases_id():
    """
    从寻医问药按首字母查询疾病页面获取爬取所有疾病链接
    :return: 一个包含所有疾病链接的集合
    """
    # 疾病请求地址
    url = "http://jib.api.xywy.com/GetJibInfo/getJibInfoByLetter"
    # 疾病请求参数 dict类型
    parameter = {
        "callback": "jsoncallback",
        "letter": "",
        "page": "1",
        "pageSize": "50"
    }
    #
    letters = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
        'W', 'X', 'Y', 'Z']

    # 所有疾病的链接
    diseases_id = set()
    # 按首字母A-Z爬取疾病链接
    for letter in letters:
        # 修改请求字母
        parameter["letter"] = letter
        # 重置请求页数
        parameter["page"] = 1
        #
        while True:
            print(f'get_diseases_id:{letter},{parameter["page"]}')
            # 请求参数dict格式转url格式
            url_parameter = urlencode(parameter)
            # 获取链接返回的内容
            data = requests.get(url + "?" + url_parameter).text
            # 查找疾病的id
            data = re.findall(r'il_sii_(.+?).html', data)
            # 获取疾病id个数不为0
            if len(data) != 0:
                # 添加疾病id到集合中
                diseases_id.update(data)
                # 请求页数 + 1 继续循环进行下页请求
                parameter["page"] = int(parameter["page"]) + 1
            # 获取疾病id个数为0
            else:
                break
    # 返回疾病id集合
    return diseases_id


# 获取药物id
def get_drugs_id():
    # 药物分类链接
    category_url = 'http://3g.yao.xywy.com/ill_category.html'
    # 药物分类id
    categories_id = []
    # 所有药物链接
    drugs_id = set()
    response = requests.get(category_url, timeout=(3, 7))
    # 设置编码方式
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    # 提取药物所有分类
    ill_categories = soup.select('.clearfix')[0].select('li')
    # 提取药物分类id
    for ill_category in ill_categories:
        ill_category = ill_category.select('a')[0]['href']
        categories_id.append(re.findall(r'cate-(.+?).html', ill_category)[0])
    # 药物请求链接
    url = 'http://3g.yao.xywy.com/index.php'
    # 药物请求参数 dict类型
    parameter = {
        "s":"IllCategory/ajax_get_cate_info",
        "callback": "list",
        "cate_id": "",
        "page": "1"
    }
    i = 0
    for cate_id in categories_id:
        parameter["cate_id"] = cate_id
        parameter["page"] = 1
        # 防止死循环
        i += 1
        n = 100000
        while n:
            n -= 1
            print(f'get_drugs_id:{i} {parameter["page"]}')
            # 请求参数dict格式转url格式
            url_parameter = urlencode(parameter)
            # 获取链接返回的内容
            data = requests.get(url + "?" + url_parameter).text
            data = re.findall(r'"id":"(.+?)",', data)
            # 获取药物id个数不为0
            if len(data) != 0:
                print(data)
                # with open("id_drugs.txt", "a") as f:
                #     f.write('\n'.join(data) + '\n')
                drugs_id.update(data)
                parameter["page"] = int(parameter["page"]) + 1
            # 获取疾病网址个数为0
            else:
                break
    return drugs_id


# 获取症状id
def get_symptoms_id():
    letters = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
        'w', 'x', 'y', 'z']
    # 所有疾病的id
    symptoms_id = set()
    # 按首字母a-z爬取疾病id
    for letter in letters:
        print(f'get_symptoms_id:{letter}')
        # 疾病请求地址
        url = f"http://zzk.xywy.com/p/{letter}.html"
        # 获取链接返回的内容
        response = requests.get(url, timeout=(3, 7))
        # 设置编码方式
        response.encoding = 'gb2312'
        # 创建Beautiful Soup对象
        soup = BeautifulSoup(response.text, 'html.parser')
        for data in soup.select('.ks-ill-txt'):
            for da in data.select('a'):
                # 获取症状id
                ids = re.findall(r'/(.+?)_', da['href'])[0]
                print(ids)
                symptoms_id.add(ids)
    return symptoms_id


if __name__ == '__main__':
    # 获取疾病id
    with open("id_diseases.txt", "w") as f:
        f.write('\n'.join(get_diseases_id()))
    # 获取药品id
    with open("id_drugs.txt", "w") as f:
        f.write('\n'.join(get_drugs_id()))
    # 获取症状id
    with open("id_symptoms.txt", "w") as f:
        f.write('\n'.join(get_symptoms_id()))
