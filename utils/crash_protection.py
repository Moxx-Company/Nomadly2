"""
Comprehensive Crash Protection System
Ensures the bot never crashes in production
"""

import logging
import traceback
import functools
import asyncio
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

class CrashProtection:
    """Comprehensive crash protection for the bot"""
    
    @staticmethod
    def safe_import(module_name: str, fallback=None):
        """Safely import modules with fallback"""
        try:
            return __import__(module_name)
        except ImportError as e:
            logger.error(f"Import failed for {module_name}: {e}")
            return fallback
        except Exception as e:
            logger.error(f"Unexpected import error for {module_name}: {e}")
            return fallback
    
    @staticmethod
    def protect_method(fallback_response: str = "Service temporarily unavailable"):
        """Decorator to protect methods from crashes"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Protected method {func.__name__} failed: {e}")
                    logger.error(traceback.format_exc())
                    
                    # Try to send fallback response if it's a query
                    if args and hasattr(args[0], 'edit_message_text'):
                        try:
                            await args[0].edit_message_text(fallback_response)
                        except:
                            pass
                    
                    return None
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Protected method {func.__name__} failed: {e}")
                    logger.error(traceback.format_exc())
                    return None
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    @staticmethod
    async def safe_api_call(api_func: Callable, *args, **kwargs) -> Optional[Any]:
        """Safely call API functions with automatic retry"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await api_func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"API call failed permanently: {e}")
                    return None
                await asyncio.sleep(1)  # Brief delay before retry
        return None
    
    @staticmethod
    def safe_database_operation(db_func: Callable, *args, **kwargs) -> Optional[Any]:
        """Safely execute database operations"""
        try:
            return db_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    async def protected_callback_handler(query, handler_func: Callable, *args, **kwargs):
        """Protected wrapper for callback handlers"""
        try:
            # Always acknowledge callback first
            try:
                await query.answer()
            except:
                pass  # Ignore if already answered
            
            # Execute handler
            return await handler_func(query, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Callback handler failed: {e}")
            logger.error(traceback.format_exc())
            
            # Send error message to user
            try:
                await query.edit_message_text(
                    "⚠️ Service temporarily unavailable. Please try again in a moment.",
                    reply_markup=None
                )
            except:
                # If that fails, try basic message
                try:
                    await query.message.reply_text("Service temporarily unavailable.")
                except:
                    pass  # Last resort - just log the error
    
    @staticmethod
    def monitor_system_health():
        """Monitor system health and log warnings"""
        import psutil
        try:
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                logger.warning(f"High memory usage: {memory.percent}%")
            
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                logger.warning(f"Low disk space: {disk.percent}% used")
                
        except Exception as e:
            logger.debug(f"Health monitoring failed: {e}")

# Global instance
crash_protection = CrashProtection()

# Convenience decorators
protect = crash_protection.protect_method
safe_api = crash_protection.safe_api_call
safe_db = crash_protection.safe_database_operation