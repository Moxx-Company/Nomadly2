#!/usr/bin/env python3
"""
Simple Connection Pool for Nomadly2 - Alternative to PgBouncer
Works with Neon database and provides connection pooling functionality
"""

import os
import psycopg2
import psycopg2.pool
import threading
import time
from contextlib import contextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleConnectionPool:
    """Simple connection pool that works with Neon database"""
    
    def __init__(self, database_url, min_connections=5, max_connections=50):
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool = None
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "pool_hits": 0,
            "pool_misses": 0
        }
        self._lock = threading.Lock()
        
        self._create_pool()
    
    def _create_pool(self):
        """Create the connection pool"""
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                self.database_url
            )
            logger.info(f"✅ Connection pool created: {self.min_connections}-{self.max_connections} connections")
        except Exception as e:
            logger.error(f"❌ Failed to create connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        conn = None
        try:
            with self._lock:
                conn = self.pool.getconn()
                self.stats["active_connections"] += 1
                self.stats["pool_hits"] += 1
            
            yield conn
            
        except Exception as e:
            with self._lock:
                self.stats["pool_misses"] += 1
            logger.error(f"Connection error: {e}")
            raise
        finally:
            if conn:
                with self._lock:
                    self.pool.putconn(conn)
                    self.stats["active_connections"] -= 1
    
    def get_stats(self):
        """Get pool statistics"""
        with self._lock:
            return {
                **self.stats,
                "pool_size": len(self.pool._pool) if self.pool else 0,
                "min_connections": self.min_connections,
                "max_connections": self.max_connections
            }
    
    def health_check(self):
        """Perform health check"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def close_all(self):
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("🔒 All connections closed")

# Global connection pool instance
_connection_pool = None

def get_pool():
    """Get the global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        _connection_pool = SimpleConnectionPool(database_url)
    return _connection_pool

def get_pooled_connection():
    """Get a pooled database connection (context manager)"""
    return get_pool().get_connection()

def test_pool():
    """Test the connection pool"""
    print("🧪 Testing Simple Connection Pool")
    print("=" * 40)
    
    try:
        pool = get_pool()
        
        # Health check
        health_ok = pool.health_check()
        print(f"🏥 Health check: {'✅' if health_ok else '❌'}")
        
        # Test multiple connections
        print("🔄 Testing multiple connections...")
        for i in range(5):
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT current_timestamp")
                result = cursor.fetchone()
                print(f"   Connection {i+1}: {result[0]}")
        
        # Show stats
        stats = pool.get_stats()
        print("\n📊 Pool Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n✅ Connection pool test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Connection pool test failed: {e}")
        return False

if __name__ == "__main__":
    test_pool()