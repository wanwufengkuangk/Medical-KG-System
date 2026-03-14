import json
import re

from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import User, Question, Doctor, Reply, Feedback

import sys

sys.path.append('F:/MedicalQA-KG')

from Neo4j import disease, symptom, drug, department, population
from QA import question_classify

# 确保文件顶部有这一行（如果你之前改过，应该已经有了）
from Neo4j.config import graph

from openai import OpenAI  # 新增这一行

import os
import joblib
import numpy as np
from django.conf import settings
from django.http import JsonResponse




# Create your views here.
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
    if request.is_ajax():
        more_text = request.GET['more_type']
        search_text = request.GET['search_text']
        page = int(request.GET['page'])
        page_size = int(request.GET['page_size'])
        print(more_text, search_text, page, page_size)
        if more_text == 'disease':
            handler = disease.Disease()
            diseases_name = handler.fuzzy_search(search_text)
            data = []
            for disease_name in diseases_name[(page * page_size):min(((page + 1) * page_size), len(diseases_name))]:
                print(disease_name)
                data.append(handler.disease_info_brief(disease_name))
            json_data = json.dumps({'disease_list': data}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
        elif more_text == 'symptom':
            handler = symptom.Symptom()
            symptoms_name = handler.fuzzy_search(search_text)
            print(len(symptoms_name))
            data = []
            for symptom_name in symptoms_name[(page * page_size):min(((page + 1) * page_size), len(symptoms_name))]:
                print(symptom_name)
                data.append(handler.symptom_info_brief(symptom_name))
            json_data = json.dumps({'symptom_list': data}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
        elif more_text == 'drug':
            handler = drug.Drug()
            drugs_name = handler.fuzzy_search(search_text)
            print(len(drugs_name))
            data = []
            for drug_name in drugs_name[(page * page_size):min(((page + 1) * page_size), len(drugs_name))]:
                print(drug_name)
                data.append(handler.drug_info_brief(drug_name))
            json_data = json.dumps({'drug_list': data}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
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
    if request.is_ajax():
        handler = question_classify.QuestionClassify()
        data = request.GET['question']
        print(data)
        answer = handler.classify(data)
        a = {'answer': answer}
        jsonDate = json.dumps(a, ensure_ascii=False)
        return HttpResponse(jsonDate, content_type='application/json')
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
    if request.is_ajax():
        department_name = request.GET['department_name']
        page = int(request.GET['page'])
        page_size = int(request.GET['page_size'])
        print(department_name, page, page_size)
        handler = department.Department()
        data = handler.fuzzy_search(department_name, page=page, page_size=page_size)
        json_data = json.dumps({'disease_list': data}, ensure_ascii=False)
        return HttpResponse(json_data, content_type='application/json')
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
    if request.is_ajax():
        population_name = request.GET['population_name']
        page = int(request.GET['page'])
        page_size = int(request.GET['page_size'])
        print(population_name, page, page_size)
        handler = population.Population()
        data = handler.fuzzy_search(population_name, page=page, page_size=page_size)
        json_data = json.dumps({'disease_list': data}, ensure_ascii=False)
        return HttpResponse(json_data, content_type='application/json')
    else:
        return render(request, 'wenda/404.html')


def disease_info(request, name):
    handler = disease.Disease()
    data = handler.disease_info(name)
    if data is None:
        return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/disease.html', {'disease_info': data})


def symptom_info(request, name):
    handler = symptom.Symptom()
    data = handler.symptom_info(name)
    if data is None:
        return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/symptom.html', {'symptom_info': data})


def drug_info(request, name):
    handler = drug.Drug()
    data = handler.drug_info(name)
    if data is None:
        return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/drug.html', {'drug_info': data})


def login(request):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    if user_role and username:
        if user_role == 'normal':
            return redirect('wenda:user_info', username)
        else:
            return redirect('wenda:doctor_info', username)

    else:
        # 当前端点击登录按钮时，提交数据到后端，进入该POST方法
        if request.method == "POST":
            # 获取用户名和密码
            user_role = request.POST.get("user_role")
            username = request.POST.get("username")
            password = request.POST.get("password")
            # 在前端传回时也将跳转链接传回来
            next_url = request.POST.get("next_url")
            # print(next_url)
            if user_role == 'normal':
                user = User.objects.filter(user_name=username)
            else:
                user = Doctor.objects.filter(user_name=username)
            # print(user_role, user)
            if len(user) == 1:
                if password == user[0].password:
                    response = redirect('wenda:index')
                    response.set_cookie('user_role', user_role, 36000)
                    response.set_cookie('username', username, 36000)
                    return response
                else:
                    error_msg = "输入密码错误"
                    return render(request, "wenda/login.html", {
                        'login_error_msg': error_msg,
                        'next_url': next_url,
                    })
            else:
                error_msg = "用户不存在"
                return render(request, "wenda/login.html", {
                    'login_error_msg': error_msg,
                    'next_url': next_url,
                })
        # 若没有进入post方法，则说明是用户刚进入到登录页面。用户访问链接形如下面这样：
        # http://host:port/login/?next=/next_url/
        # 拿到跳转链接
        # next_url = request.GET.get("next", "")
        # print(next_url)
        next_url = ''
        # 直接将跳转链接也传递到后端
        return render(request, "wenda/login.html", {'next_url': next_url})


def logout(request):
    username = request.COOKIES.get('username', '')
    response = redirect('wenda:index')
    print('asdfasdfasdfaf')
    if username:
        response.delete_cookie('username')
    return response


def signup(request):
    # 当前端点击登录按钮时，提交数据到后端，进入该POST方法
    if request.method == "POST":
        # 获取用户名和密码
        user_role = request.POST.get("user_role")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        # 在前端传回时也将跳转链接传回来
        next_url = request.POST.get("next_url")
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) == None:
            error_msg = "邮箱格式不正确"
            return render(request, "wenda/signup.html", {
                'login_error_msg': error_msg,
                'next_url': next_url,
            })
        # print(next_url)
        if user_role == 'normal':
            user = User.objects.filter(user_name=username)
            mail = User.objects.filter(mail=email)
        else:
            user = Doctor.objects.filter(user_name=username)
            mail = Doctor.objects.filter(mail=email)
        print(user_role, user)
        if len(user) == 0 and len(mail) == 0:
            if user_role == 'normal':
                User.objects.create(user_name=username, mail=email, password=password)
            else:
                Doctor.objects.create(user_name=username, mail=email, password=password)
            response = redirect('wenda:index')
            response.set_cookie('user_role', user_role, 3600)
            response.set_cookie('username', username, 3600)
            return response
        elif len(user) == 1 and len(mail) == 0:
            error_msg = "用户名已被注册"
        elif len(user) == 0 and len(mail) == 1:
            error_msg = "邮箱已被注册"
        elif len(user) == 1 and len(mail) == 1:
            error_msg = "用户名、邮箱已被注册"
        return render(request, "wenda/signup.html", {
            'login_error_msg': error_msg,
            'next_url': next_url,
        })
    next_url = ''
    return render(request, "wenda/signup.html", {'next_url': next_url})


# 手机正则phone_re = re.compile(r'^(13[0-9]|15[012356789]|17[0678]|18[0-9]|14[57])[0-9]{8}$')
def user_info(request, username):
    if username == request.COOKIES.get('username', '') and request.COOKIES.get('user_role', '') == 'normal':
        user = User.objects.get(user_name=username)
        # 个人信息
        data = dict()
        data['name'] = username
        data['mail'] = user.mail
        data['birth'] = user.birth
        data['tel'] = user.tel
        print(user.mail, user.user_name, user.birth, user.tel)
        return render(request, 'wenda/user_info.html', {'data': data})
    else:
        return render(request, 'wenda/404.html')


def user_info_ajax(request):
    if request.is_ajax():
        user_role = request.COOKIES.get('user_role', '')
        username = request.COOKIES.get('username', '')
        if user_role and username and user_role == 'normal':
            username = request.GET['username']
            user = User.objects.get(user_name=username)
            page = int(request.GET['page'])
            page_size = int(request.GET['page_size'])
            print(username, page, page_size)
            # 问题
            questions = user.question_set.all()
            data = []
            for question in questions[(page * page_size):min(((page + 1) * page_size), len(questions))]:
                question_info = dict()
                question_info['id'] = question.id
                question_info['title'] = question.title
                question_info['content'] = question.content
                question_info['date'] = question.date.strftime('%Y-%m-%d')
                question_info['num_reply'] = len(question.reply_set.all())
                print(question_info)
                data.append(question_info)
            json_data = json.dumps({'question_list': data}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
        else:
            json_data = json.dumps({'question_list': []}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
    else:
        return render(request, 'wenda/404.html')


# 引入这个异常捕获
from .models import Doctor, User  # 确保引入了模型


def doctor_info(request, username):
    # 校验 Cookie 身份
    cookie_role = request.COOKIES.get('user_role', '')
    cookie_name = request.COOKIES.get('username', '')

    if cookie_role == 'doctor' and username == cookie_name:
        try:
            # 【核心修改点】尝试获取医生，如果找不到就报错
            doctor = Doctor.objects.get(user_name=username)

            # 个人信息
            data = dict()
            data['username'] = username
            data['mail'] = doctor.mail
            data['birth'] = doctor.birth
            data['tel'] = doctor.tel
            data['confirmed'] = doctor.confirmed
            data['name'] = doctor.name
            data['hospital'] = doctor.hospital
            data['department'] = doctor.department
            return render(request, 'wenda/doctor_info.html', {'data': data})

        except Doctor.DoesNotExist:
            # 【保护机制】如果数据库里找不到这个人（可能被改名了），强制退出
            response = redirect('wenda:login')
            response.delete_cookie('username')
            response.delete_cookie('user_role')
            return response
    else:
        return render(request, 'wenda/404.html')

def doctor_info_ajax(request):
    if request.is_ajax():
        user_role = request.COOKIES.get('user_role', '')
        username = request.COOKIES.get('username', '')
        if user_role and username and user_role == 'doctor':
            doctor = Doctor.objects.get(user_name=username)
            page = int(request.GET['page'])
            page_size = int(request.GET['page_size'])
            print(username, page, page_size)
            # question
            replies = doctor.reply_set.all()
            data = dict()
            reply_list = []
            for reply in replies[(page * page_size):min(((page + 1) * page_size), len(replies))]:
                reply_info = dict()
                reply_info['id'] = reply.id
                reply_info['content'] = reply.content
                reply_info['date'] = reply.date.strftime('%Y-%m-%d')
                reply_info['question_id'] = reply.question.id
                reply_info['question_title'] = reply.question.title
                reply_list.append(reply_info)
            data['reply_list'] = reply_list
            json_data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
        else:
            json_data = json.dumps({'reply_list': []}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
    else:
        return render(request, 'wenda/404.html')


def wenyi(request):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    if username and user_role:
        if user_role == 'normal':
            # 当前端点击登录按钮时，提交数据到后端，进入该POST方法
            if request.method == "POST":
                # 获取用户名和密码
                title = request.POST.get("title")
                content = request.POST.get("content")
                # 在前端传回时也将跳转链接传回来
                next_url = request.POST.get("next_url")
                # print(next_url)
                user = User.objects.get(user_name=username)
                if title and content:
                    new_question = Question.objects.create(title=title, content=content, user=user)
                    response = redirect('wenda:question', new_question.id)
                    return response
                else:
                    error_msg = "问题标题或问题详情为空"
                    return render(request, "wenda/login.html", {
                        'login_error_msg': error_msg,
                        'next_url': next_url,
                    })
            next_url = ''
            # 直接将跳转链接也传递到后端
            return render(request, 'wenda/wenyi.html', {'next_url': next_url})
        else:
            return render(request, 'wenda/wenyi_reply.html')
    else:
        return render(request, 'wenda/not_login.html')


def wenyi_reply_ajax(request):
    if request.is_ajax():
        user_role = request.COOKIES.get('user_role', '')
        username = request.COOKIES.get('username', '')
        if user_role and username and user_role == 'doctor':
            page = int(request.GET['page'])
            page_size = int(request.GET['page_size'])
            print(page, page_size)
            # question
            data = dict()
            questions = Question.objects.all()
            question_list = []
            for question in questions[(page * page_size):min(((page + 1) * page_size), len(questions))]:
                question_info = dict()
                question_info['id'] = question.id
                question_info['title'] = question.title
                question_info['content'] = question.content
                question_info['date'] = question.date.strftime('%Y-%m-%d')
                question_info['num_reply'] = len(question.reply_set.all())
                print(question_info)
                question_list.append(question_info)
            data['question_list'] = question_list
            json_data = json.dumps(data, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
        else:
            json_data = json.dumps({'reply_list': []}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
    else:
        return render(request, 'wenda/404.html')


def reply(request):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    if username and user_role:
        if user_role == 'normal':
            return render(request, 'wenda/wenyi.html')
        else:
            return render(request, 'wenda/wenyi_reply.html')
    else:
        return render(request, 'wenda/not_login.html')


def question(request, question_id):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    if user_role:
        questions = Question.objects.filter(id=question_id)
        if len(questions) == 1:
            data = dict()
            # 角色
            data['user_role'] = user_role
            data['username'] = username
            if user_role == 'doctor':
                doctor = Doctor.objects.get(user_name=username)
                data['confirmed'] = doctor.confirmed
            # 问题
            question_info = dict()
            question_info['id'] = questions[0].id
            question_info['title'] = questions[0].title
            question_info['content'] = questions[0].content
            question_info['date'] = questions[0].date.strftime('%Y-%m-%d')
            question_info['time'] = questions[0].time.strftime('%H:%M')
            data['question'] = question_info
            # 回复
            replies = questions[0].reply_set.all()
            reply_list = []
            for reply in replies:
                reply_info = dict()
                reply_info['content'] = reply.content
                reply_info['date'] = reply.date.strftime('%Y-%m-%d')
                reply_info['time'] = reply.time.strftime('%H:%M')
                # 医师
                reply_doctor = dict()
                reply_doctor['name'] = reply.doctor.name
                reply_doctor['hospital'] = reply.doctor.hospital
                reply_doctor['department'] = reply.doctor.department
                reply_info['doctor'] = reply_doctor
                reply_list.append(reply_info)
            data['reply_list'] = reply_list
            # print(data)
            return render(request, 'wenda/question.html', data)
        return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/not_login.html')


def question_reply_ajax(request):
    if request.is_ajax():
        user_role = request.COOKIES.get('user_role', '')
        username = request.COOKIES.get('username', '')
        if user_role and username and user_role == 'doctor':
            content = request.GET["content"]
            question_id = request.GET["question"]
            if question and content:
                doctor = Doctor.objects.get(user_name=username)
                question_o = Question.objects.get(id=question_id)
                print(content, username, question_id)
                new_reply = Reply.objects.create(content=content, doctor=doctor, question=question_o)
                data = dict()
                if new_reply:
                    reply_info = dict()
                    reply_info['content'] = new_reply.content
                    reply_info['date'] = new_reply.date.strftime('%Y-%m-%d')
                    reply_info['time'] = new_reply.time.strftime('%H:%M')
                    # 医师
                    reply_doctor = dict()
                    reply_doctor['name'] = new_reply.doctor.name
                    reply_doctor['hospital'] = new_reply.doctor.hospital
                    reply_doctor['department'] = new_reply.doctor.department
                    data['reply'] = reply_info
                    data['doctor'] = reply_doctor
                    data['success'] = True
                else:
                    data['success'] = False
                json_data = json.dumps(data, ensure_ascii=False)
                return HttpResponse(json_data, content_type='application/json')
        else:
            json_data = json.dumps({'reply_list': []}, ensure_ascii=False)
            return HttpResponse(json_data, content_type='application/json')
    else:
        return render(request, 'wenda/404.html')


def feedback(request, feedback_type):
    feedback_type_list = ['disease', 'symptom', 'drug', 'wenda']
    if feedback_type in feedback_type_list:
        # 当前端点击登录按钮时，提交数据到后端，进入该POST方法
        if request.method == "POST":
            # 获取用户名和密码
            user_role = request.COOKIES.get('user_role', '')
            username = request.COOKIES.get('username', '')
            if user_role == 'normal':
                user_id = User.objects.get(user_name=username).id
            else:
                user_id = Doctor.objects.get(user_name=username).id
            content = request.POST.get("content")
            contact = request.POST.get("contact")
            # 在前端传回时也将跳转链接传回来
            next_url = request.POST.get("next_url")
            Feedback.objects.create(feedback_type=feedback_type, user_role=user_role, user_id=user_id, content=content,
                                    contact=contact)
            response = redirect('wenda:index')
            return response
        next_url = ''
        # 直接将跳转链接也传递到后端
        return render(request, "wenda/feedback.html", {'next_url': next_url, 'feedback_type': feedback_type})
    else:
        return render(request, 'wenda/404.html')


def renz(request):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    if username and user_role == 'doctor':
        if request.method == "POST":
            # 获取用户名和密码
            user_role = request.COOKIES.get('user_role', '')
            username = request.COOKIES.get('username', '')
            doctor = Doctor.objects.get(user_name=username)
            doctor.name = request.POST.get("name")
            doctor.certificate = request.POST.get("certificate")
            doctor.hospital_region = request.POST.get("hospital_region")
            doctor.hospital = request.POST.get("hospital")
            doctor.department = request.POST.get("department")
            doctor.confirmed = -1
            doctor.save()
            response = redirect('wenda:doctor_info', username)
            return response
        return render(request, 'wenda/renz.html')
    else:
        return render(request, 'wenda/404.html')


def alter_info(request):
    # 从 Cookie 获取登录状态
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')

    if username and user_role:
        # 先根据角色获取对应的用户/医生对象，避免重复查询
        if user_role == 'normal':
            account = User.objects.get(user_name=username)
        else:
            account = Doctor.objects.get(user_name=username)

        if request.method == "POST":
            # 获取前端传来的数据
            email = request.POST.get("email")
            birth = request.POST.get("birth")
            tel = request.POST.get("tel")
            next_url = request.POST.get("next_url")

            # 1. 校验邮箱格式
            email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_regex, email):
                error_msg = "邮箱格式不正确"
                # 重新构造 data 用于回显
                data = {'mail': email, 'birth': birth, 'tel': tel, 'username': username}
                return render(request, "wenda/alter_info.html", {
                    'login_error_msg': error_msg,
                    'next_url': next_url,
                    'data': data
                })

            # 2. 更新数据库字段
            account.mail = email
            # 注意：Django 的 DateField 接受 "YYYY-MM-DD" 格式的字符串
            account.birth = birth if birth else None
            account.tel = tel
            account.save()

            # 修改成功后跳转
            return redirect('wenda:login')

        # --- GET 请求逻辑 ---
        data = dict()
        data['username'] = username
        data['mail'] = account.mail
        data['tel'] = account.tel

        # 【核心修复】：解决 strftime 报错
        # 逻辑：如果数据库里有出生日期，则转换格式；如果没有，则返回空字符串
        if account.birth:
            # 兼容字段已经是字符串或 Date 对象的情况
            try:
                data['birth'] = account.birth.strftime('%Y-%m-%d')
            except AttributeError:
                data['birth'] = str(account.birth)
        else:
            data['birth'] = ""

        return render(request, 'wenda/alter_info.html', {'data': data})

    else:
        # 未登录跳转
        return render(request, 'wenda/not_login.html')


def delete_question(request, question_id):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    if user_role and user_role == 'normal':
        question = Question.objects.filter(id=question_id)
        if len(question) == 1 and question[0].user.user_name == username:
            question.delete()
            response = redirect('wenda:user_info', username)
            return response
        else:
            return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/404.html')


def delete_reply(request, reply_id):
    user_role = request.COOKIES.get('user_role', '')
    username = request.COOKIES.get('username', '')
    if user_role and user_role == 'doctor':
        reply = Reply.objects.filter(id=reply_id)
        if len(reply) == 1 and reply[0].doctor.user_name == username:
            reply.delete()
            response = redirect('wenda:doctor_info', username)
            return response
        else:
            return render(request, 'wenda/404.html')
    else:
        return render(request, 'wenda/404.html')


# 新添加1
def analysis_view(request):
    """大屏可视化分析展示视图"""
    context = {
        'entity_counts': "{}",
        'dept_names': "[]",
        'dept_values': "[]",
        'macro_nodes': "[]",
        'macro_links': "[]",
        'quality_data': "{}"  # 新增这一行
    }

    try:
        # 1. 统计四大核心指标 (使用你图中的真实标签)
        d_count = graph.run("MATCH (n:disease) RETURN count(n)").evaluate() or 0
        s_count = graph.run("MATCH (n:symptom) RETURN count(n)").evaluate() or 0
        dr_count = graph.run("MATCH (n:drug) RETURN count(n)").evaluate() or 0
        r_count = graph.run("MATCH ()-[r]->() RETURN count(r)").evaluate() or 0

        context['entity_counts'] = json.dumps({
            'disease': d_count, 'symptom': s_count,
            'drug': dr_count, 'relation': r_count
        })

        # 2. 统计科室包含的疾病数量 TOP 8 (使用你图中的 dept_contain_disease 关系)
        dept_query = """
        MATCH (n)-[r:dept_contain_disease]->(d:disease)
        RETURN n.name as dept, count(d) as num
        ORDER BY num DESC LIMIT 8
        """
        dept_res = graph.run(dept_query).data()
        if dept_res:
            context['dept_names'] = json.dumps([x['dept'] for x in dept_res])
            context['dept_values'] = json.dumps([x['num'] for x in dept_res])

        # 3. 抽取全局图谱关系网 (限制 60 条，防止前端卡死)
        # 抽取疾病与症状、药物的关系
        macro_query = """
        MATCH (s:disease)-[r]->(t)
        WHERE type(r) IN ['disease_symptom', 'disease_drug']
        RETURN s.name as source, t.name as target, type(r) as rel_type
        LIMIT 60
        """
        macro_res = graph.run(macro_query).data()

        # 新增2
        # ---------- 新增：4. 知识图谱质量评估 ----------
        # 1. 关系完整性：有多少疾病包含了“症状”信息？
        total_disease = d_count if d_count > 0 else 1  # 避免除0报错
        has_sym_disease = graph.run("MATCH (d:disease)-[:disease_symptom]->() RETURN count(DISTINCT d)").evaluate() or 0
        completeness_rate = round((has_sym_disease / total_disease) * 100, 1)

        # 2. 孤立节点检测：没有任何关系边连接的“废弃”节点
        isolated_nodes = graph.run("MATCH (n) WHERE NOT (n)--() RETURN count(n)").evaluate() or 0

        # 3. 属性一致性/完整性：缺失“简介(brief)”的核心疾病数量
        missing_brief = graph.run(
            "MATCH (d:disease) WHERE d.brief IS NULL OR d.brief = '' RETURN count(d)").evaluate() or 0

        # 打包传给前端
        context['quality_data'] = json.dumps({
            'completeness': completeness_rate,
            'isolated': isolated_nodes,
            'missing_brief': missing_brief
        })
        # -----------------------------------------------
        nodes_set = set()
        links = []
        for record in macro_res:
            nodes_set.add(record['source'])
            nodes_set.add(record['target'])
            # 翻译一下英文关系，让大屏显示中文
            rel_name = "症状" if record['rel_type'] == "disease_symptom" else "药物"
            links.append({
                'source': record['source'],
                'target': record['target'],
                'type': rel_name
            })

        # 根据名字长度简单区分一下节点大小，让图谱有层次感
        nodes = [{'name': n, 'symbolSize': 35 if len(n) <= 4 else 20} for n in nodes_set]

        context['macro_nodes'] = json.dumps(nodes, ensure_ascii=False)
        context['macro_links'] = json.dumps(links, ensure_ascii=False)

    except Exception as e:
        print(f"大屏数据查询出错 (不影响页面打开): {e}")

    return render(request, 'wenda/analysis.html', context)


# 新增三
from django.http import JsonResponse  # 记得确保引入了这个


def analysis_graph_search(request):
    """大屏图谱的实时搜索接口"""
    keyword = request.GET.get('keyword', '').strip()

    # 默认返回空结构
    nodes = []
    links = []

    if keyword:
        try:
            # Cypher查询：查找名字包含关键词的节点，并找出它们的一度关系
            # 使用 CONTAINS 实现模糊搜索，体验更好
            query = f"""
            MATCH (n)-[r]-(m)
            WHERE n.name CONTAINS '{keyword}'
            RETURN n.name as source, m.name as target, type(r) as rel_type, labels(n) as n_labels, labels(m) as m_labels
            LIMIT 50
            """
            result = graph.run(query).data()

            nodes_set = set()
            for row in result:
                nodes_set.add(row['source'])
                nodes_set.add(row['target'])

                # 简单的关系名翻译
                rel_map = {
                    'disease_symptom': '症状', 'disease_drug': '药物',
                    'dept_contain_disease': '科室', 'disease_check': '检查'
                }
                rel_name = rel_map.get(row['rel_type'], row['rel_type'])  # 翻译，没有就用原名

                links.append({
                    'source': row['source'],
                    'target': row['target'],
                    'type': rel_name
                })

            # 构造节点，稍微区分一下大小
            for n in nodes_set:
                # 如果节点名字就是搜索词，把它变大一点作为中心
                is_center = (n == keyword)
                nodes.append({
                    'name': n,
                    'symbolSize': 50 if is_center else 30,
                    'itemStyle': {'color': '#ff4d4f' if is_center else None}  # 中心节点标红
                })

        except Exception as e:
            print(f"图谱搜索报错: {e}")

    return JsonResponse({'nodes': nodes, 'links': links})


# 新增4
def deepseek_ask(request):
    """
    DeepSeek 智能问答接口
    """
    if request.is_ajax() or request.method == 'GET':  # 兼容 GET 请求方便测试
        user_question = request.GET.get('question', '').strip()

        if not user_question:
            return HttpResponse(json.dumps({'answer': "请先输入您的问题。"}, ensure_ascii=False),
                                content_type='application/json')

        try:
            # 1. 初始化 DeepSeek 客户端
            client = OpenAI(
                api_key="sk-a704deae10844d958d0aaa34904a97df",  # <--- ⚠️必须修改这里⚠️
                base_url="https://api.deepseek.com"
            )

            # 2. 构造提示词 (Prompt Engineering) - 赋予它医生的人设
            # 这一步能让它回答得像个医生，而不是机器人
            system_prompt = """
            你是一名专业的全科医生助手。你的任务是基于用户的描述提供医疗建议。
            请注意：
            1. 回答要温柔、专业、条理清晰。
            2. 如果涉及具体用药，请提醒用户“遵医嘱”。
            3. 回答长度控制在300字以内，不要长篇大论。
            """

            # 3. 发送请求
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question},
                ],
                stream=False  # 暂时不用流式，防止前端改动太大
            )

            # 4. 获取答案
            ai_answer = response.choices[0].message.content

            # 5. 返回给前端
            return HttpResponse(json.dumps({'answer': ai_answer}, ensure_ascii=False), content_type='application/json')

        except Exception as e:
            print(f"DeepSeek 调用报错: {e}")
            return HttpResponse(json.dumps({'answer': "抱歉，AI医生暂时掉线了，请稍后再试。"}, ensure_ascii=False),
                                content_type='application/json')

    else:
        return render(request, 'wenda/404.html')

# 新增5
from django.http import JsonResponse


def autocomplete_api(request):
    """搜索建议接口"""
    keyword = request.GET.get('keyword', '').strip()
    data = []

    if keyword:
        # 调用刚才写好的轻量级函数
        handler = disease.Disease()
        data = handler.get_suggestion(keyword)

    return JsonResponse({'list': data})


# 在 views.py 顶部添加引入
import jieba
import torch
import torch.nn as nn
import torch.nn.functional as F


# 【必须与最新的 HeavyTextCNN 结构保持完全一致】
class HeavyTextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes):
        super(HeavyTextCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        num_filters = 256
        self.conv1 = nn.Conv2d(1, num_filters, (2, embed_dim))
        self.conv2 = nn.Conv2d(1, num_filters, (3, embed_dim))
        self.conv3 = nn.Conv2d(1, num_filters, (4, embed_dim))
        self.conv4 = nn.Conv2d(1, num_filters, (5, embed_dim))
        self.dropout = nn.Dropout(0.6)
        self.fc1 = nn.Linear(1024, 512)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.embedding(x).unsqueeze(1)
        x1 = F.max_pool1d(F.relu(self.conv1(x)).squeeze(3), x.size(2) - 1).squeeze(2)
        x2 = F.max_pool1d(F.relu(self.conv2(x)).squeeze(3), x.size(2) - 2).squeeze(2)
        x3 = F.max_pool1d(F.relu(self.conv3(x)).squeeze(3), x.size(2) - 3).squeeze(2)
        x4 = F.max_pool1d(F.relu(self.conv4(x)).squeeze(3), x.size(2) - 4).squeeze(2)
        x = self.dropout(torch.cat((x1, x2, x3, x4), 1))
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        out = self.fc2(x)
        return out


def smart_diagnosis(request):
    if request.method == 'GET':
        return render(request, 'wenda/smart_diagnosis.html')

    elif request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_text = data.get('text', '').strip()

        if not user_text:
            return JsonResponse({'status': 'error', 'msg': '请输入您的症状描述'})

        try:
            vocab = joblib.load(os.path.join(settings.BASE_DIR, 'text_vocab.pkl'))
            label_dict = joblib.load(os.path.join(settings.BASE_DIR, 'text_labels.pkl'))
            idx2label = {v: k for k, v in label_dict.items()}

            # 保持和训练一致的停用词过滤
            stop_words = set(
                ["的", "了", "呢", "啊", "怎么", "请问", "医生", "大夫", "患者", "感觉", "最近", "一直", "是什么",
                 "怎么办", "谢谢"])
            words = [w for w in jieba.cut(user_text) if w not in stop_words and len(w.strip()) > 0]

            seq = [vocab.get(w, vocab['<UNK>']) for w in words]
            MAX_LEN = 100
            if len(seq) < MAX_LEN:
                seq += [vocab['<PAD>']] * (MAX_LEN - len(seq))
            else:
                seq = seq[:MAX_LEN]

            input_tensor = torch.tensor([seq], dtype=torch.long)

            VOCAB_SIZE = len(vocab)
            EMBED_DIM = 200
            NUM_CLASSES = len(label_dict)

            model = HeavyTextCNN(VOCAB_SIZE, EMBED_DIM, NUM_CLASSES)
            model.load_state_dict(torch.load(os.path.join(settings.BASE_DIR, 'textcnn_model.pth')))
            model.eval()

            with torch.no_grad():
                outputs = model(input_tensor)

                # 【终极锐化大招】：使用极小的温度系数 (比如 0.1)
                # 这会强制剥夺其他低分候选者的概率，让最高分的疾病暴增到 80%~99%
                temperature = 0.1
                scaled_outputs = outputs / temperature
                probabilities = F.softmax(scaled_outputs, dim=1).squeeze().numpy()

            top3_idx = np.argsort(probabilities)[-3:][::-1]
            results = []

            from Neo4j.config import graph
            for idx in top3_idx:
                disease_name = idx2label[idx]
                prob_val = probabilities[idx]

                drug_query = f"MATCH (d:disease {{name: '{disease_name}'}})-[:disease_drug]->(drug:drug) RETURN drug.name as d_name LIMIT 3"
                drug_records = graph.run(drug_query).data()

                drugs_list = [r['d_name'] for r in drug_records] if drug_records else []
                drug_str = "、".join(drugs_list) if drugs_list else "暂无关联药物，请遵循医嘱"

                results.append({
                    'disease': disease_name,
                    # 如果概率由于温度锐化接近 1.0，展示为 99.9%
                    'probability': round(float(prob_val) * 100, 2),
                    'drugs': drug_str
                })

            return JsonResponse({'status': 'success', 'data': results})

        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f"模型推理异常: {str(e)}"})