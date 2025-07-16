from fastapi import HTTPException
import pymysql.cursors
import os

from app.config.settings import settings
def connect():
    try:
        # Connect to the database
        cursor = pymysql.cursors.DictCursor
        conn = pymysql.connect(
            host=settings.db_host,
            port=int(settings.db_port),
            database=settings.db_database,
            user=settings.db_username,
            password=settings.db_password,
            cursorclass=cursor,
        )
    except Exception as error:
        conn = None
        raise HTTPException(status_code=500, detail=error.args)
    return conn