import os
import re
from datetime import datetime
from logging import getLogger
from time import time

import pytz
import redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import settings
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
        statement = f"SELECT COUNT(*) FROM {settings.db_database}.members"
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
                    "severity": "info",
                    "troubleshooting": "No action required"
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
                "service_name": "Database Connection Pool",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": round((time() - start_time) * 1000, 2),
                "message": "Connection pool health check failed",
                "error": {
                    "type": "UnexpectedError",
                    "message": str(e),
                    "category": "system_error"
                },
                "details": {
                    "description": f"Pool check failed: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Review application logs and system resources"
                }
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
                "attendance",      # Attendance records
                "attendance_states", # Attendance status types
                "entities",       # Organizational units
                "entity_members", # Entity-member relationships
                "entity_roles",    # Roles within entities
                "entity_types",    # Entity type classifications
                "event_entities",   # Event-entity relationships
                "event_types",     # Event type classifications
                "events",          # Events and activities
                "lookups",         # Lookup/reference data
                "members",        # Member information
                "users",           # System users
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
                    "required_tables_count": len(required_tables),
                    "required_tables": required_tables,
                    "existing_table_count": len(existing_tables),
                    "existing_tables": existing_tables,
                    "missing_tables": missing_tables,
                    "extra_tables": [table for table in existing_tables if table not in required_tables],
                    "details": {
                        "description": f"Missing required tables: {', '.join(missing_tables)}",
                        "severity": "critical",
                        "troubleshooting": "Review database schema and migrations"
                    }
                }
            response_time = round((time() - start_time) * 1000, 2)
            logger.info("Database schema is healthy.")
            
            return {
                "service_name": "Database Schema",
                "status": "healthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": response_time,
                "required_tables_count": len(required_tables),
                "required_tables": required_tables,
                "existing_table_count": len(existing_tables),
                "existing_tables": existing_tables,
                "extra_tables": [table for table in existing_tables if table not in required_tables],
                "details": {
                    "description": "All required database tables exist",
                    "severity": "info",
                    "troubleshooting": "No action required"
                }
            }
            
        except Exception as e:
            logger.error(f"Schema health check failed: {str(e)}")
            return {
                "service_name": "Database Schema",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": round((time() - start_time) * 1000, 2),
                "message": "Database schema health check failed",
                "error": {
                    "type": "UnexpectedError",
                    "message": str(e),
                    "category": "system_error"
                },
                "details": {
                    "description": f"Schema check failed: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Review application logs and database connectivity"
                }
            }
        finally:
            if 'db' in locals():
                db.close()

    def check_environment_health(self):
        """Check environment configuration"""
        logger.info("Checking environment health...")
        start_time = time()
        try:
            required_env_vars = [
                'environment',
                'db_host',
                'db_port',
                'db_database',
                'db_username',
                'db_password',
                'db_max_connections',
                'db_min_connections',
                'rds_host',
                'rds_port',
                'rds_database',
                'secret_key',
                'algorithm',
                'access_token_expires_minutes',
                'cors_origins',
                'rate_limit_per_minute',
                'log_level'
            ]
            missing_vars = [var for var in required_env_vars if not os.getenv(var)]
            
            if missing_vars:
                return {
                    "service_name": "Environment Configuration",
                    "status": "unhealthy",
                    "timestamp": self.get_egypt_time().isoformat(),
                    "response_time_ms": round((time() - start_time) * 1000, 2),
                    "environment": os.getenv("environment", "unknown"),
                    "details": {
                        "description": f"Missing environment variables: {', '.join(missing_vars)}",
                        "severity": "critical",
                        "troubleshooting": "Review application logs and environment configuration"
                    }
                }
            
            return {
                "service_name": "Environment Configuration",
                "status": "healthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": round((time() - start_time) * 1000, 2),
                "environment": os.getenv("environment", "unknown"),
                "details": {
                    "description": "All required environment variables are set",
                    "severity": "info",
                    "troubleshooting": "No action required"
                }
            }
        except Exception as e:
            logger.error(f"Environment health check failed: {str(e)}")
            return {
                "service_name": "Environment Configuration",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": round((time() - start_time) * 1000, 2),
                "environment": os.getenv("environment", "unknown"),
                "message": "Environment health check failed",
                "error": {
                    "type": "UnexpectedError",
                    "message": str(e),
                    "category": "system_error"
                },
                "details": {
                    "description": f"Environment check failed: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Review application logs and environment configuration"
                }
            }

    async def check_redis_health(self):
        """Check Redis connectivity for token blacklisting"""
        logger.info("Checking Redis health...")
        start_time = time()
        try:
            # Get Redis connection details from settings
            redis_host = settings.rds_host
            redis_port = settings.rds_port
            redis_db = settings.rds_database
            # redis_password = settings.rds_password

            # Create Redis connection
            redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                # password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test basic connectivity
            redis_client.ping()
            
            # Test set/get operations for token blacklisting
            test_key = "health_check_test_token"
            test_value = f"test_{int(time())}"
            
            # Test SET operation
            redis_client.setex(test_key, 10, test_value)  # 10 seconds TTL
            
            # Test GET operation
            retrieved_value = redis_client.get(test_key)
            
            # Test DELETE operation
            redis_client.delete(test_key)
            
            # Get Redis info
            redis_info = redis_client.info()
            
            response_time = round((time() - start_time) * 1000, 2)
            logger.info("Redis is healthy.")
            
            return {
                "service_name": "Redis Token Blacklist",
                "status": "healthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": response_time,
                "connection_info": {
                    "host": redis_host,
                    "port": redis_port,
                    "database": redis_db,
                    "redis_version": redis_info.get('redis_version', 'unknown')
                },
                "performance_metrics": {
                    "connected_clients": redis_info.get('connected_clients', 0),
                    "used_memory_human": redis_info.get('used_memory_human', 'unknown'),
                    "total_commands_processed": redis_info.get('total_commands_processed', 0),
                    "keyspace_hits": redis_info.get('keyspace_hits', 0),
                    "keyspace_misses": redis_info.get('keyspace_misses', 0)
                },
                "test_operations": {
                    "ping_successful": True,
                    "set_operation": True,
                    "get_operation": retrieved_value == test_value,
                    "delete_operation": True
                },
                "message": "Redis connection and token blacklist operations working properly",
                "details": {
                    "description": "Successfully connected to Redis and performed token blacklist test operations",
                    "severity": "info",
                    "troubleshooting": "No action required"
                }
            }
            
        except RedisConnectionError as e:
            response_time = round((time() - start_time) * 1000, 2)
            logger.error(f"Redis connection failed: {str(e)}")
            return {
                "service_name": "Redis Token Blacklist",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": response_time,
                "connection_info": {
                    "host": redis_host,
                    "port": redis_port,
                    "database": redis_db
                },
                "error": {
                    "type": "RedisConnectionError",
                    "message": str(e),
                    "category": "redis_connection"
                },
                "message": "Redis connection failed",
                "details": {
                    "description": f"Failed to connect to Redis server: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Check Redis server status, network connectivity, and connection credentials"
                }
            }
            
        except RedisError as e:
            response_time = round((time() - start_time) * 1000, 2)
            logger.error(f"Redis operation failed: {str(e)}")
            return {
                "service_name": "Redis Token Blacklist",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": response_time,
                "connection_info": {
                    "host": redis_host,
                    "port": redis_port,
                    "database": redis_db
                },
                "error": {
                    "type": "RedisError",
                    "message": str(e),
                    "category": "redis_operation"
                },
                "message": "Redis operation failed",
                "details": {
                    "description": f"Redis operation error: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Check Redis server configuration and available memory"
                }
            }
            
        except Exception as e:
            response_time = round((time() - start_time) * 1000, 2)
            logger.error(f"Unexpected error in Redis health check: {str(e)}")
            return {
                "service_name": "Redis Token Blacklist",
                "status": "unhealthy",
                "timestamp": self.get_egypt_time().isoformat(),
                "response_time_ms": response_time,
                "error": {
                    "type": "UnexpectedError",
                    "message": str(e),
                    "category": "system_error"
                },
                "message": "Unexpected error during Redis health check",
                "details": {
                    "description": f"An unexpected error occurred: {str(e)}",
                    "severity": "critical",
                    "troubleshooting": "Review application logs and system resources"
                }
            }

    async def check_health(self, summary_only=False):
        """Check overall application health using SQLAlchemy"""
        logger.info("Checking overall application health...")
        start_time = time()
        
        # Run all health checks
        db_health = self.check_database()
        pool_health = self.check_connection_pool()
        db_schema_health = self.check_database_schema_health()
        env_health = self.check_environment_health()
        redis_health = await self.check_redis_health()

        # Determine overall status
        all_services = [db_health, pool_health, db_schema_health, env_health, redis_health]
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
                "summary": {
                    "total_services": len(all_services),
                    "healthy_services": len([s for s in all_services if s["status"] == "healthy"]),
                    "warning_services": len(warning_services),
                    "unhealthy_services": len(unhealthy_services)
                }
            }

        return {
            "status": overall_status,
            "timestamp": self.get_egypt_time().isoformat(),
            "version": "2.0.0",
            "response_time_ms": total_response_time,
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
                "environment": env_health,
                "redis_token_blacklist": redis_health
            }
        }