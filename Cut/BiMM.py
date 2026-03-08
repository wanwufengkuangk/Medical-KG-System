import sys
import os
import re

# 疾病，症状，药物字典
dict_dis_sym = []
dict_ali_sym = []
dict_disease = []
dict_alias = []
dict_symptom = []
dict_drug = []
dict_check = []
dict_department = []
dict_population = []
# 特指，特殊，选择，是非，正反问句字典
key_ts = []
key_tz = []
key_xz = []
key_sf = []
key_zf = []
# 属性
attr_disease = []
attr_department = []
attr_check = []
attr_method = []
attr_infect = []
attr_proportion = []
attr_population = []
attr_fee = []
attr_cure_period = []
attr_cure_rate = []
attr_cause = []
attr_prevent = []
attr_symptom = []
attr_drug = []
attr_form = []
attr_function = []
attr_usage = []
attr_component = []
attr_effects = []
attr_avoid = []
attr_matters = []
# 词典中最长的词的长度
max_length = 0

dict_dir = os.path.dirname(__file__) + '/dict/'
key_dir = os.path.dirname(__file__) + '/key/'
attr_dir = os.path.dirname(__file__) + '/attr/'
# 字典路径
dict_file_path = {'dis_sym': dict_dir + 'dis_sym.txt',
                  'ali_sym': dict_dir + 'ali_sym.txt',
                  'disease': dict_dir + 'disease.txt',
                  'alias': dict_dir + 'alias.txt',
                  'symptom': dict_dir + 'symptom.txt',
                  'drug': dict_dir + 'drug.txt',
                  'check': dict_dir + 'check.txt',
                  'department': dict_dir + 'department.txt',
                  'population': dict_dir + 'population.txt'}
# 问句关键字路径
key_file_path = {'ts': key_dir + 'ts.txt',
                  'tz': key_dir + 'tz.txt',
                  'xz': key_dir + 'xz.txt',
                  'sf': key_dir + 'sf.txt',
                  'zf': key_dir + 'zf.txt'}
# 属性路径
attr_file_path = {'disease': attr_dir + 'disease.txt',
                  'department': attr_dir + 'department.txt',
                  'check': attr_dir + 'check.txt',
                  'method': attr_dir + 'method.txt',
                  'infect': attr_dir + 'infect.txt',
                  'proportion': attr_dir + 'proportion.txt',
                  'population': attr_dir + 'population.txt',
                  'fee': attr_dir + 'fee.txt',
                  'cure_period': attr_dir + 'cure_period.txt',
                  'cure_rate': attr_dir + 'cure_rate.txt',
                  'cause': attr_dir + 'cause.txt',
                  'prevent': attr_dir + 'prevent.txt',
                  'symptom': attr_dir + 'symptom.txt',
                  'drug': attr_dir + 'drug.txt',
                  'form': attr_dir + 'form.txt',
                  'function': attr_dir + 'function.txt',
                  'usage': attr_dir + 'usage.txt',
                  'component': attr_dir + 'component.txt',
                  'effects': attr_dir + 'effects.txt',
                  'avoid': attr_dir + 'avoid.txt',
                  'matters': attr_dir + 'matters.txt'}


def init():
    # 词典中最长的词的长度
    global max_length
    # 实体
    with open(dict_file_path['dis_sym'], 'r', encoding='utf-8') as f:
        dict_dis_sym.extend(f.read().strip().split('\n'))
    with open(dict_file_path['ali_sym'], 'r', encoding='utf-8') as f:
        dict_ali_sym.extend(f.read().strip().split('\n'))
    with open(dict_file_path['disease'], 'r', encoding='utf-8') as f:
        dict_disease.extend(f.read().strip().split('\n'))
    with open(dict_file_path['alias'], 'r', encoding='utf-8') as f:
        dict_alias.extend(f.read().strip().split('\n'))
    with open(dict_file_path['symptom'], 'r', encoding='utf-8') as f:
        dict_symptom.extend(f.read().strip().split('\n'))
    with open(dict_file_path['drug'], 'r', encoding='utf-8') as f:
        dict_drug.extend(f.read().strip().split('\n'))
    with open(dict_file_path['check'], 'r', encoding='utf-8') as f:
        dict_check.extend(f.read().strip().split('\n'))
    with open(dict_file_path['department'], 'r', encoding='utf-8') as f:
        dict_department.extend(f.read().strip().split('\n'))
    with open(dict_file_path['population'], 'r', encoding='utf-8') as f:
        dict_population.extend(f.read().strip().split('\n'))
    # 问句关键词
    # key_ts.extend(['为什么'])
    # key_tz.extend(['谁', '什么', '哪', '哪儿', '哪里', '几', '多少', '多', '多么', '怎么', '怎样', '怎么样', '什么', '怎样', '什么样', '哪些', '啥',
    #                '有哪些', '怎么办'])
    # key_xz.extend(['还是'])
    # key_sf.extend(['能', '可以', '会', '有', '是', '长', '挂', '用', '做', '容易'])
    # key_zf.extend(['能不能', '可不可以', '会不会', '有没有', '是不是', '长不长', '挂不挂', '用不用', '做不做', '容易不容易'])
    with open(key_file_path['ts'], 'r', encoding='utf-8') as f:
        key_ts.extend(f.read().strip().split('\n'))
    with open(key_file_path['tz'], 'r', encoding='utf-8') as f:
        key_tz.extend(f.read().strip().split('\n'))
    with open(key_file_path['xz'], 'r', encoding='utf-8') as f:
        key_xz.extend(f.read().strip().split('\n'))
    with open(key_file_path['sf'], 'r', encoding='utf-8') as f:
        key_sf.extend(f.read().strip().split('\n'))
    with open(key_file_path['zf'], 'r', encoding='utf-8') as f:
        key_zf.extend(f.read().strip().split('\n'))
    # 属性
    # attr_disease.extend(['病', '疾病', '并发症',
    #                      '查出'])
    # attr_department.extend(['科', '科室', '部门', '门诊部门',
    #                         '挂'])
    # attr_check.extend(['检查', '检查项目', '查',
    #                    '查出来'])
    # attr_method.extend(['治疗', '方法', '治疗方法', ''])
    # attr_infect.extend(['传染', '传染性', '传染率'])
    # attr_proportion.extend(['患病率', '患病比例', '得'])
    # attr_population.extend(['人', '人群', '好发人群'])
    # attr_fee.extend(['费用', '钱', '花费'])
    # attr_cure_period.extend(['时间', '天', '年', '久', '周期', '时间', '长', '治愈时间', '治愈周期', '治好时间', '治好周期'])
    # attr_cure_rate.extend(['治愈率', '治好', '治愈', '好'])
    # attr_cause.extend(['病因', ''])
    # attr_prevent.extend(['预防', '预防方法', '', '', '', '', '', '', '', ''])
    # attr_symptom.extend(['症状', '表征', '表现', '症候', '', '', '', '', '', ''])
    # attr_drug.extend(['药', '药物', '药品', '', '', '', '', '', '', ''])
    # attr_form.extend(['剂型', '类型', '', '', '', '', '', '', '', ''])
    # attr_function.extend(['作用', '功能主治', '治', '功能', '', '', '', '', '', ''])
    # attr_usage.extend(['用法用量', '服用', '使用', '', '', '', '', '', '', ''])
    # attr_component.extend(['成份', '', '', '', ''])
    # attr_effects.extend(['不良反应', '', '', '', '', '', '', '', '', ''])
    # attr_avoid.extend(['禁忌', '', '', '', '', '', '', '', '', ''])
    # attr_matters.extend(['注意事项', '注意', '', '', '', '', '', '', '', ''])
    with open(attr_file_path['disease'], 'r', encoding='utf-8') as f:
        attr_disease.extend(f.read().strip().split('\n'))
    with open(attr_file_path['department'], 'r', encoding='utf-8') as f:
        attr_department.extend(f.read().strip().split('\n'))
    with open(attr_file_path['check'], 'r', encoding='utf-8') as f:
        attr_check.extend(f.read().strip().split('\n'))
    with open(attr_file_path['method'], 'r', encoding='utf-8') as f:
        attr_method.extend(f.read().strip().split('\n'))
    with open(attr_file_path['infect'], 'r', encoding='utf-8') as f:
        attr_infect.extend(f.read().strip().split('\n'))
    with open(attr_file_path['proportion'], 'r', encoding='utf-8') as f:
        attr_proportion.extend(f.read().strip().split('\n'))
    with open(attr_file_path['population'], 'r', encoding='utf-8') as f:
        attr_population.extend(f.read().strip().split('\n'))
    with open(attr_file_path['fee'], 'r', encoding='utf-8') as f:
        attr_fee.extend(f.read().strip().split('\n'))
    with open(attr_file_path['cure_period'], 'r', encoding='utf-8') as f:
        attr_cure_period.extend(f.read().strip().split('\n'))
    with open(attr_file_path['cure_rate'], 'r', encoding='utf-8') as f:
        attr_cure_rate.extend(f.read().strip().split('\n'))
    with open(attr_file_path['cause'], 'r', encoding='utf-8') as f:
        attr_cause.extend(f.read().strip().split('\n'))
    with open(attr_file_path['prevent'], 'r', encoding='utf-8') as f:
        attr_prevent.extend(f.read().strip().split('\n'))
    with open(attr_file_path['symptom'], 'r', encoding='utf-8') as f:
        attr_symptom.extend(f.read().strip().split('\n'))
    with open(attr_file_path['drug'], 'r', encoding='utf-8') as f:
        attr_drug.extend(f.read().strip().split('\n'))
    with open(attr_file_path['form'], 'r', encoding='utf-8') as f:
        attr_form.extend(f.read().strip().split('\n'))
    with open(attr_file_path['function'], 'r', encoding='utf-8') as f:
        attr_function.extend(f.read().strip().split('\n'))
    with open(attr_file_path['usage'], 'r', encoding='utf-8') as f:
        attr_usage.extend(f.read().strip().split('\n'))
    with open(attr_file_path['component'], 'r', encoding='utf-8') as f:
        attr_component.extend(f.read().strip().split('\n'))
    with open(attr_file_path['effects'], 'r', encoding='utf-8') as f:
        attr_effects.extend(f.read().strip().split('\n'))
    with open(attr_file_path['avoid'], 'r', encoding='utf-8') as f:
        attr_avoid.extend(f.read().strip().split('\n'))
    with open(attr_file_path['matters'], 'r', encoding='utf-8') as f:
        attr_matters.extend(f.read().strip().split('\n'))
    # 词典中最长的词的长度
    max_length = max(max(len(word) for word in dict_dis_sym),
                     max(len(word) for word in dict_ali_sym),
                     max(len(word) for word in dict_disease),
                     max(len(word) for word in dict_symptom),
                     max(len(word) for word in dict_drug),
                     max(len(word) for word in dict_check))
    # max(len(word) for word in dict_alias),


def is_in_dict(word_list, word):
    """
    词是非在词典中
    :param word_list: 词列表
    :param word:
    :return: word在词典中则返回true
    """
    # 实体
    if word in dict_dis_sym:
        word_list.append((word, "dis_sym"))
        return True
    elif word in dict_ali_sym:
        word_list.append((word, "alis_sym"))
        return True
    elif word in dict_disease:
        word_list.append((word, "disease"))
        return True
    elif word in dict_alias:
        word_list.append((word, "alias"))
        return True
    elif word in dict_symptom:
        word_list.append((word, "symptom"))
        return True
    elif word in dict_drug:
        word_list.append((word, "drug"))
        return True
    elif word in dict_check:
        word_list.append((word, "check"))
        return True
    elif word in dict_department:
        word_list.append((word, "department"))
        return True
    elif word in dict_population:
        word_list.append((word, "population"))
        return True
    # 问句关键词
    elif word in key_ts:
        word_list.append((word, "key_ts"))
        return True
    elif word in key_tz:
        word_list.append((word, "key_tz"))
        return True
    elif word in key_xz:
        word_list.append((word, "key_xz"))
        return True
    elif word in key_sf:
        word_list.append((word, "key_sf"))
        return True
    elif word in key_zf:
        word_list.append((word, "key_zf"))
        return True
    # 属性
    # attr_disease attr_department attr_check attr_method attr_infect attr_proportion attr_population
    elif word in attr_disease:
        word_list.append((word, "attr_disease"))
        return True
    elif word in attr_department:
        word_list.append((word, "attr_department"))
        return True
    elif word in attr_check:
        word_list.append((word, "attr_check"))
        return True
    elif word in attr_method:
        word_list.append((word, "attr_method"))
        return True
    elif word in attr_infect:
        word_list.append((word, "attr_infect"))
        return True
    elif word in attr_proportion:
        word_list.append((word, "attr_proportion"))
        return True
    elif word in attr_population:
        word_list.append((word, "attr_population"))
        return True
    # attr_fee attr_cure_period attr_cure_rate attr_cause attr_prevent attr_symptom attr_drug
    elif word in attr_fee:
        word_list.append((word, "attr_fee"))
        return True
    elif word in attr_cure_period:
        word_list.append((word, "attr_cure_period"))
        return True
    elif word in attr_cure_rate:
        word_list.append((word, "attr_cure_rate"))
        return True
    elif word in attr_cause:
        word_list.append((word, "attr_cause"))
        return True
    elif word in attr_prevent:
        word_list.append((word, "attr_prevent"))
        return True
    elif word in attr_symptom:
        word_list.append((word, "attr_symptom"))
        return True
    elif word in attr_drug:
        word_list.append((word, "attr_drug"))
        return True
    # attr_form attr_function attr_usage attr_component attr_effects attr_avoid attr_matters
    elif word in attr_form:
        word_list.append((word, "attr_form"))
        return True
    elif word in attr_function:
        word_list.append((word, "attr_function"))
        return True
    elif word in attr_usage:
        word_list.append((word, "attr_usage"))
        return True
    elif word in attr_component:
        word_list.append((word, "attr_component"))
        return True
    elif word in attr_effects:
        word_list.append((word, "attr_effects"))
        return True
    elif word in attr_component:
        word_list.append((word, "attr_component"))
        return True
    elif word in attr_avoid:
        word_list.append((word, "attr_avoid"))
        return True
    elif word in attr_matters:
        word_list.append((word, "attr_matters"))
        return True
    elif len(word) == 1:  # 剩一个字时
        word_list.append((word, "x"))
        return True
    else:
        return False


# 正向最大匹配算法
def fmm_cut_words(sentence):
    """
    正向最大匹配算法
    :param sentence: 需要切的句子
    :return: 切好的词列表 列表元素为元组(词，词性)
    """
    global max_length
    sentence = sentence.strip()
    # 统计序列长度
    words_length = len(sentence)
    # 存储切分好的词语
    cut_word_list = []
    while words_length > 0:
        max_cut_length = min(max_length, words_length)
        sub_sentence = sentence[0: max_cut_length]
        while max_cut_length > 0:
            if is_in_dict(cut_word_list, sub_sentence):
                break
            else:
                max_cut_length -= 1
                sub_sentence = sub_sentence[0: max_cut_length]
        sentence = sentence[max_cut_length:]
        words_length = words_length - max_cut_length
    # words = "/".join(cut_word_list)
    return cut_word_list


# 逆向最大匹配算法
def bmm_cut_words(sentence):
    """
    逆向最大匹配算法
    :param sentence: 需要切的句子
    :return: 切好的词列表 列表元素为元组(词，词性)
    """
    global max_length
    sub_sentence = sentence.strip()  # 去除句子两边的空格换行等
    sub_sentence_length = len(sub_sentence)
    cut_word_list = []  # 存储切分好的词
    # 句子循环
    while sub_sentence_length > 0:
        # 当前句子所能切出的最长的词 及句子和词典长度最小值
        sub_word_length = min(max_length, sub_sentence_length)
        sub_word = sub_sentence[-sub_word_length:]
        # 词循环
        while sub_word_length > 0:
            if is_in_dict(cut_word_list, sub_word):
                break
            else:  # 去除最左边的字
                sub_word_length -= 1
                sub_word = sub_word[-sub_word_length:]
        # 切除右边分出的词
        sub_sentence_length = sub_sentence_length - sub_word_length
        sub_sentence = sub_sentence[:sub_sentence_length]
    cut_word_list.reverse()  # 反转一下切出的词的顺序
    # cut_sentence = "/".join(cut_word_list)  # 返回切好的句子
    return cut_word_list


# 双向最大匹配算法
def cut_words(sentence):
    """
    双向最大匹配算法
    :param sentence: 需要切的句子
    :return: 切好的词列表 列表元素为元组(词，词性)
    """
    fmm_word_list = fmm_cut_words(sentence)
    bmm_word_list = bmm_cut_words(sentence)
    fmm_word_list_length = len(fmm_word_list)
    bmm_word_list_length = len(bmm_word_list)
    if fmm_word_list_length < bmm_word_list_length:
        return fmm_word_list
    elif fmm_word_list_length > bmm_word_list_length:
        return bmm_word_list
    else:
        if fmm_word_list == bmm_word_list:
            return fmm_word_list
        else:
            # 返回FMM和BMM中单个字少的word_list
            single = 0
            for i in range(fmm_word_list_length):
                if len(fmm_word_list[i][0]) == 1:
                    single += 1
                if len(bmm_word_list[i][0]) == 1:
                    single -= 1
            if single >= 0:
                return bmm_word_list
            else:
                return fmm_word_list


def main():
    """
    用户交互接口
    :return:
    """
    init()
    while True:
        print("请输入需要分词的序列")
        input_str = input()
        if not input_str:
            break
        result = cut_words(input_str)
        print(f"分词结果\n{result}")


def test():
    init()
    # 问句
    with open("query_bak.txt", "r", encoding='utf-8') as f:
        # print(f.readline())
        query = re.split('\n', f.read().rstrip('\n'))
    for query in query:
        print(query)
        words = cut_words(query)
        print(words)


if __name__ == "__main__":
    # main()
    test()
