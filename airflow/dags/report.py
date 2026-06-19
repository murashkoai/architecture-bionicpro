from datetime import datetime
from airflow import DAG
from airflow_clickhouse_plugin.operators.clickhouse import ClickHouseOperator

with DAG(
    dag_id="device_analytics_report_daily",
    start_date=datetime(2026, 6, 17),
    schedule="@daily",
    catchup=True,
) as dag:

    generate_report = ClickHouseOperator(
        task_id='postgres_pull',
        clickhouse_conn_id='clickhouse_default',
        sql="""
            INSERT INTO device_analytics.report_daily
            SELECT 
                device_id,
                DATE_TRUNC('day', reading_timestamp),
                AVG(heart_rate)
            FROM postgresql(
                'telemetry_db:5432', 'telemetry_db', 'telemetry', 'admin', 'admin'
            ) WHERE reading_timestamp::date = '{{ ds }}' GROUP BY device_id, DATE_TRUNC('day', reading_timestamp);
        """
    )

    generate_report