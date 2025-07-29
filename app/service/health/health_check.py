from datetime import datetime, timezone
from typing import Dict, Any
from app.util.pymysql_pool import db_pool
from app.config.logging_config import logger

def check_database_health() -> Dict[str, Any]:
    """Check database connectivity"""
    conn = db_pool.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return {
                "status": "healthy",
                # "response_time": "fast",
                "details": "Database connection successful"
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            # "response_time": "slow",
            "details": f"Database connection failed: {str(e)}"
        }
    finally:
        if conn:
            db_pool.return_connection(conn)

def check_application_health() -> Dict[str, Any]:
    """Check overall application health"""
    db_health = check_database_health()
    pool_health = db_pool.get_pool_status()
    overall_status = "healthy" if db_health["status"] == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "services": {
            "database": db_health,
            "connectionPool": pool_health
        }
    }