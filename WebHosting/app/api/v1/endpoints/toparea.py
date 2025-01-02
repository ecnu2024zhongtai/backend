from fastapi import APIRouter
from app.services.topkarea_service import getClustersByGrahamScanService
from app.services.topkarea_service import getCurrentRoads
from app.services.topkarea_service import searchClustersByEuclideanDistance
from app.services.topkarea_service import selectbestpath

router = APIRouter()

#.\env\scripts\uvicorn app.main:app --reload


#�õ���ͬʱ��ε������ؿ���
@router.get("/topkarea/")
async def getClustersByGrahamScan(time:int):
    clusters = await getClustersByGrahamScanService(time)
    return clusters

#�õ�ʵʱ��ͨ����
@router.get("/getRoads/")
async def getRoads():
    return await getCurrentRoads()

#���ݾ�γ�Ȼ�ȡ������������
@router.get("/searchtopkarea/")
async def searchtopkarea(lat:float,lng:float):
    return await searchClustersByEuclideanDistance(lat,lng)

#·���滮    
@router.get("/sendtopkarea/")
async def sendtopkarea(lat:float,lng:float):
    return await selectbestpath(lat,lng)
