from django.urls import path

from . import views


app_name = 'wenda'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('info_brief/ajax/', views.info_brief_ajax, name='info_brief_ajax'),
    path('search/<str:search_type>/', views.search_more, name='search_more'),
    path('wenda/', views.wenda, name='wenda'),
    path('wenda/ajax/', views.wenda_ajax, name='wenda_ajax'),
    path('department/<str:keshi>', views.department_html, name='department'),
    path('department_ajax/', views.department_ajax, name='department_ajax'),
    path('population/<str:renqun>', views.population_html, name='population'),
    path('population_ajax/', views.population_ajax, name='population_ajax'),
    path('disease/<str:name>', views.disease_info, name='disease'),
    path('symptom/<str:name>', views.symptom_info, name='symptom'),
    path('drug/<str:name>', views.drug_info, name='drug'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('user/<str:username>', views.user_info, name='user_info'),
    path('user/ajax/', views.user_info_ajax, name='user_info_ajax'),
    path('doctor/<str:username>', views.doctor_info, name='doctor_info'),
    path('doctor/ajax/', views.doctor_info_ajax, name='doctor_info_ajax'),
    path('wenyi/', views.wenyi, name='wenyi'),
    path('wenyi_reply/ajax/', views.wenyi_reply_ajax, name='wenyi_reply_ajax'),
    path('reply/', views.reply, name='reply'),
    path('question/<str:question_id>', views.question, name='question'),
    path('question_reply/ajax/', views.question_reply_ajax, name='question_reply_ajax'),
    path('feedback/<str:feedback_type>', views.feedback, name='feedback'),
    path('renz/', views.renz, name='renz'),
    path('alter/info/', views.alter_info, name='alter_info'),
    path('delete/question/<str:question_id>', views.delete_question, name='delete_question'),
    path('delete/reply/<str:reply_id>', views.delete_reply, name='delete_reply'),
    # 新添加1
    path('analysis/', views.analysis_view, name='analysis'),
    # 新增 3 # 大屏图谱的异步搜索接口
    path('analysis/search/', views.analysis_graph_search, name='analysis_search'),
    # DeepSeek 问答接口
    path('deepseek/ask/', views.deepseek_ask, name='deepseek_ask'),
]
