# 项目介绍
![_cgi-bin_mmwebwx-bin_webwxgetmsgimg__ MsgID=3627529868527961803 skey=@crypt_b427ad58_513de5431789e4b4ffcb38eb51df3c0d mmweb_appid=wx_webfilehelper](https://github.com/user-attachments/assets/a061c2eb-52d3-4d92-ba72-948b5e5fbac9)

本项目由前端、后端、数据处理三部分组成
因为小组人数众多，沟通成本过高，故而采用较为松耦合的方式进行项目开发，即各成员各自开发负责的业务条线，再统一采用前端Angular+后端FastAPI的架构整合成一个完整的项目。
大致分工为三个层次：公共数据处理，各条业务线数据处理及前后端开发，项目整合。
本项目采用前后端分离的架构

其中**前端项目**仓库地址：https://github.com/ecnu2024zhongtai/zhongtai_ng

**后端项目**位于本项目WebHosting目录下

# 项目准备
## 环境准备
debian12
## 数据库安装

1. Mongodb
2. PostgreSql
3. Redis
4. 可选：Hadoop、Hive、Spark
   
## 编程语言开发包安装

1. Julia 1.11
2. Python 3.12
3. C# donet8
4. Node 22
5. Angular 18
   
## 数据准备
至个业务目录执行数据处理脚本
## 后端环境依
```
cd WebHosting
pip install -r requirements.txt
```
## 前端环境依赖安装
```
npm install
```
## 其他中间件准备
```
Airflow
```
# 项目启动
## 后端启动
```
python main.py
```
![image](https://github.com/user-attachments/assets/15cedf3f-8ac9-48b3-8670-799d5162dde5)

## 前端启动
```
npm start
```
![image](https://github.com/user-attachments/assets/670fe6a2-3194-4005-9550-5094e36e8649)

