import os
import requests
import re
from bs4 import BeautifulSoup
import json


# 分析疾病页面
def analyze_disease_info(disease_id):
    response = requests.get(f'http://3g.jib.xywy.com/il_sii_{disease_id}.html', timeout=(3, 10))
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
            # print(disease_gs)
            # 疾病名称
            disease_title = disease_gs.select('em')
            if len(disease_title) == 1:
                disease_info["疾病名称"] = disease_title[0].text
            # print(soup.select('.analysis-nei'))
            cause = soup.find_all(id='disease-by')
            prevent = soup.find_all(id='disease-yuf')

            print(cause.txt, prevent.txt)
        except Exception as e:
            print(f"{e}")
            return None



if __name__ == '__main__':
    for i in range(1000):
        print(i)
        analyze_disease_info(i)
