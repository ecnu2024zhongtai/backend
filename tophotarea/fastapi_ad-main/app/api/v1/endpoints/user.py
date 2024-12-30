from ast import Import
from fastapi import APIRouter, Depends, HTTPException,WebSocket,WebSocketDisconnect
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse
import asyncio
from typing import List
from app.services.user_service import create_user
from app.services.topkarea_service import getClustersByGrahamScanService
from app.services.topkarea_service import getCurrentRoads
from app.services.topkarea_service import searchClustersByEuclideanDistance
from app.services.topkarea_service import selectbestpath
from app.dependencies import get_db
import random

router = APIRouter()

#.\env\scripts\uvicorn app.main:app --reload

@router.post("/users/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db=db, user=user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User registration failed.")
    return db_user

#�õ���ͬʱ��ε������ؿ���
@router.get("/topkarea/")
def getClustersByGrahamScan(time:int):
    clusters = getClustersByGrahamScanService(time)
    return clusters

#�õ�ʵʱ��ͨ����
@router.get("/getRoads/")
def getRoads():
    return getCurrentRoads()

#���ݾ�γ�Ȼ�ȡ������������
@router.get("/searchtopkarea/")
def searchtopkarea(lat:float,lng:float):
    return searchClustersByEuclideanDistance(lat,lng)

#·���滮    
@router.get("/sendtopkarea/")
def sendtopkarea(lat:float,lng:float):
    return selectbestpath(lat,lng);


# # ģ�⽻ͨ����
# def get_traffic_data() -> List[dict]:
#     return [
#         {"lat": 45.790, "lng": 126.651, "traffic_status": random.choice(['clear', 'congested'])},
#         {"lat": 45.791, "lng": 126.652, "traffic_status": random.choice(['clear', 'congested'])},
#         {"lat": 45.792, "lng": 126.653, "traffic_status": random.choice(['clear', 'congested'])},
#         {"lat": 45.793, "lng": 126.654, "traffic_status": random.choice(['clear', 'congested'])},
#         {"lat": 45.794, "lng": 126.655, "traffic_status": random.choice(['clear', 'congested'])},
#         {"lat": 45.795, "lng": 126.656, "traffic_status": random.choice(['clear', 'congested'])}
#     ]


# @router.websocket("/ws/traffic")
# async def traffic_websokcet(websocket:WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#              # ÿ3������ͻ��˷���һ�ν�ͨ����
#             traffic_data = get_traffic_data()
#             await websocket.send_json(traffic_data)
#             await asyncio.sleep(3)
#     except WebSocketDisconnect:
#             print("Client disconnected")

