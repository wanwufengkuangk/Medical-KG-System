import json
import re

from .models import Doctor, Feedback, Question, Reply, User
from .view_support import is_ajax, json_http_response, redirect, render, slice_page

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
    if is_ajax(request):
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
            for question in slice_page(questions, page, page_size):
                question_info = dict()
                question_info['id'] = question.id
                question_info['title'] = question.title
                question_info['content'] = question.content
                question_info['date'] = question.date.strftime('%Y-%m-%d')
                question_info['num_reply'] = len(question.reply_set.all())
                print(question_info)
                question_list.append(question_info)
            data['question_list'] = question_list
            return json_http_response(data)
        else:
            return json_http_response({'reply_list': []})
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
    if is_ajax(request):
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
                return json_http_response(data)
        else:
            return json_http_response({'reply_list': []})
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
