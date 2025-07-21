import pymysql
import pymysql.cursors
import os
from queue import Queue, Empty
from threading import Lock
import time
from typing import Optional
from app.config.settings import settings

class PyMySQLPool:
    def __init__(self, max_connections=20, min_connections=5):
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_pool = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = Lock()
        
        # Initialize minimum connections
        for _ in range(min_connections):
            self._create_connection()
    
    def _create_connection(self):
        """Create a new database connection"""
        try:
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
            return conn
        except Exception as e:
            raise Exception(f"Failed to create database connection: {str(e)}")
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            # Try to get an existing connection
            conn = self.connection_pool.get_nowait()
            
            # Check if connection is still alive
            if self._is_connection_alive(conn):
                return conn
            else:
                # Connection is dead, create a new one
                self.active_connections -= 1
                return self._create_connection()
                
        except Empty:
            # No available connections, create new one if under max
            with self.lock:
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    return self._create_connection()
                else:
                    # Wait for a connection to become available
                    return self.connection_pool.get()
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        if conn and self._is_connection_alive(conn):
            try:
                self.connection_pool.put_nowait(conn)
            except:
                # Pool is full, close the connection
                conn.close()
                self.active_connections -= 1
        else:
            # Connection is dead, don't return it
            if conn:
                conn.close()
            self.active_connections -= 1
    
    def _is_connection_alive(self, conn):
        """Check if connection is still alive"""
        try:
            conn.ping(reconnect=False)
            return True
        except:
            return False
    
    def close_all(self):
        """Close all connections in the pool"""
        while not self.connection_pool.empty():
            try:
                conn = self.connection_pool.get_nowait()
                conn.close()
            except Empty:
                break
        self.active_connections = 0

# Global pool instance
db_pool = PyMySQLPool(max_connections=settings.db_max_connections, min_connections=settings.db_min_connections)