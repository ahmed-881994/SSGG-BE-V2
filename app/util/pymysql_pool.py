"""
PyMySQL Connection Pool Module

This module provides a thread-safe connection pooling mechanism for MySQL database
connections using PyMySQL. It manages a pool of database connections to improve
performance and resource utilization.

The connection pool features:
- Automatic connection creation and management
- Connection health monitoring and validation
- Thread-safe operations with proper locking
- Configurable pool size and initialization
- Retry logic for database connectivity issues
- Connection timeout and read/write timeout handling

Key Components:
- PyMySQLPool: Main connection pool class
- Global db_pool instance: Application-wide pool instance

Configuration:
- Pool size limits (min/max connections)
- Connection timeouts
- Retry logic parameters
- Database connection parameters

Thread Safety:
- Uses threading.Lock for thread-safe operations
- Queue-based connection management
- Atomic connection counting

Performance Features:
- Connection reuse to reduce overhead
- Health checks to ensure connection validity
- Automatic dead connection replacement
- Efficient connection allocation and return
"""

import pymysql
import pymysql.cursors
from queue import Queue, Empty
from threading import Lock
import time
from typing import Optional
from app.config.logging_config import logger
from app.config.settings import settings


class PyMySQLPool:
    """
    Thread-safe MySQL connection pool implementation.
    
    This class manages a pool of MySQL database connections, providing efficient
    connection reuse, health monitoring, and automatic connection recovery.
    
    Attributes:
        max_connections (int): Maximum number of connections in the pool
        min_connections (int): Minimum number of connections to maintain
        connection_pool (Queue): Thread-safe queue for available connections
        active_connections (int): Current number of active connections
        lock (Lock): Thread lock for atomic operations
        
    Example:
        # Create a pool with custom settings
        pool = PyMySQLPool(max_connections=50, min_connections=10)
        
        # Get a connection
        conn = pool.get_connection()
        try:
            # Use the connection
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        finally:
            # Return the connection to the pool
            pool.return_connection(conn)
    """
    
    def __init__(self, max_connections: int = 20, min_connections: int = 5):
        """
        Initialize the connection pool.
        
        Args:
            max_connections (int): Maximum number of connections in the pool
            min_connections (int): Minimum number of connections to maintain
            
        Raises:
            Exception: If pool initialization fails after all retries
        """
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_pool = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = Lock()
        
        logger.info(f"Initializing MySQL connection pool: max={max_connections}, min={min_connections}")
        
        # Initialize minimum connections with retry logic
        self._initialize_pool()

    def _initialize_pool(self, max_retries: int = 30, retry_delay: int = 5) -> None:
        """
        Initialize the connection pool with retry logic.
        
        This method creates the minimum number of connections required for the pool
        to function. It includes retry logic to handle temporary database connectivity
        issues during application startup.
        
        Args:
            max_retries (int): Maximum number of initialization attempts
            retry_delay (int): Delay between retry attempts in seconds
            
        Raises:
            Exception: If pool initialization fails after all retries
        """
        logger.info(f"Starting pool initialization with {self.min_connections} minimum connections")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to initialize database pool (attempt {attempt + 1}/{max_retries})")
                
                for i in range(self.min_connections):
                    try:
                        self.connection_pool.put_nowait(self._create_connection())
                        logger.debug(f"Created connection {i + 1}/{self.min_connections}")
                    except Exception as e:
                        logger.error(f"Failed to create connection {i + 1}: {str(e)}")
                        raise
                
                logger.info(f"Database pool initialized successfully. Active connections: {self.active_connections}")
                return
                
            except Exception as e:
                logger.warning(f"Failed to initialize database pool (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Failed to initialize database pool after all retries", exc_info=True)
                    raise Exception(f"Failed to initialize database pool after {max_retries} attempts: {str(e)}")
    
    def _create_connection(self) -> pymysql.Connection:
        """
        Create a new database connection.
        
        This method creates a new MySQL connection with the configured settings
        and adds it to the pool's active connection count.
        
        Returns:
            pymysql.Connection: A new database connection
            
        Raises:
            Exception: If connection creation fails
        """
        start_time = time.time()
        
        try:
            logger.debug(f"Creating new database connection to {settings.db_host}:{settings.db_port}")
            
            conn = pymysql.connect(
                host=settings.db_host,
                port=int(settings.db_port),
                user=settings.db_username,
                password=settings.db_password,
                database=settings.db_database,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                charset='utf8mb4',
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30,
            )
            connection_time = round((time.time() - start_time) * 1000, 2)
            self.active_connections += 1
            logger.debug(f"Database connection created successfully in {connection_time}ms. "
                        f"Active connections: {self.active_connections}")
            
            return conn
            
        except Exception as e:
            connection_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Failed to create database connection after {connection_time}ms: {str(e)}", exc_info=True)
            raise Exception(f"Failed to create database connection: {str(e)}")
    
    def get_connection(self) -> pymysql.Connection:
        """
        Get a connection from the pool.
        
        This method retrieves an available connection from the pool. If no connections
        are available, it either creates a new one (if under max limit) or waits for
        one to become available.
        
        Returns:
            pymysql.Connection: A database connection from the pool
            
        Note:
            The returned connection should be returned to the pool using
            return_connection() when no longer needed.
        """
        start_time = time.time()
        
        try:
            # Try to get an existing connection
            conn = self.connection_pool.get_nowait()
            
            # Check if connection is still alive
            if self._is_connection_alive(conn):
                wait_time = round((time.time() - start_time) * 1000, 2)
                logger.debug(f"Retrieved existing connection from pool in {wait_time}ms. "
                           f"Active connections: {self.active_connections}")
                return conn
            else:
                # Connection is dead, create a new one
                logger.warning("Retrieved dead connection from pool, creating replacement")
                self.active_connections -= 1
                return self._create_connection()
                
        except Empty:
            # No available connections, create new one if under max
            with self.lock:
                if self.active_connections < self.max_connections:
                    logger.debug(f"No available connections, creating new one. "
                               f"Current: {self.active_connections}, Max: {self.max_connections}")
                    return self._create_connection()
                else:
                    # Wait for a connection to become available
                    logger.debug(f"Pool at maximum capacity ({self.max_connections}), waiting for available connection")
                    conn = self.connection_pool.get()
                    
                    # Check if the waited connection is still alive
                    if self._is_connection_alive(conn):
                        wait_time = round((time.time() - start_time) * 1000, 2)
                        logger.debug(f"Retrieved connection after waiting {wait_time}ms")
                        return conn
                    else:
                        logger.warning("Retrieved dead connection after waiting, creating replacement")
                        self.active_connections -= 1
                        return self._create_connection()
    
    def return_connection(self, conn: pymysql.Connection) -> None:
        """
        Return a connection to the pool.
        
        This method returns a connection back to the pool for reuse. If the connection
        is dead or the pool is full, the connection is closed and removed from the
        active count.
        
        Args:
            conn (pymysql.Connection): The connection to return to the pool
        """
        if not conn:
            logger.warning("Attempted to return None connection to pool")
            return
            
        try:
            if self._is_connection_alive(conn):
                try:
                    self.connection_pool.put_nowait(conn)
                    logger.debug(f"Connection returned to pool successfully. "
                               f"Active connections: {self.active_connections}")
                except:
                    # Pool is full, close the connection
                    logger.debug("Pool is full, closing returned connection")
                    conn.close()
                    self.active_connections -= 1
            else:
                # Connection is dead, don't return it
                logger.warning("Dead connection detected, closing instead of returning to pool")
                conn.close()
                self.active_connections -= 1
                
        except Exception as e:
            logger.error(f"Error returning connection to pool: {str(e)}", exc_info=True)
            # Ensure connection is closed and count is decremented
            try:
                conn.close()
            except:
                pass
            self.active_connections -= 1
    
    def _is_connection_alive(self, conn: pymysql.Connection) -> bool:
        """
        Check if a connection is still alive and usable.
        
        This method performs a lightweight ping operation to verify the connection
        is still valid without reconnecting.
        
        Args:
            conn (pymysql.Connection): The connection to check
            
        Returns:
            bool: True if connection is alive, False otherwise
        """
        try:
            conn.ping(reconnect=False)
            return True
        except Exception as e:
            logger.debug(f"Connection health check failed: {str(e)}")
            return False
    
    def close_all(self) -> None:
        """
        Close all connections in the pool.
        
        This method closes all connections in the pool and resets the active
        connection count. It's typically called during application shutdown.
        """
        logger.info("Closing all connections in the pool")
        
        closed_count = 0
        while not self.connection_pool.empty():
            try:
                conn = self.connection_pool.get_nowait()
                conn.close()
                closed_count += 1
            except Empty:
                break
                
        self.active_connections = 0
        logger.info(f"Closed {closed_count} connections from pool")
    
    def get_pool_status(self) -> dict:
        """
        Get the current status of the connection pool.
        
        Returns:
            dict: Pool status information including connection counts and pool size
        """
        return {
            "active_connections": self.active_connections,
            "pool_size": self.connection_pool.qsize(),
            "max_connections": self.max_connections,
            "min_connections": self.min_connections,
            "available_connections": self.connection_pool.qsize(),
            "utilization_percentage": round((self.active_connections / self.connection_pool.qsize()) * 100, 2)
        }


# Global pool instance
logger.info("Creating global MySQL connection pool instance")
db_pool = PyMySQLPool(
    max_connections=settings.db_max_connections, 
    min_connections=settings.db_min_connections
)
logger.info("Global MySQL connection pool created successfully")