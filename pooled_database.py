#!/usr/bin/env python3
"""
Database wrapper using connection pooling
Drop-in replacement for direct database connections
"""

from simple_connection_pool import get_pooled_connection
import os

class PooledDatabaseManager:
    """Database manager that uses connection pooling"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
    
    def get_connection(self):
        """Get a pooled connection"""
        return get_pooled_connection()
    
    def execute_query(self, query, params=None):
        """Execute a query using pooled connection"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
    
    def test_connection(self):
        """Test the pooled connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

# Global instance
pooled_db = PooledDatabaseManager()

def get_database_manager():
    """Get the pooled database manager"""
    return pooled_db
