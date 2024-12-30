using MongoDB.Bson;
using MongoDB.Driver;
using Npgsql;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace ConsoleApp1
{
    //把上客所在道路的经纬度提取出来，并将时间戳进行转化
    public class MangoDBToPG
    {
        public  void PG()
        {
            // MongoDB 连接设置
            string mongoConnectionString = "XXX";
            string databaseName = "harbintrips";
            var client = new MongoClient(mongoConnectionString);
            var database = client.GetDatabase(databaseName);

            // PostgreSQL 连接设置
            string pgConnectionString = "XXX";

            // MongoDB 和 PostgreSQL 的表名
            var tableNames = new List<string> { "trips2_06" }; // MongoDB 集合名
            var pgTableNames = new List<string> { "topkarea" }; // PostgreSQL 表名

            using var pgConnection = new NpgsqlConnection(pgConnectionString);
            pgConnection.Open();

            int batchSize = 1000;
            int index = 0;

            foreach (var tableName in tableNames)
            {
                Console.WriteLine($"{tableName} 开始导入...");

                var collection = database.GetCollection<BsonDocument>(tableName);
                int skip = 0, totalInserted = 0;

                while (true)
                {
                    // 分批获取 MongoDB 数据
                    var documents = collection.Find(Builders<BsonDocument>.Filter.Empty)
                                              .Skip(skip)
                                              .Limit(batchSize)
                                              .ToList();

                    if (documents.Count == 0)
                    {
                        Console.WriteLine($"{tableName} 全部数据导入完成.");
                        break;
                    }

                    // 构建批量插入数据
                    var insertValues = new List<string>();

                    foreach (var doc in documents)
                    {
                        // 提取 devid
                        var devid = doc.Contains("devid") ? doc["devid"].AsInt64.ToString() : "NULL";

                        // 提取 timestamp 的第一条数据，并转换为 yyyy-MM-dd HH:mm:ss
                        var timestampList = doc.Contains("timestamp")
                            ? doc["timestamp"].AsBsonArray.Select(val => val.ToString()).ToList()
                            : new List<string>();

                        var timestamp = timestampList.Count > 0
                            ? ConvertUnixToDateTimeWithOffset(timestampList.First())
                            : "NULL";

                        var endtime= timestampList.Count > 0
                            ? ConvertUnixToDateTimeWithOffset(timestampList.Last())
                            : "NULL";

                        var longitude = "NULL";
                        var latitude = "NULL";

                        var endlongitude = "NULL";
                        var endlatitude = "NULL";
                        if (doc.Contains("route_geom"))
                        {
                            var routeGeomList = doc["route_geom"].AsBsonArray
                                .Select(val => val.ToString()).ToList();

                            if (routeGeomList.Count > 0)
                            {
                                // 提取坐标，例如 "LINESTRING (126.6588695 45.7528896, ...)"
                                var match = Regex.Match(routeGeomList.First(), @"LINESTRING\s*\(\s*([\d\.\-]+)\s+([\d\.\-]+)");
                                if (match.Success)
                                {
                                    longitude = match.Groups[1].Value;
                                    latitude = match.Groups[2].Value;
                                }

                                var endmatch = Regex.Match(routeGeomList.Last(), @"LINESTRING\s*\((.*)\)");
                                if (endmatch.Success)
                                {
                                    var coordinates = endmatch.Groups[1].Value;
                                    // 拆分坐标成单独的点
                                    var points = coordinates.Split(',');

                                    // 提取最后一组经度和纬度
                                    var lastPoint = points[points.Length - 1].Trim(); // 获取最后一个坐标
                                    var lastPointMatch = Regex.Match(lastPoint, @"([\-]?\d+\.\d+)\s+([\-]?\d+\.\d+)");

                                    if (lastPointMatch.Success)
                                    {
                                         endlongitude = lastPointMatch.Groups[1].Value; // 经度
                                         endlatitude = lastPointMatch.Groups[2].Value;  // 纬度

                                      //  Console.WriteLine($"Last Longitude: {longitude}, Last Latitude: {latitude}");
                                    }
                                }
                            }
                        }


                        //"[LINESTRING (126.6588695 45.7528896, 126.6587634 45.751689)]"
                        // 处理字符串的单引号转义


                        // 构造插入数据
                        string value = $"('{timestamp}','{endtime}', {devid}, {longitude}, {latitude},{endlongitude},{endlatitude})";
                        insertValues.Add(value);

                    }

                    // 执行 PostgreSQL 批量插入
                    string insertQuery = $@"
                    INSERT INTO {pgTableNames[index]} (starttime,endtime,devid,longitude,latitude,endlongitude,endlatitude) 
                    VALUES {string.Join(",", insertValues)};";

                    using var pgCommand = new NpgsqlCommand(insertQuery, pgConnection);
                    pgCommand.ExecuteNonQuery();

                    // 日志输出
                    totalInserted += documents.Count;
                    Console.WriteLine($"{documents.Count} 条记录已插入, 累计: {totalInserted} 条.");

                    skip += batchSize;
                }

                index++;
                Console.WriteLine($"{tableName} 数据导入完成.");
            }

            Console.WriteLine("所有数据导入完成.");
        }

        private string ConvertUnixToDateTimeWithOffset(string unixTime)
        {
            if (long.TryParse(unixTime, out long timestamp))
            {
                var dateTime = DateTimeOffset.FromUnixTimeSeconds(timestamp)
                                             .ToOffset(TimeSpan.FromHours(8)) // 加8小时
                                             .DateTime;
                return dateTime.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture);
            }
            return "NULL";
        }
    }
}
