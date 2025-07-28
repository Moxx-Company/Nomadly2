"""
Enhanced Logging System for Nomadly2
Provides structured logging with correlation IDs and performance tracking
"""

import os
import logging
import json
import time
import uuid
import threading
from typing import Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager
from functools import wraps

# Thread-local storage for correlation IDs
_correlation_context = threading.local()

class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records"""
    
    def filter(self, record):
        # Add correlation ID to log record
        correlation_id = get_correlation_id()
        record.correlation_id = correlation_id
        
        # Add user context if available
        user_context = get_user_context()
        record.user_id = user_context.get('user_id', 'anonymous') if user_context else 'anonymous'
        record.telegram_id = user_context.get('telegram_id', 'N/A') if user_context else 'N/A'
        
        return True

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', 'N/A'),
            'user_id': getattr(record, 'user_id', 'anonymous'),
            'telegram_id': getattr(record, 'telegram_id', 'N/A'),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_enhanced_logging(log_level: str = "INFO", enable_structured: bool = True):
    """Setup enhanced logging configuration"""
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # Add correlation filter
    correlation_filter = CorrelationFilter()
    console_handler.addFilter(correlation_filter)
    
    # Set formatter based on configuration
    if enable_structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] [%(telegram_id)s] - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler for important logs
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = logging.FileHandler('logs/nomadly2.log')
    file_handler.setLevel(logging.WARNING)  # Only warnings and above to file
    file_handler.addFilter(correlation_filter)
    file_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(file_handler)
    
    logging.info("Enhanced logging system initialized")

def get_correlation_id() -> str:
    """Get current correlation ID from thread-local storage"""
    if not hasattr(_correlation_context, 'correlation_id'):
        _correlation_context.correlation_id = str(uuid.uuid4())[:8]
    return _correlation_context.correlation_id

def set_correlation_id(correlation_id: str):
    """Set correlation ID for current thread"""
    _correlation_context.correlation_id = correlation_id

def get_user_context() -> Optional[Dict[str, Any]]:
    """Get current user context from thread-local storage"""
    return getattr(_correlation_context, 'user_context', None)

def set_user_context(telegram_id: int, user_id: Optional[int] = None):
    """Set user context for current thread"""
    _correlation_context.user_context = {
        'telegram_id': telegram_id,
        'user_id': user_id or telegram_id
    }

@contextmanager
def correlation_context(correlation_id: Optional[str] = None):
    """Context manager for correlation ID"""
    old_correlation_id = get_correlation_id()
    
    if correlation_id:
        set_correlation_id(correlation_id)
    else:
        set_correlation_id(str(uuid.uuid4())[:8])
    
    try:
        yield get_correlation_id()
    finally:
        set_correlation_id(old_correlation_id)

@contextmanager
def user_context(telegram_id: int, user_id: Optional[int] = None):
    """Context manager for user context"""
    old_context = get_user_context()
    
    set_user_context(telegram_id, user_id)
    
    try:
        yield
    finally:
        if old_context:
            _correlation_context.user_context = old_context
        else:
            if hasattr(_correlation_context, 'user_context'):
                delattr(_correlation_context, 'user_context')

def log_with_extra(level: int, message: str, extra_fields: Dict[str, Any]):
    """Log message with extra structured fields"""
    logger = logging.getLogger(__name__)
    
    # Create log record
    record = logger.makeRecord(
        logger.name, level, __file__, 0, message, (), None
    )
    
    # Add extra fields
    record.extra_fields = extra_fields
    
    # Handle the record
    logger.handle(record)

class PerformanceTracker:
    """Track performance metrics for operations"""
    
    def __init__(self, operation_name: str, threshold_ms: float = 1000):
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time = None
        self.logger = logging.getLogger(f"performance.{operation_name}")
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            
            extra_fields = {
                'operation': self.operation_name,
                'duration_ms': round(duration_ms, 2),
                'slow_operation': duration_ms > self.threshold_ms
            }
            
            if exc_type:
                extra_fields['error'] = str(exc_val)
                log_with_extra(logging.ERROR, 
                             f"Operation {self.operation_name} failed after {duration_ms:.2f}ms", 
                             extra_fields)
            elif duration_ms > self.threshold_ms:
                log_with_extra(logging.WARNING,
                             f"Slow operation {self.operation_name} took {duration_ms:.2f}ms", 
                             extra_fields)
            else:
                log_with_extra(logging.INFO,
                             f"Operation {self.operation_name} completed in {duration_ms:.2f}ms", 
                             extra_fields)

def performance_monitor(operation_name: Optional[str] = None, threshold_ms: float = 1000):
    """Decorator to monitor function performance"""
    def decorator(func):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with PerformanceTracker(op_name, threshold_ms):
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with PerformanceTracker(op_name, threshold_ms):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class APICallLogger:
    """Logger specifically for API calls"""
    
    def __init__(self, api_name: str):
        self.api_name = api_name
        self.logger = logging.getLogger(f"api.{api_name}")
    
    def log_request(self, method: str, endpoint: str, params: Dict[str, Any] = None):
        """Log API request"""
        extra_fields = {
            'api_name': self.api_name,
            'method': method,
            'endpoint': endpoint,
            'request_params': params or {}
        }
        
        log_with_extra(logging.INFO, f"API Request: {method} {endpoint}", extra_fields)
    
    def log_response(self, method: str, endpoint: str, status_code: int, 
                    response_time_ms: float, error: Optional[str] = None):
        """Log API response"""
        extra_fields = {
            'api_name': self.api_name,
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'success': status_code < 400
        }
        
        if error:
            extra_fields['error'] = error
        
        level = logging.ERROR if status_code >= 400 else logging.INFO
        message = f"API Response: {method} {endpoint} - {status_code} ({response_time_ms:.2f}ms)"
        
        log_with_extra(level, message, extra_fields)

# Convenience functions
def log_user_action(telegram_id: int, action: str, details: Dict[str, Any] = None):
    """Log user action with context"""
    with user_context(telegram_id):
        extra_fields = {
            'action_type': 'user_action',
            'action': action,
            'details': details or {}
        }
        log_with_extra(logging.INFO, f"User action: {action}", extra_fields)

def log_payment_event(order_id: str, event: str, details: Dict[str, Any] = None):
    """Log payment-related event"""
    extra_fields = {
        'event_type': 'payment',
        'order_id': order_id,
        'event': event,
        'details': details or {}
    }
    log_with_extra(logging.INFO, f"Payment event: {event} for order {order_id}", extra_fields)

def log_domain_event(domain_name: str, event: str, details: Dict[str, Any] = None):
    """Log domain-related event"""
    extra_fields = {
        'event_type': 'domain',
        'domain_name': domain_name,
        'event': event,
        'details': details or {}
    }
    log_with_extra(logging.INFO, f"Domain event: {event} for {domain_name}", extra_fields)

# Import asyncio at the end to avoid circular imports
import asyncio