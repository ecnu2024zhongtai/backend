class TopkAreaClusters_ByGrahamScan:
    def __init__(self,id:int,longitude:float,latitude:float,time:int,clusterid:int):
        self.id=id
        self.longitude=longitude
        self.latitude=latitude
        self.time=time
        self.clusterid = clusterid
    


class Roads:
    def __init__(self,roadid:int,longitude:float,latitude:float,seq:int,orientation:str,status:str):
        self.roadid=roadid
        self.longitude=longitude
        self.latitude=latitude
        self.seq=seq
        self.orientation = orientation
        self.status=status
        self.flag=f"{roadid}_{seq}"
        #self.weight = self.get_weight(status)

    def getflag(self,roadid,seq):
        return f"{roadid}_{seq}"

    def get_weight(self):
        if self.status == 'red':
            return 4  # ӵ��
        elif self.status == 'hotpink':
            return 3  # �е�ӵ��
        elif self.status == 'yellow':
            return 2  # ��Щ��
        else:
            return 1  # ͨ��

    def __repr__(self):
        return f"{{'roadid': {self.roadid}, 'longitude': {self.longitude}, 'latitude': {self.latitude}, 'seq': {self.seq}, 'flag': '{self.orientation}', 'status': '{self.status}'}}"


class Graph:
    def __init__(self):
        self.adj_list = {}

    def add_edge(self, start, end, weight):
        if start not in self.adj_list:
            self.adj_list[start] = []
        self.adj_list[start].append((end, weight))

    def get_neighbors(self, node):
        return self.adj_list.get(node, [])

