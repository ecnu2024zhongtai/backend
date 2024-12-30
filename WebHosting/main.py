from fastapi import FastAPI, APIRouter, Depends
from app.api.v1.endpoints import trip
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # 允许所有来源
    allow_credentials=True,        # 允许发送凭据（如 Cookies）
    allow_methods=["*"],           # 允许所有 HTTP 方法
    allow_headers=["*"],           # 允许所有 HTTP 请求头
)

# 根路径路由
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}

app.include_router(trip.router, prefix="/api/v1")


import os

port = int(os.environ.get("PORT", 8004))
uvicorn.run(app, host="::", port=port)