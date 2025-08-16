"""
Health check services for application monitoring
"""
from typing import Dict, Any
from app.core.config import logger
from app.core.database_connection_pool import db_pool


def check_application_health() -> Dict[str, Any]:
    """
    Comprehensive health check for the application
    
    Returns:
        Health status information
    """
    health_status = {
        "status": "healthy",
        "services": {},
        "timestamp": None
    }
    
    # Check database connection
    try:
        conn = db_pool.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    health_status["services"]["database"] = {
                        "status": "healthy",
                        "message": "Database connection successful"
                    }
                else:
                    health_status["services"]["database"] = {
                        "status": "unhealthy", 
                        "message": "Database query failed"
                    }
                    health_status["status"] = "unhealthy"
        finally:
            db_pool.return_connection(conn)
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Add timestamp
    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat()
    
    return health_status
