# 组织答案
import re
from Neo4j import data_search
from Answer import disease, alias, symptom, drug, check, population


class Answer:
    def __init__(self):
        self.entity = None
        self.attr = None
        self.sub_entity = None
        self.answer = ''
        self.data = ""
        self.data_search = data_search.DataSearch()
        self.disease = disease.Disease()
        self.alias = alias.Alias()
        self.symptom = symptom.Symptom()
        self.drug = drug.Drug()
        self.check = check.Check()
        self.population = population.Population()
        return

    def generate(self, question_type, entity, attr, sub_entity=None):
        self.entity = entity
        self.attr = attr
        self.sub_entity = sub_entity
        self.answer = ''
        if question_type == 'ts':
            self.ts()
        elif question_type == 'tz':
            self.tz()
        elif question_type == 'xz':
            self.xz()
        elif question_type == 'zf':
            self.sf_or_zf()
        elif question_type == 'sf':
            self.sf_or_zf()
        else:
            return

    def ts(self):
        if self.attr is None:
            self.attr = 'cause'
            self.data = self.data_search.search(self.entity, self.attr)
            if self.data is None or self.data == '':
                self.attr = 'brief'
                self.data = self.data_search.search(self.entity, self.attr)
                self.answer = '\n'.join(self.data).rstrip()
            else:
                self.data = '\n'.join(self.data).rstrip()
                self.answer = f"{self.entity[0]}主要有以下原因\n{self.data}"
            # print(self.answer)
            # return self.answer
        else:
            return None

    def tz(self):
        # 疾病症状类
        if self.entity[1] in ["dis_sym", "ali_sym", "disease", "alias"]:
            # 无属性
            if self.attr is None:
                self.attr = "brief"
                data = self.data_search.search(self.entity, self.attr)
                # self.attr = "check"
                # data2 = self.data_search.search(self.entity, self.attr)
                # print(data, data2, sep='\n')
                self.answer = data
            # 单属性
            else:
                data = self.data_search.search(self.entity, self.attr)
                if self.data is None:
                    return
                elif self.attr == 'brief':
                    self.answer = data
                elif self.attr == 'department':
                    self.answer = f"{self.entity[0]}可以挂{'或'.join(data)}。"
                elif self.attr == 'check':
                    self.answer = f"{self.entity[0]}可以做{'，'.join(data)}等检查。"
                elif self.attr == 'method':
                    self.answer = f"{self.entity[0]}的治疗方法有{'，'.join(data)}。"
                elif self.attr == 'fee':
                    self.answer = f"{self.entity[0]}的一般费用为{data}。"
                elif self.attr == 'infect':
                    if data != '':
                        self.answer = f"{self.entity[0]}一般为{data}。"
                    else:
                        self.answer = f"{self.entity[0]}无传染性。"
                elif self.attr == 'cure_period':
                    self.answer = f"{self.entity[0]}的治疗周期一般为{data}。"
                elif self.attr == 'cure_rate':
                    self.answer = f"{self.entity[0]}的治愈率一般为{data}。"
                elif self.attr == 'proportion':
                    self.answer = f"{self.entity[0]}的患病比例一般为{data}。"
                elif self.attr == 'population':
                    if data != '':
                        self.answer = f"{self.entity[0]}好发人群为{data}。"
                    else:
                        self.answer = f"{self.entity[0]}无特殊人群。"
                elif self.attr == 'disease':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}的相关疾病有{','.join(data)}等。"
                elif self.attr == 'symptom':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}的相关症状有{','.join(data)}等。"
                elif self.attr == 'drug':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}的常用药物有{','.join(data)}等。"
                # elif self.attr == 'cause':
                # elif self.attr == 'diagnose':
                # elif self.attr == 'prevent':
                else:
                    self.answer = data
        # 症状类
        elif self.entity[1] == "symptom":
            # 无属性
            if self.attr is None:
                self.attr = "brief"
                data = self.data_search.search(self.entity, self.attr)
                # self.attr = "check"
                # data2 = self.data_search.search(self.entity, self.attr)
                # print(data, data2, sep='\n')
                self.answer = data
            # 单属性
            else:
                data = self.data_search.search(self.entity, self.attr)
                if self.data is None:
                    return
                elif self.attr == 'disease':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}的相关疾病有{','.join(data)}等。"
                elif self.attr == 'symptom':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}的相关症状有{','.join(data)}等。"
                # elif self.attr == 'brief':
                #     self.answer = data
                # elif self.attr == 'check':
                # elif self.attr == 'cause':
                # elif self.attr == 'diagnose':
                # elif self.attr == 'prevent':
                else:
                    self.answer = data
        # 药物类
        elif self.entity[1] in ["drug"]:
            # 无属性
            if self.attr is None:
                self.attr = "function"
                data = self.data_search.search(self.entity, self.attr)
                self.answer = data
            # 单属性
            else:
                data = self.data_search.search(self.entity, self.attr)
                if self.data is None:
                    return
                elif self.attr == 'disease':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}可治疾病有{','.join(data)}等。"
                else:
                    self.answer = data
        # 检查项目
        elif self.entity[1] == "check":
            # 无属性
            if self.attr is None:
                self.attr = "disease"
                data = self.data_search.search(self.entity, self.attr)
                if len(data) == 0:
                    self.answer = '暂无相关信息'
                else:
                    self.answer = f"{self.entity[0]}可以查出{','.join(data)}等疾病。"
            # 单属性
            else:
                data = self.data_search.search(self.entity, self.attr)
                if self.data is None:
                    return
                elif self.attr == 'disease':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}可以查出{','.join(data)}等疾病。"
                else:
                    self.answer = data
        # 人群类
        elif self.entity[1] == 'population':
            # 无属性
            if self.attr is None:
                self.attr = "disease"
                data = self.data_search.search(self.entity, self.attr)
                if len(data) == 0:
                    self.answer = '暂无相关信息'
                else:
                    self.answer = f"{self.entity[0]}容易得{','.join(data)}等疾病。"
            # 单属性
            else:
                data = self.data_search.search(self.entity, self.attr)
                if self.data is None:
                    return
                elif self.attr == 'disease':
                    if len(data) == 0:
                        self.answer = '暂无相关信息'
                    else:
                        self.answer = f"{self.entity[0]}容易得{','.join(data)}等疾病。"
                else:
                    self.answer = data
        return None

    def xz(self):
        data = self.data_search.search(self.entity, self.attr)
        if self.data is None:
            return
        # 疾病-实体
        else:
            # "dis_sym", "ali_sym", "disease", "alias", "symptom", "drug", "check",
            # 'population', 'department'
            sub_entity = []
            # 疾病-科室
            if self.attr == 'department':
                for word, pos in self.sub_entity:
                    if word in data:
                        sub_entity.append(word)
                if len(sub_entity) != 0:
                    self.answer = f"应该挂{'，'.join(sub_entity)}。"
                else:
                    self.answer = f"都不可以，{self.entity[0]}可以挂{'或'.join(data)}。"
            # 疾病-检查
            elif self.attr == 'check':
                for word, pos in self.sub_entity:
                    if word in data:
                        sub_entity.append(word)
                if len(sub_entity) != 0:
                    self.answer = f"可以做{'，'.join(sub_entity)}。"
                else:
                    self.answer = f"都不可以，{self.entity[0]}可以做{'，'.join(data)}等检查。"
            # 疾病-药物
            elif self.attr == 'drug':
                for word, pos in self.sub_entity:
                    if word in data:
                        sub_entity.append(word)
                if len(sub_entity) != 0:
                    self.answer = f"可以用{'，'.join(sub_entity)}。"
                else:
                    self.answer = f"{self.robot}不确定，但{self.entity[0]}可以做{'，'.join(data)}等药物，具体用药请咨询医师。"
            else:
                self.answer = data
        return

    def sf_or_zf(self):
        data = self.data_search.search(self.entity, self.attr)
        if self.data is None:
            return
        else:
            # 疾病-属性
            if self.sub_entity is None:
                # 'attr_disease', 'attr_department', 'attr_check', 'attr_method',
                # 'attr_infect', 'attr_proportion', 'attr_population', 'attr_fee',
                # 'attr_cure_period', 'attr_cure_rate', 'attr_cause', 'attr_prevent',
                # 'attr_symptom', 'attr_drug'
                # 疾病-治愈率
                if self.attr == 'cure_rate':
                    num = re.findall(r"\d+\.?\d*", data)
                    an = ''
                    if len(num) > 0:
                        if float(num[0]) > 60:
                            an = '有很大几率可以治愈'
                        elif float(num[0]) > 1:
                            an = '有几率可以治愈'
                        else:
                            an = '治愈可能性比较小'
                    self.answer = f"{self.entity[0]}的治愈率为{data}，{an}。"
                # 疾病-治愈周期
                elif self.attr == 'cure_period':
                    self.answer = data
                # 疾病-传染性
                elif self.attr == 'infect':
                    if self.data != '':
                        self.answer = f'会传染，传染性为{data}。'
                    else:
                        self.answer = '不会传染'
                # 疾病-患病比例
                elif self.attr == 'proportion':
                    num = re.findall(r"\d+\.?\d*", data)
                    an = ''
                    if len(num) > 0:
                        if float(num[0]) > 60:
                            an = '很容易得'
                        elif float(num[0]) > 1:
                            an = '容易得'
                        else:
                            an = '不容易'
                    self.answer = f"{an}，其患病比例为{data}。"
                elif self.attr == 'disease':
                    self.answer = f"{self.entity[0]}的并发症有{','.join(data)}"
                elif self.attr == 'symptom':
                    self.answer = f"{self.entity[0]}的症状有{','.join(data)}"
                else:
                    self.answer = data
            # 疾病-实体
            else:
                # "dis_sym", "ali_sym", "disease", "alias", "symptom", "drug", "check",
                # 'population', 'department'
                # 疾病-科室
                if self.attr == 'department':
                    if self.sub_entity[0][0] in data:
                        self.answer = f"是的，{self.entity[0]}可以挂{self.sub_entity[0][0]}。"
                    else:
                        self.answer = f"不是，{self.entity[0]}不可以挂{self.sub_entity[0][0]}，但可以挂{'或'.join(data)}。"
                # 疾病-检查
                elif self.attr == 'check':
                    if self.sub_entity[0][0] in data:
                        self.answer = f"是的，{self.entity[0]}可以做{self.sub_entity[0][0]}。"
                    else:
                        self.answer = f"不是，{self.entity[0]}不可以做{self.sub_entity[0][0]}，但可以做{'，'.join(data)}。"
                # 疾病-药物
                elif self.attr == 'drug':
                    if self.sub_entity[0][0] in data:
                        self.answer = f"是的，{self.entity[0]}可以用{self.sub_entity[0][0]}。"
                    else:
                        self.answer = f"不确定，但{self.entity[0]}可以做{'，'.join(data)}等药物，具体用药请咨询医师。"
                else:
                    self.answer = data
        return
