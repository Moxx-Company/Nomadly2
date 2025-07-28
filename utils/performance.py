#!/usr/bin/env python3
"""
Performance and Caching Module for Nomadly2 Bot
Implements caching, async processing, and performance optimization
"""

import asyncio
import time
import json
import hashlib
from typing import Any, Dict, Optional, Callable, List
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class MemoryCache:
    """In-memory cache for frequently accessed data"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def _is_expired(self, timestamp: float, ttl: int) -> bool:
        """Check if cache entry is expired"""
        return time.time() - timestamp > ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            value, timestamp, ttl = self.cache[key]
            if not self._is_expired(timestamp, ttl):
                logger.debug(f"Cache hit for key: {key}")
                return value
            else:
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key}")
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = (value, time.time(), ttl)
        logger.debug(f"Cache set for key: {key}, TTL: {ttl}")
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.debug("Cache cleared")
    
    def cleanup_expired(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, (value, timestamp, ttl) in self.cache.items():
            if current_time - timestamp > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        cache = MemoryCache(ttl)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{key_prefix}{func.__name__}{str(args)}{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

class BackgroundTaskManager:
    """Manage background tasks and async processing"""
    
    def __init__(self):
        self.tasks = {}
        self.task_queue = asyncio.Queue()
        self.workers_started = False
    
    async def start_workers(self, num_workers: int = 3):
        """Start background workers"""
        if self.workers_started:
            return
        
        for i in range(num_workers):
            task = asyncio.create_task(self._worker(f"worker-{i}"))
            self.tasks[f"worker-{i}"] = task
        
        self.workers_started = True
        logger.info(f"Started {num_workers} background workers")
    
    async def _worker(self, name: str):
        """Background worker to process tasks"""
        while True:
            try:
                task_func, args, kwargs = await self.task_queue.get()
                logger.debug(f"{name} processing task: {task_func.__name__}")
                
                start_time = time.time()
                await task_func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.debug(f"{name} completed task in {duration:.2f}s")
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Background task error in {name}: {e}")
    
    async def add_task(self, func: Callable, *args, **kwargs):
        """Add task to background queue"""
        await self.task_queue.put((func, args, kwargs))
        logger.debug(f"Added background task: {func.__name__}")
    
    def add_task_sync(self, func: Callable, *args, **kwargs):
        """Add task to background queue (sync version)"""
        try:
            asyncio.create_task(self.add_task(func, *args, **kwargs))
        except RuntimeError:
            # If no event loop is running, start one
            asyncio.run(self.add_task(func, *args, **kwargs))

def async_retry(max_retries: int = 3, delay: float = 1.0, exponential_backoff: bool = True):
    """Decorator for retrying async functions with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    # Calculate delay
                    current_delay = delay * (2 ** attempt) if exponential_backoff else delay
                    
                    logger.warning(f"Attempt {attempt + 1} of {func.__name__} failed: {e}. Retrying in {current_delay}s")
                    await asyncio.sleep(current_delay)
            
            raise last_exception
        
        return wrapper
    return decorator

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = 0  # Would need psutil for actual memory monitoring
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > 1.0:  # Log slow operations
                logger.warning(f"Slow operation: {func.__name__} took {duration:.2f}s")
            else:
                logger.debug(f"Performance: {func.__name__} took {duration:.2f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed operation: {func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    return wrapper

# Global instances
memory_cache = MemoryCache()
background_task_manager = BackgroundTaskManager()

# Pagination helper
class PaginationHelper:
    """Helper for paginating large datasets"""
    
    @staticmethod
    def paginate_list(items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Paginate a list of items"""
        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page
        
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        paginated_items = items[start_index:end_index]
        
        return {
            'items': paginated_items,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }