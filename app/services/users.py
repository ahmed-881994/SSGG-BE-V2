"""
Consolidated user services
"""
from typing import List, Optional, Dict, Any
from app.core.exceptions import EntityDoesNotExistError
from app.core.config import logger
from app.core.database import get_connection
from app.core.database_connection_pool import db_pool
from app.schemas.users import User, UserCreate, UserUpdate, CreateUserRequest


def search_users_db(criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Search users based on criteria"""
    conn = db_pool.get_connection()
    
    try:
        with conn.cursor() as cursor:
            cursor.callproc("SearchUsers", [criteria])
            records = cursor.fetchall()
            users = [format_user_record(record) for record in records]
            return {
                "Users": users,
                "TotalCount": len(users)
            }
    finally:
        db_pool.return_connection(conn)


def create_user_db(user: CreateUserRequest) -> Dict[str, Any]:
    """Create a new user in the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        args = [
            user.username,
            user.email,
            user.password,
            user.is_active
        ]
        
        cursor.callproc("CreateUser", args)
        result = cursor.fetchone()
        return result


def update_user_db(user: UserUpdate) -> Dict[str, Any]:
    """Update an existing user in the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        args = [
            user.username,
            user.email,
            user.password,
            user.is_active
        ]
        
        cursor.callproc("UpdateUser", args)
        result = cursor.fetchone()
        return result


def delete_user_db(user_id: str) -> Dict[str, Any]:
    """Delete a user from the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.callproc("DeleteUser", [user_id])
        result = {"message": "User deleted successfully"}
        return result


def get_user_db(user_id: str) -> Dict[str, Any]:
    """Get user by ID from database"""
    conn = db_pool.get_connection()

    if conn is not None:
        try:
            with conn.cursor() as cursor:
                cursor.callproc("GetUser", [user_id])
                records = cursor.fetchall()
                if records is not None and len(records) > 0:
                    logger.info(f"Found {len(records)} records for user ID: {user_id}")
                    data = format_user_record(records[0])
                    return data
                else:
                    logger.info(f"No records found for user ID: {user_id}")
                    raise EntityDoesNotExistError(
                        message="No users found with the provided criteria.", name=None)
        finally:
            db_pool.return_connection(conn)
    else:
        raise EntityDoesNotExistError(
            message="Database connection failed.", name=None)


def format_user_record(record) -> Dict[str, Any]:
    """Format a single user record"""
    return {
        'UserID': record.get('UserID'),
        'Username': record.get('Username'),
        'Email': record.get('Email'),
        'IsActive': record.get('IsActive'),
        'LastLogin': record.get('LastLogin'),
        'CreatedAt': record.get('CreatedAt')
    }
