#!/usr/bin/env python3
"""
Enhanced Error Handling System
Comprehensive error handling with user-friendly recovery
"""

import asyncio
import logging
import traceback
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for better handling"""
    NETWORK = "network"
    API = "api"
    DATABASE = "database"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    USER_INPUT = "user_input"

@dataclass
class ErrorContext:
    """Context information for error handling"""
    operation: str
    user_id: Optional[int] = None
    domain_name: Optional[str] = None
    payment_id: Optional[str] = None
    callback_data: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None

@dataclass
class ErrorRecovery:
    """Error recovery strategy"""
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 1.0
    fallback_action: Optional[Callable] = None
    user_message: Optional[str] = None
    support_contact: bool = False

class EnhancedErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_patterns: Dict[str, ErrorCategory] = self._initialize_error_patterns()
        self.recovery_strategies: Dict[ErrorCategory, ErrorRecovery] = self._initialize_recovery_strategies()
        self.circuit_breakers: Dict[str, datetime] = {}
        self.circuit_breaker_duration = timedelta(minutes=5)
    
    def _initialize_error_patterns(self) -> Dict[str, ErrorCategory]:
        """Initialize error pattern recognition"""
        return {
            # Network errors
            'timeout': ErrorCategory.NETWORK,
            'connection': ErrorCategory.NETWORK,
            'network': ErrorCategory.NETWORK,
            'unreachable': ErrorCategory.NETWORK,
            'dns': ErrorCategory.NETWORK,
            
            # API errors
            'api': ErrorCategory.API,
            'http': ErrorCategory.API,
            '400': ErrorCategory.API,
            '401': ErrorCategory.AUTHENTICATION,
            '403': ErrorCategory.AUTHENTICATION,
            '404': ErrorCategory.API,
            '429': ErrorCategory.API,
            '500': ErrorCategory.EXTERNAL_SERVICE,
            '502': ErrorCategory.EXTERNAL_SERVICE,
            '503': ErrorCategory.EXTERNAL_SERVICE,
            
            # Database errors
            'database': ErrorCategory.DATABASE,
            'sql': ErrorCategory.DATABASE,
            'postgresql': ErrorCategory.DATABASE,
            'connection pool': ErrorCategory.DATABASE,
            'deadlock': ErrorCategory.DATABASE,
            
            # Validation errors
            'validation': ErrorCategory.VALIDATION,
            'invalid': ErrorCategory.USER_INPUT,
            'format': ErrorCategory.USER_INPUT,
            'missing': ErrorCategory.USER_INPUT,
            
            # External service errors
            'openprovider': ErrorCategory.EXTERNAL_SERVICE,
            'cloudflare': ErrorCategory.EXTERNAL_SERVICE,
            'blockbee': ErrorCategory.EXTERNAL_SERVICE,
        }
    
    def _initialize_recovery_strategies(self) -> Dict[ErrorCategory, ErrorRecovery]:
        """Initialize recovery strategies by error category"""
        return {
            ErrorCategory.NETWORK: ErrorRecovery(
                max_retries=3,
                retry_delay=2.0,
                user_message="🌐 Network issue detected. Retrying connection...",
                support_contact=False
            ),
            
            ErrorCategory.API: ErrorRecovery(
                max_retries=2,
                retry_delay=1.0,
                user_message="🔧 API temporarily unavailable. Please try again shortly.",
                support_contact=False
            ),
            
            ErrorCategory.DATABASE: ErrorRecovery(
                max_retries=3,
                retry_delay=0.5,
                user_message="💾 Database connection issue. Reconnecting...",
                support_contact=False
            ),
            
            ErrorCategory.EXTERNAL_SERVICE: ErrorRecovery(
                max_retries=2,
                retry_delay=3.0,
                user_message="🌍 External service temporarily unavailable. Retrying...",
                support_contact=True
            ),
            
            ErrorCategory.AUTHENTICATION: ErrorRecovery(
                max_retries=1,
                retry_delay=1.0,
                user_message="🔐 Authentication issue. Checking credentials...",
                support_contact=True
            ),
            
            ErrorCategory.USER_INPUT: ErrorRecovery(
                max_retries=0,
                user_message="📝 Please check your input and try again.",
                support_contact=False
            ),
            
            ErrorCategory.VALIDATION: ErrorRecovery(
                max_retries=0,
                user_message="✏️ Input validation failed. Please correct and retry.",
                support_contact=False
            ),
            
            ErrorCategory.BUSINESS_LOGIC: ErrorRecovery(
                max_retries=1,
                retry_delay=0.5,
                user_message="🤔 Unexpected issue occurred. Attempting recovery...",
                support_contact=True
            )
        }
    
    def categorize_error(self, error: Exception, context: ErrorContext) -> ErrorCategory:
        """Categorize error based on message and context"""
        error_message = str(error).lower()
        
        # Check for specific patterns
        for pattern, category in self.error_patterns.items():
            if pattern in error_message:
                return category
        
        # Context-based categorization
        if context.operation and 'api' in context.operation.lower():
            return ErrorCategory.API
        elif context.operation and 'database' in context.operation.lower():
            return ErrorCategory.DATABASE
        elif context.operation and 'validation' in context.operation.lower():
            return ErrorCategory.VALIDATION
        
        # Default categorization
        return ErrorCategory.BUSINESS_LOGIC
    
    def get_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        error_message = str(error).lower()
        
        # Critical errors
        if any(critical in error_message for critical in ['critical', 'fatal', 'corrupted']):
            return ErrorSeverity.CRITICAL
        
        # High severity
        if category in [ErrorCategory.DATABASE, ErrorCategory.AUTHENTICATION]:
            return ErrorSeverity.HIGH
        elif any(high in error_message for high in ['500', '502', '503', 'timeout']):
            return ErrorSeverity.HIGH
        
        # Medium severity  
        if category in [ErrorCategory.API, ErrorCategory.EXTERNAL_SERVICE]:
            return ErrorSeverity.MEDIUM
        elif any(medium in error_message for medium in ['400', '404', 'connection']):
            return ErrorSeverity.MEDIUM
        
        # Low severity
        if category in [ErrorCategory.USER_INPUT, ErrorCategory.VALIDATION]:
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM
    
    def should_retry(self, category: ErrorCategory, retry_count: int) -> bool:
        """Determine if operation should be retried"""
        strategy = self.recovery_strategies.get(category)
        if not strategy:
            return False
        
        return retry_count < strategy.max_retries
    
    def is_circuit_breaker_open(self, service: str) -> bool:
        """Check if circuit breaker is open for a service"""
        if service in self.circuit_breakers:
            if datetime.now() < self.circuit_breakers[service]:
                return True
            else:
                # Reset circuit breaker
                del self.circuit_breakers[service]
        
        return False
    
    def trip_circuit_breaker(self, service: str):
        """Trip circuit breaker for a service"""
        self.circuit_breakers[service] = datetime.now() + self.circuit_breaker_duration
        logger.warning(f"🚫 Circuit breaker tripped for {service} for {self.circuit_breaker_duration}")
    
    async def handle_error_with_recovery(
        self, 
        error: Exception, 
        context: ErrorContext,
        operation_func: Callable,
        *args, 
        **kwargs
    ) -> Dict[str, Any]:
        """Handle error with automatic recovery"""
        category = self.categorize_error(error, context)
        severity = self.get_severity(error, category)
        strategy = self.recovery_strategies.get(category, ErrorRecovery())
        
        # Track error for patterns
        error_key = f"{context.operation}_{category.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log error with context
        logger.error(
            f"🚨 Error in {context.operation}: {error} "
            f"(Category: {category.value}, Severity: {severity.value})"
        )
        logger.error(f"Error traceback: {traceback.format_exc()}")
        
        # Check circuit breaker
        if self.is_circuit_breaker_open(context.operation):
            return {
                'success': False,
                'error': 'Service temporarily unavailable (circuit breaker)',
                'user_message': '🔧 Service is temporarily offline for maintenance. Please try again in a few minutes.',
                'support_contact': True
            }
        
        # Attempt recovery
        recovery_attempts = 0
        while recovery_attempts < strategy.max_retries:
            recovery_attempts += 1
            
            logger.info(f"🔄 Recovery attempt {recovery_attempts}/{strategy.max_retries} for {context.operation}")
            
            # Wait before retry
            if strategy.retry_delay > 0:
                await asyncio.sleep(strategy.retry_delay * recovery_attempts)  # Exponential backoff
            
            try:
                # Retry the operation
                result = await operation_func(*args, **kwargs)
                logger.info(f"✅ Recovery successful for {context.operation} after {recovery_attempts} attempts")
                return {
                    'success': True,
                    'result': result,
                    'recovery_attempts': recovery_attempts
                }
            
            except Exception as retry_error:
                logger.warning(f"❌ Recovery attempt {recovery_attempts} failed: {retry_error}")
                
                # If this is the last attempt, prepare final error response
                if recovery_attempts >= strategy.max_retries:
                    # Trip circuit breaker if too many failures
                    if self.error_counts.get(error_key, 0) >= 5:
                        self.trip_circuit_breaker(context.operation)
                    
                    return self._prepare_error_response(error, category, strategy, context, recovery_attempts)
        
        # Should never reach here, but safety fallback
        return self._prepare_error_response(error, category, strategy, context, recovery_attempts)
    
    def _prepare_error_response(
        self, 
        error: Exception, 
        category: ErrorCategory, 
        strategy: ErrorRecovery,
        context: ErrorContext,
        recovery_attempts: int
    ) -> Dict[str, Any]:
        """Prepare final error response after all recovery attempts"""
        # Generate user-friendly message
        user_message = strategy.user_message or f"❌ {context.operation.replace('_', ' ').title()} failed"
        
        # Add recovery attempt info if any were made
        if recovery_attempts > 0:
            user_message += f"\n\n🔄 Attempted recovery {recovery_attempts} times"
        
        # Add support contact info if needed
        if strategy.support_contact:
            user_message += "\n\n💬 If this issue persists, please contact our support team for assistance."
        
        return {
            'success': False,
            'error': str(error),
            'category': category.value,
            'user_message': user_message,
            'support_contact': strategy.support_contact,
            'recovery_attempts': recovery_attempts
        }
    
    def get_user_friendly_message(self, error: Exception, operation: str) -> str:
        """Get user-friendly error message"""
        error_str = str(error).lower()
        
        # Domain-specific messages
        if 'domain' in operation.lower():
            if 'unavailable' in error_str or 'taken' in error_str:
                return "😔 That domain is already taken, but we'll show you some great alternatives!"
            elif 'invalid' in error_str:
                return "📝 The domain format looks unusual. Let us help you correct it!"
        
        # Payment-specific messages
        elif 'payment' in operation.lower():
            if 'timeout' in error_str or 'expired' in error_str:
                return "⏰ Payment session expired. Don't worry - you can create a new payment anytime!"
            elif 'insufficient' in error_str:
                return "💳 Your wallet needs more funds. You can easily add cryptocurrency anytime!"
        
        # DNS-specific messages
        elif 'dns' in operation.lower():
            if 'invalid' in error_str:
                return "🌐 The DNS record format needs adjustment. Let's fix that together!"
            elif 'propagation' in error_str:
                return "⏰ DNS changes are still processing. This usually takes a few minutes!"
        
        # Generic friendly messages
        return "🤔 Something unexpected happened, but we're here to help you resolve it!"

# Global error handler instance
error_handler = EnhancedErrorHandler()

# Decorator for automatic error handling
def with_error_recovery(operation_name: str):
    """Decorator for automatic error handling and recovery"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract context from arguments if available
            context = ErrorContext(operation=operation_name)
            
            # Try to extract user_id from common argument patterns
            if args and hasattr(args[0], 'from_user'):
                context.user_id = args[0].from_user.id
            elif 'user_id' in kwargs:
                context.user_id = kwargs['user_id']
            
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                return await error_handler.handle_error_with_recovery(
                    e, context, func, *args, **kwargs
                )
        return wrapper
    return decorator

async def test_error_handling():
    """Test error handling system"""
    print("🧪 TESTING ERROR HANDLING SYSTEM")
    print("=" * 50)
    
    handler = EnhancedErrorHandler()
    
    # Test error categorization
    test_errors = [
        (Exception("Connection timeout"), "network_operation"),
        (Exception("HTTP 500 Internal Server Error"), "api_call"),
        (Exception("Invalid domain format"), "domain_validation"),
        (Exception("Database connection failed"), "database_query"),
        (Exception("OpenProvider API error"), "domain_registration")
    ]
    
    print("📋 Error Categorization Tests:")
    for error, operation in test_errors:
        context = ErrorContext(operation=operation)
        category = handler.categorize_error(error, context)
        severity = handler.get_severity(error, category)
        friendly_msg = handler.get_user_friendly_message(error, operation)
        
        print(f"{operation:20} → {category.value:15} ({severity.value}) → {friendly_msg}")
    
    # Test recovery strategy
    print(f"\n🔄 Recovery Strategy Tests:")
    for category, strategy in handler.recovery_strategies.items():
        print(f"{category.value:20} → Max retries: {strategy.max_retries}, Delay: {strategy.retry_delay}s")

if __name__ == "__main__":
    asyncio.run(test_error_handling())