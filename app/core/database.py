"""
Database configuration and session management for Nomadly3
"""

import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

# Import Base from fresh database module for consistency
try:
    from fresh_database import Base, FreshDatabaseManager
    
    # Create global database manager instance
    db_manager = FreshDatabaseManager()
    
    def get_db_session():
        """Get database session - returns SQLAlchemy session"""
        try:
            return db_manager.get_session()
        except Exception as e:
            logger.error(f"Error creating database session: {e}")
            raise

    def get_db_connection():
        """Get direct database connection"""
        try:
            return db_manager.create_connection()
        except Exception as e:
            logger.error(f"Error creating database connection: {e}")
            raise
            
except ImportError:
    # Fallback implementation if fresh_database is not available
    logger.warning("Could not import from fresh database module, using fallback")
    
    Base = declarative_base()
    
    def get_db_session():
        """Fallback database session"""
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        return SessionLocal()
    
    def get_db_connection():
        """Fallback database connection"""
        import psycopg2
        return psycopg2.connect(os.getenv('DATABASE_URL'))
