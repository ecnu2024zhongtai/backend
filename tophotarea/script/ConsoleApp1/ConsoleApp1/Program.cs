using System;
using System.Collections.Generic;
using System.Linq;
using MongoDB.Bson;
using MongoDB.Driver;
using ClickHouse.Client.ADO;
using ClickHouse.Client.Formats;
using ClickHouse.Client;
using System.Collections;
using ClickHouse.Client.Utility;
using ConsoleApp1;
using Npgsql;

/// <summary>
/// DBSCAN聚类逻辑
/// </summary>
class Program
{

    public static void Main(string[] args)
    {
        // 数据库连接字符串
        string connString = "XXX";

        using (var conn = new NpgsqlConnection(connString))
        {
            conn.Open();

            var cmd = new NpgsqlCommand(
    "SELECT longitude, latitude, starttime FROM public.topkarea WHERE longitude is not null", conn);
            var reader = cmd.ExecuteReader();

            var points = new List<Point>();
            while (reader.Read())
            {
                double longitude = reader.GetDouble(0);
                double latitude = reader.GetDouble(1);
                DateTime startTime = reader.GetDateTime(2);

                int time = startTime.Hour; // 按小时分片，忽略年月日
                points.Add(new Point { Longitude = longitude, Latitude = latitude, Time = time });
            }
            reader.Close();

            // DBSCAN 参数
            int minPts = 20;
            double epsilonTemporal = 1; // 时间阈值（单位：小时）
            double epsilonSpatial = 0.15; // 空间距离阈值（单位：公里）

            var times=points.Select(c=>c.Time).Distinct().ToList();

            foreach (var ti in times)
            {
                Console.WriteLine($"{ti}聚类开始！");
                var pointstt = points.Where(c => c.Time == ti).ToList();

                // 执行 DBSCAN 聚类
                var clusteredPoints = DBSCAN.PerformDBSCAN(pointstt, minPts, epsilonTemporal, epsilonSpatial);

                    // 插入聚类结果
                    foreach (var point in clusteredPoints)
                    {
                        cmd = new NpgsqlCommand(@"
                        INSERT INTO topkarea_clusters (longitude, latitude, time, clusterID, isNoised)
                        VALUES (@longitude, @latitude, @time, @clusterID, @isNoised);
                    ", conn);

                        cmd.Parameters.AddWithValue("longitude", point.Longitude);
                        cmd.Parameters.AddWithValue("latitude", point.Latitude);
                        cmd.Parameters.AddWithValue("time", point.Time);
                        cmd.Parameters.AddWithValue("clusterID", point.ClusterID);
                        cmd.Parameters.AddWithValue("isNoised", point.IsNoised);
                        cmd.ExecuteNonQuery();
                    }

                Console.WriteLine($"{ti}聚类结果已成功存储到 PostgreSQL 的新表 topkarea_clusters 中！");

            }

 
        }
    }
}


public class Point
{
    public double Longitude { get; set; }
    public double Latitude { get; set; }
    public int Time { get; set; } // 时间（小时）
    public int ClusterID { get; set; } = 0;
    public bool IsVisited { get; set; } = false;
    public bool IsNoised { get; set; } = false;
}

public class DBSCAN
{
    private const double EarthRadius = 6370.99681; // 地球半径（公里）

    // 计算球面距离
    public static double HaversineDistance(Point point1, Point point2)
    {
        double lat1 = DegreesToRadians(point1.Latitude);
        double lon1 = DegreesToRadians(point1.Longitude);
        double lat2 = DegreesToRadians(point2.Latitude);
        double lon2 = DegreesToRadians(point2.Longitude);

        return EarthRadius * Math.Acos(
            Math.Sin(lat1) * Math.Sin(lat2) +
            Math.Cos(lat1) * Math.Cos(lat2) * Math.Cos(lon1 - lon2)
        );
    }

    private static double DegreesToRadians(double degrees)
    {
        return degrees * Math.PI / 180.0;
    }

    // 查找邻域点
    public static List<Point> FindNeighbors(Point point, List<Point> pointsList, double epsilonTemporal, double epsilonSpatial)
    {
        return pointsList.Where(otherPoint =>
            Math.Abs(point.Time - otherPoint.Time) <= epsilonTemporal &&
            HaversineDistance(point, otherPoint) <= epsilonSpatial).ToList();
    }

    // DBSCAN 聚类算法
    public static List<Point> PerformDBSCAN(List<Point> pointsList, int minPts, double epsilonTemporal, double epsilonSpatial)
    {
        int clusterID = 1;

        foreach (var point in pointsList)
        {
            if (point.IsVisited) continue;

            point.IsVisited = true;
            var neighbors = FindNeighbors(point, pointsList, epsilonTemporal, epsilonSpatial);

            if (neighbors.Count < minPts)
            {
                point.IsNoised = true;
            }
            else
            {
                point.ClusterID = clusterID;
                for (int i = 0; i < neighbors.Count; i++)
                {
                    var neighbor = neighbors[i];
                    if (!neighbor.IsVisited)
                    {
                        neighbor.IsVisited = true;
                        var newNeighbors = FindNeighbors(neighbor, pointsList, epsilonTemporal, epsilonSpatial);
                        if (newNeighbors.Count >= minPts)
                        {
                            neighbors.AddRange(newNeighbors); // 这里不会抛出异常
                        }
                    }

                    if (neighbor.ClusterID == 0)
                    {
                        neighbor.ClusterID = clusterID;
                        if (neighbor.IsNoised) neighbor.IsNoised = false;
                    }
                }
                clusterID++;
            }
        }

        return pointsList;
    }
}