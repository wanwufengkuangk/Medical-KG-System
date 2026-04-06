from .view_support import HttpResponse, JsonResponse, is_ajax, json_http_response, render, slice_page


def _department_handler():
    from Neo4j import department

    return department.Department()


def _disease_handler():
    from Neo4j import disease

    return disease.Disease()


def _drug_handler():
    from Neo4j import drug

    return drug.Drug()


def _population_handler():
    from Neo4j import population

    return population.Population()


def _symptom_handler():
    from Neo4j import symptom

    return symptom.Symptom()


def _question_classifier():
    from QA import question_classify

    return question_classify.QuestionClassify()

def index(request):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    print(user_role, username, 'aaaaaaaaaaaaa')
    return render(request, 'wenda/index.html')


def search(request):
    if request.method == 'POST':
        data = dict()
        data['search_text'] = request.POST['search_text']
        return render(request, 'wenda/search.html', {'data': data})
    else:
        return render(request, 'wenda/404.html')


def info_brief_ajax(request):
    if is_ajax(request):
        more_text = request.GET['more_type']
        search_text = request.GET['search_text']
        page = int(request.GET['page'])
        page_size = int(request.GET['page_size'])
        print(more_text, search_text, page, page_size)
        if more_text == 'disease':
            handler = _disease_handler()
            diseases_name = handler.fuzzy_search(search_text)
            data = []
            for disease_name in slice_page(diseases_name, page, page_size):
                print(disease_name)
                data.append(handler.disease_info_brief(disease_name))
            return json_http_response({'disease_list': data})
        elif more_text == 'symptom':
            handler = _symptom_handler()
            symptoms_name = handler.fuzzy_search(search_text)
            print(len(symptoms_name))
            data = []
            for symptom_name in slice_page(symptoms_name, page, page_size):
                print(symptom_name)
                data.append(handler.symptom_info_brief(symptom_name))
            return json_http_response({'symptom_list': data})
        elif more_text == 'drug':
            handler = _drug_handler()
            drugs_name = handler.fuzzy_search(search_text)
            print(len(drugs_name))
            data = []
            for drug_name in slice_page(drugs_name, page, page_size):
                print(drug_name)
                data.append(handler.drug_info_brief(drug_name))
            return json_http_response({'drug_list': data})
    else:
        return render(request, 'wenda/404.html')


def search_more(request, search_type):
    data = dict()
    if request.method == 'POST':
        data['search_text'] = request.POST['search_text']
    else:
        data['search_text'] = ''
    data['search_type'] = search_type
    if search_type == 'disease':
        data['search_type_zh'] = '疾病'
    elif search_type == 'symptom':
        data['search_type_zh'] = '症状'
    elif search_type == 'drug':
        data['search_type_zh'] = '药物'
    else:
        return render(request, 'wenda/404.html')
    return render(request, 'wenda/search_more.html', {'data': data})


def wenda(request):
    return render(request, 'wenda/wenda.html')


def wenda_ajax(request):
    if is_ajax(request):
        handler = _question_classifier()
        data = request.GET['question']
        print(data)
        answer = handler.classify(data)
        return json_http_response({'answer': answer})
    else:
        return render(request, 'wenda/404.html')


def department_html(request, keshi):
    data = dict()
    dept_first = ['全部科室', '内科', '外科', '妇产科', '传染科', '生殖健康',
                  '男科', '皮肤性病科', '中医科', '五官科', '精神科', '心理科',
                  '儿科', '营养科', '肿瘤科', '其他科室', '急诊科', '肝病']
    if keshi in dept_first:
        data['department'] = keshi
        return render(request, 'wenda/department.html', {'data': data})
    else:
        return render(request, 'wenda/404.html')


def department_ajax(request):
    if is_ajax(request):
        department_name = request.GET['department_name']
        page = int(request.GET['page'])
        page_size = int(request.GET['page_size'])
        print(department_name, page, page_size)
        handler = _department_handler()
        data = handler.fuzzy_search(department_name, page=page, page_size=page_size)
        return json_http_response({'disease_list': data})
    else:
        return render(request, 'wenda/404.html')


def population_html(request, renqun):
    renqun_list = ['全部', '男性', '女性', '老年', '儿童']
    if renqun in renqun_list:
        data = dict()
        data['population'] = renqun
        return render(request, 'wenda/people.html', {'data': data})
    else:
        return render(request, 'wenda/404.html')


def population_ajax(request):
    if is_ajax(request):
        population_name = request.GET['population_name']
        page = int(request.GET['page'])
        page_size = int(request.GET['page_size'])
        print(population_name, page, page_size)
        handler = _population_handler()
        data = handler.fuzzy_search(population_name, page=page, page_size=page_size)
        return json_http_response({'disease_list': data})
    else:
        return render(request, 'wenda/404.html')


def disease_info(request, name):
    handler = _disease_handler()
    data = handler.disease_info(name)
    if data is None:
        return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/disease.html', {'disease_info': data})


def symptom_info(request, name):
    handler = _symptom_handler()
    data = handler.symptom_info(name)
    if data is None:
        return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/symptom.html', {'symptom_info': data})


def drug_info(request, name):
    handler = _drug_handler()
    data = handler.drug_info(name)
    if data is None:
        return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/drug.html', {'drug_info': data})


def autocomplete_api(request):
    """搜索建议接口"""
    keyword = request.GET.get('keyword', '').strip()
    data = []

    if keyword:
        # 调用刚才写好的轻量级函数
        handler = _disease_handler()
        data = handler.get_suggestion(keyword)

    return JsonResponse({'list': data})


