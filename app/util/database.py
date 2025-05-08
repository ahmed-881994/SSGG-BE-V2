from fastapi import HTTPException
import pymysql.cursors
import os
def connect():
    try:
        # Connect to the database
        cursor = pymysql.cursors.DictCursor
        conn = pymysql.connect(
            host=os.environ.get("host"),
            port=int(os.environ["port"]),
            database=os.environ["database"],
            user=os.environ["username"],
            password=os.environ["password"],
            cursorclass=cursor,
        )
    except Exception as error:
        conn = None
        raise HTTPException(status_code=500, detail=error.args)
    return conn