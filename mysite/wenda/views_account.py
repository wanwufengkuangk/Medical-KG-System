import re

from .models import Doctor, Question, Reply, User
from .view_support import is_ajax, json_http_response, redirect, render, slice_page

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
    if is_ajax(request):
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
            for question in slice_page(questions, page, page_size):
                question_info = dict()
                question_info['id'] = question.id
                question_info['title'] = question.title
                question_info['content'] = question.content
                question_info['date'] = question.date.strftime('%Y-%m-%d')
                question_info['num_reply'] = len(question.reply_set.all())
                print(question_info)
                data.append(question_info)
            return json_http_response({'question_list': data})
        else:
            return json_http_response({'question_list': []})
    else:
        return render(request, 'wenda/404.html')


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
    if is_ajax(request):
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
            for reply in slice_page(replies, page, page_size):
                reply_info = dict()
                reply_info['id'] = reply.id
                reply_info['content'] = reply.content
                reply_info['date'] = reply.date.strftime('%Y-%m-%d')
                reply_info['question_id'] = reply.question.id
                reply_info['question_title'] = reply.question.title
                reply_list.append(reply_info)
            data['reply_list'] = reply_list
            return json_http_response(data)
        else:
            return json_http_response({'reply_list': []})
    else:
        return render(request, 'wenda/404.html')


