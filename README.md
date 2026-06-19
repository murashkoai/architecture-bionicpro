## Описание

1. Запускаем docker compose и дожидаемся запуск airflow scheduler:

  ```bash
  docker-compose up -d
  ```

  ![img3.png](./img/img3.png)

2. Переходим в airflow **http://localhost:8081** :

  При запуске airflow автоматически запускается DAG device_analytics_report_daily

  Строка подключения к ClickHouse указана в docker-compose.yaml
  - AIRFLOW_CONN_CLICKHOUSE_DEFAULT: 'clickhouse://admin:admin@clickhouse:9000/default'
  
  ![img2.png](./img/img2.png)

3. Переходим на страницу отчетов **http://localhost:3000**; вводим логин: **user1**, пароль: **password123**; нажимаем **Download Report**  :

  ![img1.png](./img/img1.png)
