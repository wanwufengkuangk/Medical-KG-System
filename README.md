# 基于医疗知识图谱的问答系统

#### 介绍

菜鸡速成本科毕业设计：首先，创建了知识图谱，然后实现了基于模板的问答，最后通过网页展示出来。

#### 软件架构

软件架构说明

1. **系统架构图**


2. **各部分功能**

   Answer：对查询结果进行组织，返回答案

   Cut：对问句进行分词

   Neo4j：对知识图谱查询的接口

   QA：模板匹配，问句解析

   mysite：系统网页

   spider：爬虫，知识图谱创建

   关系型数据库：存储用户业务信息


#### 开发环境

开发系统时所使用的环境版本。

| Python |      Neo4j       | MySQL | Django | pymysql | py2neo |
| :----: | :--------------: | :---: | :----: | :-----: | :----: |
|  3.7   | 3.5.16-Community |  8.0  | 3.0.4  |  1.0.2  | 4.3.0  |

|  pip   | urlib3 |  request  | requests |
| :----: | :----: | :-------: | :------: |
| 20.0.2 | 1.24.3 | 2019.4.13 |  2.23.0  |

注：若直接使用Neo4j数据`graph.db`，需Neo4j 使用 3.x 的版本，4.x的版本data存储格式变了。运行 neo4j 需安装相应的Java JDK

#### 使用说明

1. Neo4j 

   将graph.db 拷贝到Neo4j的安装目录下的/data/databases中,eg:`D:\Program Softwares\neo4j-community-3.5.16\data\databases`

   **启动Neo4j**   win：`neo4j.bat console`   mac: `neo4j console` 

   neo4j 默认用户名:`neo4j` 密码:`neo4j`   浏览器下输入命令：`:server change-password`可进行密码修改

2. pip 安装必须的库

   `pip install django==3.0.4 py2neo==4.3.0 pymysql==1.0.2`

   其他为爬虫需要的库 非必需。

3. mysql

   django是不能创建数据库的，只能够创建数据库表，因此，我们在连接数据库的时候要先建立一个数据库。

   在命令行进入mysql `mysql -u root -p`

   创建一个数据库 `create database wenda;`

4. django

   将`mysite/mysite/settings.py`文件中的`DATABASES`选项里的用户名和密码及数据库改为自己所设置的

   将`Neo4j/config.py`文件中的neo4j的用户名和密码修改为自己所设置的

   进入`manage.py`所在路径，输入`python manage.py makemigrations`，输入`python manage.py migrate`，将会在`wenda`数据库中创建出需要的表，若创建不成功，执行`python manage.py makemigrations wenda`，`python manage.py migrate`。[参考链接](https://www.cnblogs.com/michealjy/p/14018517.html)
  
    **启动Web服务**    执行 `python manage.py runserver`

