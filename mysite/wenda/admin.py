# from django.contrib import admin
#
# from .models import User, Question, Doctor, Reply, Feedback
#
# # Register your models here.
#
# admin.site.register(User)
#
# admin.site.register(Question)
#
# admin.site.register(Doctor)
#
# admin.site.register(Reply)
#
# admin.site.register(Feedback)
from django.contrib import admin
from .models import User, Doctor, Question, Reply, Feedback
from django.contrib import admin
from .models import Doctor, User, Question, Reply

# 定义一个高级管理配置，让列表页更好看
class DoctorAdmin(admin.ModelAdmin):
    # 在列表中显示这些字段
    list_display = ('user_name', 'name', 'hospital', 'department', 'confirmed')
    # 允许点击这些字段进入编辑
    list_display_links = ('user_name', 'name')
    # 允许直接在列表页修改认证状态
    list_editable = ('confirmed',)
    # 右侧增加过滤器（按认证状态筛选）
    list_filter = ('confirmed', 'hospital_region')
    # 增加搜索框
    search_fields = ('name', 'hospital', 'user_name')

# 注册模型
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(User)
admin.site.register(Question)
admin.site.register(Reply)