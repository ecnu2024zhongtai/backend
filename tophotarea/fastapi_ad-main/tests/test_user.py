
import sys
import os
# 将项目根目录加入到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

#from app.services.topkarea_service import getClustersByGrahamScanService

#def test_get_clusters_by_graham_scan_service():
#    clusters = getClustersByGrahamScanService()


#test_get_clusters_by_graham_scan_service()


from app.services.topkarea_service import selectbestpath

selectbestpath(45.76637,126.67251)