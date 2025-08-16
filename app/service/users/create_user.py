from app.config.logging_config import logger
from app.core.exceptions import ServiceError
from app.schema.users.create_user import CreateUserRequest
from app.util.password import generate_salt, get_password_hash
from app.core.database_connection_pool import db_pool


def create_user_db(user: CreateUserRequest):
    """Create a new user in the database."""
    conn = db_pool.get_connection()
    if conn is None:
        logger.error(
            "Failed to get database connection for user retrieval")
        raise ServiceError(
            message="Database connection error", name="Database Error")
    try:
        salt = generate_salt()
        hashed_password, _ = get_password_hash(user.password, salt)
        
        with conn.cursor() as cursor:
            cursor.callproc("CreateUser", [user.user_name, user.user_id, hashed_password, user.user_type, salt])
            conn.commit()
            return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise ServiceError(message="Error creating user", name="Database Error")
    finally:
        db_pool.return_connection(conn)