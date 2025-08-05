from contextlib import contextmanager
from fastapi import HTTPException
import pymysql.cursors
import os

from app.config.settings import settings
from app.util.pymysql_pool import db_pool



@contextmanager
def get_connection():
    """Get a database connection from the pool"""
    conn = None
    try:
        conn = db_pool.get_connection()
        yield conn
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Database error: {str(error)}")
    finally:
        if conn:
            db_pool.return_connection(conn)

# def connect():
#     try:
#         # Connect to the database
#         cursor = pymysql.cursors.DictCursor
#         conn = pymysql.connect(
#             host=settings.db_host,
#             port=int(settings.db_port),
#             database=settings.db_database,
#             user=settings.db_username,
#             password=settings.db_password,
#             cursorclass=cursor,
#         )
#     except Exception as error:
#         conn = None
#         raise HTTPException(status_code=500, detail=error.args)
#     return conn