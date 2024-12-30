


## 项目结构
```
fastapi_ad/
├── app/
│   ├── api/                  # API 路由
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── user.py   # 用户模块 API 端点
│   │   │   │   ├── auth.py   # 认证模块 API 端点
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/                 # 核心配置、初始化
│   │   ├── config.py         # 全局配置文件
│   │   ├── security.py       # 认证和授权模块
│   │   └── __init__.py
│   ├── db/                   # 数据库连接及管理
│   │   ├── base.py           # 数据库基础模块
│   │   ├── session.py        # 数据库会话管理
│   │   └── __init__.py
│   ├── models/               # 数据库模型
│   │   ├── user.py
│   │   └── __init__.py
│   ├── schemas/              # 数据传输对象 (Pydantic 模型)
│   │   ├── user.py
│   │   └── __init__.py
│   ├── services/             # 业务逻辑
│   │   ├── user_service.py
│   │   └── __init__.py
│   ├── main.py               # 应用入口
│   ├── dependencies.py       # 依赖注入
│   └── __init__.py
├── tests/                    # 单元测试和集成测试
│   ├── test_user.py
│   └── __init__.py
├── alembic/                  # 数据库迁移管理 (例如使用 Alembic)
│   └── versions/
├── .env                      # 环境变量文件
├── requirements.txt          # 项目依赖
└── README.md
```






