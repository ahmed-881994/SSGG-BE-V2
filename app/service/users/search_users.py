from typing import Optional

from app.config.logging_config import logger
from app.exceptions.exceptions import EntityDoesNotExistError, ServiceError
from app.schema.entities.search_entities import SearchEntitiesResponse
from app.util.pymysql_pool import db_pool


def search_users_db(user_name: Optional[str] = None, user_id: Optional[str] = None):
    conn = db_pool.get_connection()
    if conn is None:
        logger.error(
            "Failed to get database connection for user retrieval")
        raise ServiceError(
            message="Database connection error", name="Database Error")
    try:
        with conn.cursor() as cursor:
            cursor.callproc("SearchUsers", [user_name, user_id])
            records = cursor.fetchall()
            if records is None or len(records) == 0:
                raise EntityDoesNotExistError(
                    message="No users found with the provided criteria.", name=None)
            db_pool.return_connection(conn)
            users=[]
            for record in records:
                users.append({
                    'UserID': record.get('user_id'),
                    "UserName": record.get('user_name'),
                    "IsActive": record.get('is_active'),
                    "PasswordReset": record.get('password_reset'),
                    "UserType": record.get('user_type')
                })
            return {"Users": users}
    finally:
        db_pool.return_connection(conn)
