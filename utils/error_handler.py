#!/usr/bin/env python3
"""
Global Error Handling System for Nomadly2 Bot
Provides centralized error handling, logging, and user-friendly error messages
"""

import logging
import traceback
import functools
from typing import Optional, Any, Callable
from telegram import Update
from telegram.ext import ContextTypes

# Configure centralized logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nomadly_bot.log'),
        logging.StreamHandler()
    ]
)

class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler for telegram bot"""
        error = context.error
        
        # Log the error with full context
        self.logger.error(
            f"Exception while handling update {update.update_id}: {error}",
            exc_info=context.error
        )
        
        # Get user-friendly error message
        user_message = self._get_user_error_message(error)
        
        # Try to send error message to user
        try:
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"⚠️ {user_message}\n\nPlease try again or contact support if the issue persists."
                )
        except Exception as send_error:
            self.logger.error(f"Could not send error message to user: {send_error}")
    
    def _get_user_error_message(self, error: Exception) -> str:
        """Convert technical errors to user-friendly messages"""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return "Request timed out. Please try again."
        elif "network" in error_str or "connection" in error_str:
            return "Network connection issue. Please check your internet connection."
        elif "api" in error_str:
            return "External service temporarily unavailable."
        elif "database" in error_str:
            return "Database temporarily unavailable. Please try again shortly."
        elif "payment" in error_str:
            return "Payment processing issue. Please contact support."
        else:
            return "An unexpected error occurred."

def safe_execute(fallback_message: str = "Operation failed"):
    """Decorator for safe function execution with error handling"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(func.__module__)
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return fallback_message
        return wrapper
    return decorator

def log_function_call(func: Callable) -> Callable:
    """Decorator to log function calls for debugging"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"Calling {func.__name__} with args: {len(args)}, kwargs: {list(kwargs.keys())}")
        
        try:
            result = await func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
    
    return wrapper

# Global error handler instance
error_handler = ErrorHandler()