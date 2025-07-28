#!/usr/bin/env python3
"""
Enhanced Database Manager with Session Optimization
Resolves database session conflicts and connection pooling
"""

import logging
import contextlib
from typing import Optional, Any, Dict, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
import time
import threading
from functools import wraps

logger = logging.getLogger(__name__)

class OptimizedDatabaseManager:
    """Enhanced database manager with session optimization and connection pooling"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._engine = None
        self._session_factory = None
        self._local = threading.local()
        self.setup_optimized_engine()
    
    def setup_optimized_engine(self):
        """Setup database engine with optimized connection pooling"""
        try:
            # Enhanced connection pool configuration
            self._engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=10,          # Base number of connections
                max_overflow=20,       # Additional connections when needed
                pool_pre_ping=True,    # Validate connections before use
                pool_recycle=3600,     # Recycle connections every hour
                echo=False,            # Set to True for SQL debugging
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "nomadly2_bot"
                }
            )
            
            self._session_factory = sessionmaker(
                bind=self._engine,
                autoflush=False,       # Manual control over flushing
                expire_on_commit=False # Keep objects accessible after commit
            )
            
            logger.info("✅ Optimized database engine configured")
            
        except Exception as e:
            logger.error(f"❌ Database engine setup failed: {e}")
            raise

    @contextlib.contextmanager
    def get_optimized_session(self, retries: int = 3):
        """Get database session with automatic retry and cleanup"""
        session = None
        attempt = 0
        
        while attempt < retries:
            try:
                session = self._session_factory()
                yield session
                session.commit()
                break
                
            except DisconnectionError as e:
                logger.warning(f"⚠️ Database disconnection (attempt {attempt + 1}/{retries}): {e}")
                if session:
                    session.rollback()
                    session.close()
                    session = None
                
                if attempt == retries - 1:
                    raise
                
                attempt += 1
                time.sleep(0.5 * attempt)  # Exponential backoff
                
            except SQLAlchemyError as e:
                logger.error(f"❌ Database error (attempt {attempt + 1}/{retries}): {e}")
                if session:
                    session.rollback()
                    session.close()
                    session = None
                
                if attempt == retries - 1:
                    raise
                
                attempt += 1
                time.sleep(0.2 * attempt)
                
            except Exception as e:
                logger.error(f"❌ Unexpected database error: {e}")
                if session:
                    session.rollback()
                    session.close()
                raise
                
        if session and session.is_active:
            session.close()

    def safe_database_operation(self, operation_name: str):
        """Decorator for safe database operations with error handling"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    with self.get_optimized_session() as session:
                        # Inject session into kwargs if not present
                        if 'session' not in kwargs:
                            kwargs['session'] = session
                        
                        result = func(*args, **kwargs)
                        return result
                        
                except Exception as e:
                    logger.error(f"❌ {operation_name} failed: {e}")
                    raise
                    
            return wrapper
        return decorator

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get database connection pool statistics"""
        if not self._engine:
            return {"status": "not_initialized"}
        
        pool = self._engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "status": "healthy"
        }

# Enhanced session management functions
def with_db_session(retries: int = 3):
    """Decorator for functions that need database sessions"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from database import get_db_manager
            db_manager = get_db_manager()
            
            if hasattr(db_manager, 'get_optimized_session'):
                with db_manager.get_optimized_session(retries=retries) as session:
                    kwargs['session'] = session
                    return await func(*args, **kwargs)
            else:
                # Fallback to regular session
                session = db_manager.get_session()
                try:
                    kwargs['session'] = session
                    result = await func(*args, **kwargs)
                    session.commit()
                    return result
                except Exception as e:
                    session.rollback()
                    raise
                finally:
                    session.close()
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            from database import get_db_manager
            db_manager = get_db_manager()
            
            if hasattr(db_manager, 'get_optimized_session'):
                with db_manager.get_optimized_session(retries=retries) as session:
                    kwargs['session'] = session
                    return func(*args, **kwargs)
            else:
                # Fallback to regular session
                session = db_manager.get_session()
                try:
                    kwargs['session'] = session
                    result = func(*args, **kwargs)
                    session.commit()
                    return result
                except Exception as e:
                    session.rollback()
                    raise
                finally:
                    session.close()
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Connection health check
def check_database_health() -> Dict[str, Any]:
    """Check database connection health"""
    try:
        from database import get_db_manager
        db_manager = get_db_manager()
        
        if hasattr(db_manager, 'get_connection_stats'):
            stats = db_manager.get_connection_stats()
            stats['timestamp'] = time.time()
            return stats
        else:
            # Basic health check
            session = db_manager.get_session()
            session.execute("SELECT 1")
            session.close()
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "pool_type": "basic"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

logger.info("✅ Enhanced database manager module loaded")