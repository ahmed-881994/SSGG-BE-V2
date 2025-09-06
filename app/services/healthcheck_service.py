from datetime import datetime
from logging import getLogger
from time import time

import pytz
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine, get_db

logger = getLogger(__name__)

class HealthCheckService:
    
    def __init__(self):
        # Set Egypt timezone with automatic daylight saving handling
        self.egypt_tz = pytz.timezone('Africa/Cairo')
    
    def get_egypt_time(self):
        """Get current time in Egypt timezone with DST handling"""
        utc_now = datetime.now(pytz.UTC)
        return utc_now.astimezone(self.egypt_tz)
    
    def check_database(self):
        """Check database connectivity and responsiveness."""
        logger.info("Checking database health...")
        statement = "SELECT COUNT(*) FROM SSGG.members"
        start_time = time()
        try:
            db = next(get_db())
            result = db.execute(text(statement)).scalar()
            response_time = round((time() - start_time) * 1000, 2)
            logger.info("Database is healthy.")
            return {
                "service_name": "Database Connectivity",
                "status": "healthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "performance": {
                    "response_time_ms": response_time,
                    "query_executed": statement,
                    "table_count": result
                },
                "connection_info": {
                    "engine_url": str(engine.url).split('@')[0] + '@[REDACTED]',
                    "dialect": engine.dialect.name,
                    "driver": engine.dialect.driver
                },
                "message": "Database connection established successfully",
                "details": {
                    "description": "Successfully connected to database and executed test query",
                    "severity": "info"
                }
            }
        except SQLAlchemyError as e:
            response_time = round((time() - start_time) * 1000, 2)
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "service_name": "Database Connectivity",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "performance": {
                    "response_time_ms": response_time,
                    "query_executed": statement,
                    "query_failed": True
                },
                "error": {
                    "type": "SQLAlchemyError",
                    "message": str(e),
                    "category": "database_connection"
                },
                "message": "Database connection failed",
                "details": {
                    "description": f"Failed to establish database connection: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Check database server status and connection credentials"
                }
            }
        except Exception as e:
            response_time = round((time() - start_time) * 1000, 2)
            logger.error(f"Unexpected error in database health check: {str(e)}")
            return {
                "service_name": "Database Connectivity",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "performance": {
                    "response_time_ms": response_time,
                    "query_executed": statement,
                    "query_failed": True
                },
                "error": {
                    "type": "UnexpectedError",
                    "message": str(e),
                    "category": "system_error"
                },
                "message": "Unexpected error during database health check",
                "details": {
                    "description": f"An unexpected error occurred: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Review application logs and system resources"
                }
            }
        finally:
            if 'db' in locals():
                db.close()
                
    def check_connection_pool(self):
        """Check connection pool status"""
        logger.info("Checking connection pool health...")
        start_time = time()
        try:
            pool = engine.pool
            
            # Get the pool status string
            pool_status_str = str(pool.status())
            # Example: "Pool size: 10  Connections in pool: 1 Current Overflow: -9 Current Checked out connections: 0"
            
            # Parse the string to extract values
            import re

            # Extract values using regex
            pool_size_match = re.search(r'Pool size: (\d+)', pool_status_str)
            connections_in_pool_match = re.search(r'Connections in pool: (\d+)', pool_status_str)
            overflow_match = re.search(r'Current Overflow: (-?\d+)', pool_status_str)
            checked_out_match = re.search(r'Current Checked out connections: (\d+)', pool_status_str)
            
            pool_size = int(pool_size_match.group(1)) if pool_size_match else 0
            connections_in_pool = int(connections_in_pool_match.group(1)) if connections_in_pool_match else 0
            overflow = int(overflow_match.group(1)) if overflow_match else 0
            checked_out = int(checked_out_match.group(1)) if checked_out_match else 0
            
            # Calculate checked in connections (total in pool - checked out)
            checked_in = connections_in_pool
            
            # Calculate utilization percentage
            utilization = (checked_out / pool_size * 100) if pool_size > 0 else 0
            
            # Determine status based on utilization
            if utilization > 80:
                status = "warning"
                message = "Connection pool usage is critically high"
                severity = "warning"
                recommendation = "Consider increasing pool size or optimizing connection usage"
            elif utilization > 60:
                status = "warning"
                message = "Connection pool usage is moderately high"
                severity = "warning"
                recommendation = "Monitor connection usage patterns"
            else:
                status = "healthy"
                message = "Connection pool is operating within normal parameters"
                severity = "info"
                recommendation = "No action required"
            response_time = round((time() - start_time) * 1000, 2)
            logger.info("Database connection pool health check completed.")
            return {
                "service_name": "Database Connection Pool",
                "status": status,
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": response_time,
                "pool_configuration": {
                    "max_pool_size": pool_size,
                    "pool_timeout": getattr(pool, '_timeout', 'N/A'),
                    "max_overflow": getattr(pool, '_max_overflow', 'N/A'),
                    "pool_recycle": getattr(pool, '_recycle', 'N/A')
                },
                "current_metrics": {
                    "total_connections_created": connections_in_pool,
                    "available_connections": checked_in,
                    "active_connections": checked_out,
                    "overflow_connections": overflow,
                    "utilization_percentage": round(utilization, 2)
                },
                "capacity_analysis": {
                    "is_near_capacity": utilization > 80,
                    "available_capacity": pool_size - checked_out,
                    "capacity_utilization": f"{checked_out}/{pool_size}",
                    "overflow_available": overflow < 0
                },
                "message": message,
                "details": {
                    "description": f"Pool utilization at {utilization:.1f}% ({checked_out}/{pool_size} connections)",
                    "severity": severity,
                    "recommendation": recommendation,
                    "raw_pool_status": pool_status_str
                }
            }
            
        except Exception as e:
            logger.error(f"Pool health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "details": f"Pool check failed: {str(e)}"
            }

    def check_database_schema_health(self):
        """Check if required database tables exist"""
        logger.info("Checking database schema health...")
        start_time = time()
        try:
            db = next(get_db())
            inspector = inspect(engine)
            
            # Define your critical tables here
            required_tables = [
                "users",           # System users
                "event_types",     # Event type classifications
                "events",          # Events and activities
                "entity_types",    # Entity type classifications
                "entity_roles",    # Roles within entities
                "entities",       # Organizational units
                "members",        # Member information
                "entity_members", # Entity-member relationships
                "attendance_states", # Attendance status types
                "attendance",      # Attendance records
                "event_entities"     # Event-entity relationships
            ]
            
            existing_tables = inspector.get_table_names()
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logger.error(f"Missing required tables: {', '.join(missing_tables)}")
                response_time = round((time() - start_time) * 1000, 2)
                return {
                    "service_name": "Database Schema",
                    "status": "unhealthy",
                    "timestamp": self.get_egypt_time().isoformat(),
                    "response_time_ms": response_time,
                    "table_count": len(existing_tables),
                    "required_tables": required_tables,
                    "details": f"Missing required tables: {', '.join(missing_tables)}",
                    "existing_tables": len(existing_tables),
                    "missing_tables": missing_tables
                }
            response_time = round((time() - start_time) * 1000, 2)
            logger.info("Database schema is healthy.")
            
            return {
                "service_name": "Database Schema",
                "status": "healthy",
                "response_time_ms": response_time,
                "timestamp": self.get_egypt_time().isoformat(),
                "details": "All required database tables exist",
                "table_count": len(existing_tables),
                "required_tables": required_tables
            }
            
        except Exception as e:
            logger.error(f"Schema health check failed: {str(e)}")
            return {
                "service_name": "Database Schema",
                "status": "unhealthy",
                "details": f"Schema check failed: {str(e)}"
            }
        finally:
            if 'db' in locals():
                db.close()

    def check_health(self, summary_only=False):
        """Check overall application health using SQLAlchemy"""
        logger.info("Checking overall application health...")
        start_time = time()
        
        # Run all health checks
        db_health = self.check_database()
        pool_health = self.check_connection_pool()
        db_schema_health = self.check_database_schema_health()
        
        # Determine overall status
        all_services = [db_health, pool_health, db_schema_health]
        unhealthy_services = [s for s in all_services if s["status"] == "unhealthy"]
        warning_services = [s for s in all_services if s["status"] == "warning"]
        
        if unhealthy_services:
            overall_status = "unhealthy"
        elif warning_services:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        total_response_time = round((time() - start_time) * 1000, 2)

        if summary_only:
            return {
                "status": overall_status,
                "timestamp": self.get_egypt_time().isoformat(),
                "version": "2.0.0",
                "response_time_ms": total_response_time,
            }

        return {
            "status": overall_status,
            "timestamp": self.get_egypt_time().isoformat(),
            "version": "2.0.0",
            "response_time_ms": total_response_time,
            # "database": {
            #     "engine": str(engine.url).split('@')[0] + '@[REDACTED]',  # Hide credentials
            #     "dialect": engine.dialect.name
            # },
            "summary": {
                "total_services": len(all_services),
                "healthy_services": len([s for s in all_services if s["status"] == "healthy"]),
                "warning_services": len(warning_services),
                "unhealthy_services": len(unhealthy_services)
            },
            "services": {
                "database_connectivity": db_health,
                "connection_pool": pool_health,
                "database_schema": db_schema_health,
                # "environment": env_health
            }
        }