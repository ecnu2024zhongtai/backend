# 项目简介
该项目是出租车调度系统，用户可以通过网页输入经纬度来模拟定位用户所在的位置来请求最近的出租车，并在地图上显示出租车（红色标记）到用户（蓝色标记）所在位置的路线。

## 使用方法
用户可以在taxi.html页面输入经纬度，并点击“Taxi”按钮请求最近的出租车。地图上会显示用户位置和出租车的路线。

## 主要功能
利用历史出租车下客经纬度数据，在时间上进行匹配，将返回的数据用geopandas处理成几何点，便用使用R树获取附近的司机位置。

![R树(a)](https://github.com/user-attachments/assets/2239bca7-b8cf-4d89-89de-4f6787fdffa1)


使用haversine公式计算两个经纬度之间的距离，选取最近的司机。

![haversine](https://github.com/user-attachments/assets/ed8a408f-08de-4e5e-8d05-c707eb489ad7)

基于 高德地图API-驾车路径规划 获取从司机到用户位置的路线。

## 例子
![taxi example](https://github.com/user-attachments/assets/6a721979-0b63-45a8-9e64-420c4c293124)
