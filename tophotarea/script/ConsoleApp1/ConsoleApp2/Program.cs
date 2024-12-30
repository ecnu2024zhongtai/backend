using System;
using System.Collections.Generic;
using System.Linq;
using System.Data;
using Npgsql;

/// <summary>
/// 计算簇点的中心点
/// </summary>
class Program
{
    static string connectionString = "XXX";

    static void Main()
    {
        // 获取每组的经纬度数据并计算中心点
        var data = GetData();
        var centerPoints = CalculateCenterPoints(data);
        InsertCenterPoints(centerPoints);
    }

    // 获取数据并按 time 和 clusterid 分组
    static List<GroupData> GetData()
    {
        List<GroupData> data = new List<GroupData>();

        using (var connection = new NpgsqlConnection(connectionString))
        {
            connection.Open();

            var query = "SELECT time, clusterid, longitude, latitude FROM public.topkarea_graham";
            using (var cmd = new NpgsqlCommand(query, connection))
            using (var reader = cmd.ExecuteReader())
            {
                while (reader.Read())
                {
                    data.Add(new GroupData
                    {
                        Time = reader.GetInt32(0),
                        ClusterId = reader.GetInt32(1),
                        Longitude = reader.GetDouble(2),
                        Latitude = reader.GetDouble(3)
                    });
                }
            }
        }

        return data;
    }

    // 按 time 和 clusterid 分组，并计算每组的中心点
    static List<CenterPoint> CalculateCenterPoints(List<GroupData> data)
    {
        var groupedData = data.GroupBy(d => new { d.Time, d.ClusterId });

        List<CenterPoint> centerPoints = new List<CenterPoint>();

        foreach (var group in groupedData)
        {
            double avgLongitude = group.Average(g => g.Longitude);
            double avgLatitude = group.Average(g => g.Latitude);

            centerPoints.Add(new CenterPoint
            {
                Time = group.Key.Time,
                ClusterId = group.Key.ClusterId,
                CenterLongitude = avgLongitude,
                CenterLatitude = avgLatitude
            });
        }

        return centerPoints;
    }

    // 将计算出的中心点插入 topkarea_graham_center 表
    static void InsertCenterPoints(List<CenterPoint> centerPoints)
    {
        using (var connection = new NpgsqlConnection(connectionString))
        {
            connection.Open();

            foreach (var point in centerPoints)
            {
                var query = @"
                    INSERT INTO public.topkarea_graham_center (time, clusterid, longitude, latitude)
                    VALUES (@time, @clusterid, @longitude, @latitude)";
                using (var cmd = new NpgsqlCommand(query, connection))
                {
                    cmd.Parameters.AddWithValue("time", point.Time);
                    cmd.Parameters.AddWithValue("clusterid", point.ClusterId);
                    cmd.Parameters.AddWithValue("longitude", point.CenterLongitude);
                    cmd.Parameters.AddWithValue("latitude", point.CenterLatitude);

                    cmd.ExecuteNonQuery();
                }
            }
        }
    }
}

// 存储每条数据
public class GroupData
{
    public int Time { get; set; }
    public int ClusterId { get; set; }
    public double Longitude { get; set; }
    public double Latitude { get; set; }
}

// 存储计算出的中心点
public class CenterPoint
{
    public int Time { get; set; }
    public int ClusterId { get; set; }
    public double CenterLongitude { get; set; }
    public double CenterLatitude { get; set; }
}
