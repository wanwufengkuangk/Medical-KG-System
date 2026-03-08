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

# 注册模型，使其在管理员后台可见
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    # 后台列表中显示的字段
    list_display = ('user_name', 'name', 'hospital', 'department', 'confirmed')
    # 允许管理员在后台直接筛选审核状态
    list_filter = ('confirmed',)
    # 允许搜索用户名和真实姓名
    search_fields = ('user_name', 'name')

# 顺便把其他表也注册了，方便你管理整个系统
admin.site.register(User)
admin.site.register(Question)
admin.site.register(Reply)
admin.site.register(Feedback)

# 修改后台网页的标题
admin.site.site_header = '医疗辅助决策系统 - 超级管理后台'
admin.site.site_title = '管理员控制台'