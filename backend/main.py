import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, Request
from pydantic import BaseModel
import clickhouse_connect
from fastapi.middleware.cors import CORSMiddleware
from fastapi_keycloak_middleware import (
    FastApiUser,
    KeycloakConfiguration,
    setup_keycloak_middleware,
    get_user,
)
import psycopg2

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "admin")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")


keycloak_config = KeycloakConfiguration(
    url="http://keycloak:8080",
    realm="reports-realm",            
    client_id="reports-api",
    claims=["sub", "name", "email", "given_name", "family_name"],
    reject_on_missing_claim=False,
    email_claim="email"
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Device Analytics API")

class User(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None

async def custom_user_mapper(claims) -> Optional[User]:
    user_id = claims.get("sub")

    if not user_id:
        user_id = claims.get("client_id") 
        
    if not user_id:
        return None 

    return User(
        user_id=user_id,
        username=claims.get("given_name"),
        email=claims.get("email"),
    )

setup_keycloak_middleware(app, keycloak_configuration=keycloak_config, user_mapper=custom_user_mapper)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

try:
    ch_client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DB
    )
except Exception as e:
    print(f"Что-то пошло не так: {e}")
    ch_client = None

try:
    db_config = {
        "dbname": "crm_db",
        "user": "admin",
        "password": "admin",
        "host": "crm_db",
        "port": "5432"
    }

    conn = psycopg2.connect(**db_config)
except Exception as e:
    logger.error(f"Что-то пошло не так: {e}")
    conn = None

@app.get("/reports")
def get_analytics_events(
    limit: int = Query(100, ge=1, le=1000, description="Кол-во строк"),
    user: User = Depends(get_user)
):
    email = user.email
    logger.info(f"user email: {email}")

    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT device_id FROM users WHERE email = '{email}' LIMIT 1;
            """)
            result = cur.fetchone()

            if not result:
                logger.info("no devices")
                return []

            logger.info(f"device_id: {result[0]}") 
            device_id = result[0]
            

    except Exception as e:
        logger.error(f"Что-то пошло не так: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Что-то пошло не так: {str(e)}")

    query = "SELECT device_id, window_start, avg_heart_rate FROM device_analytics.report_daily"
    parameters = {}

    query += " WHERE device_id = %(device_id)s ORDER BY window_start DESC LIMIT %(limit)s"
    parameters["device_id"] = device_id
    parameters["limit"] = limit

    try:
        result = ch_client.query(query, parameters=parameters)
        
        data = [
            dict(zip(result.column_names, row)) 
            for row in result.result_rows
        ]
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Что-то пошло не так: {str(e)}")