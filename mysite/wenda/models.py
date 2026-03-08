from django.db import models


# Create your models here.


# 用户
class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=16)
    mail = models.EmailField(max_length=32)
    password = models.CharField(max_length=16)
    # 个人信息
    birth = models.DateField(max_length=32, null=True, blank=True)
    tel = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return self.user_name


# 医师
class Doctor(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=16)
    mail = models.EmailField(max_length=32)
    password = models.CharField(max_length=16)
    # 个人信息
    birth = models.DateField(max_length=32, null=True, blank=True)
    tel = models.CharField(max_length=16, null=True, blank=True)
    # 认证信息
    confirmed = models.IntegerField(default=False)
    name = models.CharField(max_length=16, null=True, blank=True)
    certificate = models.CharField(max_length=64, null=True, blank=True)
    hospital_region = models.CharField(max_length=64, null=True, blank=True)
    hospital = models.CharField(max_length=64, null=True, blank=True)
    department = models.CharField(max_length=64, null=True, blank=True)
    # 照片
    # photo_card = models.ImageField(default=None)
    # photo_certificate = models.ImageField(default=None)

    def __str__(self):
        return self.user_name


# 咨询问题
class Question(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    content = models.TextField(max_length=10000)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date', '-time']


# 回复
class Reply(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField(max_length=10000)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    # 外键
    doctor = models.ForeignKey(Doctor, default=None, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

    class Meta:
        ordering = ['-date', '-time']


# 反馈
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    feedback_type = models.CharField(max_length=100)
    content = models.TextField(max_length=20000)
    contact = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    user_role = models.CharField(max_length=100)
    user_id = models.IntegerField()

    def __str__(self):
        template = '{0.feedback_type}, {0.content}'
        return template.format(self)
        # return self.feedback_type
