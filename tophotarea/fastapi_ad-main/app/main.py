from fastapi import FastAPI
from app.api.v1.endpoints import user
from app.db.session import engine
from app.db.base import Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许的跨域源列表
origins = [
    "http://localhost",  # 本地开发环境
    "http://127.0.0.1",  # 本地开发环境
    "*",  # 或者允许所有的来源，这里只是为了示范，使用 "*" 会有安全风险
]

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 GET, POST, PUT, DELETE 等
    allow_headers=["*"],  # 允许所有头部
)



# 创建所有数据库表
Base.metadata.create_all(bind=engine)

# 根路径路由
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}

app.include_router(user.router, prefix="/api/v1")

#运行PS C:\Users\wujie\Downloads\fastapi_ad-main> uvicorn app.main:app --reload
#官网 https://fastapi.tiangolo.com/zh/
