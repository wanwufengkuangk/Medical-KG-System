# 项目配置文档

#### 介绍

本文件用于记录项目运行前需要确认的配置项和常用命令，便于在本地快速完成 Django、MySQL 和 Neo4j 的基础配置。

#### 配置说明

1. **Python 环境**

   当前项目建议使用 conda 环境：`med_kg`

   激活命令：

   `conda activate med_kg`

2. **Django 数据库配置**

   配置文件位置：`mysite/mysite/settings.py`

   当前项目默认连接 MySQL，主要配置项如下：

   - 数据库名：`wenda`
   - 用户名：`root`
   - 主机：`127.0.0.1`
   - 端口：`3306`
   如果本地数据库账号或密码不同，需要先修改 `DATABASES` 中对应的配置。

3. **Neo4j 配置**

   配置文件位置：`Neo4j/config.py`

   当前项目默认连接：

   - 地址：`http://localhost:7474`
   - 用户名：`neo4j`

   如果你本地 Neo4j 密码不同，需要修改 `PASSWORD` 变量，并保证浏览器端和项目配置保持一致。

4. **后台界面配置**

   后台管理端使用了 `Jazzmin` 进行界面美化，相关配置位于：

   - `mysite/mysite/settings.py`
   - `mysite/wenda/static/wenda/css/admin-theme.css`

   如果只是调整后台样式，一般不需要改动业务逻辑文件。

#### 常用命令

1. **安装依赖**

   原命令：

   `E:\gitlab\medical\venv\Scripts\pip.exe install django==3.0.4 py2neo==4.3.0 pymysql==1.0.2`

   当前环境下更建议直接在项目目录执行：

   `pip install django==3.0.4 py2neo==4.3.0 pymysql==1.0.2`

2. **生成迁移文件**

   原命令：

   `python E:\\gitlab\\medical\\mysite\\manage.py  makemigrations wenda`

   当前项目目录下可执行：

   `python manage.py makemigrations wenda`

3. **执行数据库迁移**

   原命令：

   ` python  manage.py migrate`

   建议命令：

   `python manage.py migrate`

4. **启动项目**

   原命令：

   `python manage.py runserver`

#### 使用说明

1. 先激活环境并进入项目目录

   `conda activate med_kg`

   `cd C:\Users\89657\Desktop\medical\mysite`

2. 再确认 MySQL 和 Neo4j 配置是否与本机一致

3. 然后执行迁移命令

   `python manage.py makemigrations wenda`

   `python manage.py migrate`

4. 最后启动服务

   `python manage.py runserver`
