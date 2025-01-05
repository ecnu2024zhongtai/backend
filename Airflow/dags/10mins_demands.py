from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='10mins_demands',
    default_args=default_args,
    schedule_interval='*/1 * * * *',  # 每分钟执行一次
    catchup=False,
    tags=['redis', 'api'],
) as dag:
    load_to_redis = HttpOperator(
        task_id='10mins_demands_to_redis',
        http_conn_id='realtime_origin_trips',  # 使用上面配置的 Conn Id
        endpoint='/api/v1/demands/last10mins/loadtoredis',  # 接口的路径部分
        method='GET',  # 或 'POST'，根据你的 API 要求
        log_response=True,  # 记录 API 响应，方便调试
        response_filter=lambda response: response.text, # 可选：处理API响应，例如获取文本
        # extra_options={"verify": False} # 如果是自签名证书或测试环境，可以添加此项，生产环境不建议
    )