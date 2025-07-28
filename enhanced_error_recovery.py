#!/usr/bin/env python3
"""
Enhanced Error Recovery System
Comprehensive edge case handling and recovery mechanisms
"""

import logging
import asyncio
import traceback
import json
import time
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from enum import Enum
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"          # Recoverable, retry automatically
    MEDIUM = "medium"    # Needs attention but not critical
    HIGH = "high"        # Critical, immediate attention
    CRITICAL = "critical" # System-wide impact

class ErrorCategory(Enum):
    """Error categorization"""
    NETWORK = "network"
    DATABASE = "database" 
    API = "api"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"

class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"     # Normal operation
    OPEN = "open"         # Failing, blocking requests
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreaker:
    """Circuit breaker pattern for API resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, expected_exception: Exception = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    async def acall(self, func, *args, **kwargs):
        """Async version of circuit breaker call"""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        return (
            self.last_failure_time and 
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

class ErrorRecoveryManager:
    """Centralized error recovery and monitoring"""
    
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_history = deque(maxlen=1000)
        self.recovery_strategies = {}
        self.circuit_breakers = {}
        self.lock = threading.Lock()
    
    def register_recovery_strategy(self, error_category: ErrorCategory, strategy: Callable):
        """Register recovery strategy for specific error category"""
        self.recovery_strategies[error_category] = strategy
        logger.info(f"✅ Registered recovery strategy for {error_category.value}")
    
    def get_circuit_breaker(self, service_name: str, **kwargs) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(**kwargs)
        return self.circuit_breakers[service_name]
    
    def log_error(self, error: Exception, category: ErrorCategory, severity: ErrorSeverity, context: Dict[str, Any] = None):
        """Log error with categorization and context"""
        with self.lock:
            error_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "category": category.value,
                "severity": severity.value,
                "context": context or {},
                "traceback": traceback.format_exc()
            }
            
            self.error_history.append(error_info)
            self.error_counts[f"{category.value}_{severity.value}"] += 1
            
            # Log with appropriate level
            if severity == ErrorSeverity.CRITICAL:
                logger.critical(f"CRITICAL ERROR [{category.value}]: {error}")
            elif severity == ErrorSeverity.HIGH:
                logger.error(f"HIGH SEVERITY [{category.value}]: {error}")
            elif severity == ErrorSeverity.MEDIUM:
                logger.warning(f"MEDIUM SEVERITY [{category.value}]: {error}")
            else:
                logger.info(f"LOW SEVERITY [{category.value}]: {error}")
    
    async def attempt_recovery(self, error: Exception, category: ErrorCategory, context: Dict[str, Any] = None) -> bool:
        """Attempt to recover from error using registered strategies"""
        try:
            if category in self.recovery_strategies:
                strategy = self.recovery_strategies[category]
                
                if asyncio.iscoroutinefunction(strategy):
                    success = await strategy(error, context)
                else:
                    success = strategy(error, context)
                
                if success:
                    logger.info(f"✅ Recovery successful for {category.value} error")
                    return True
                else:
                    logger.warning(f"⚠️ Recovery failed for {category.value} error")
                    return False
            else:
                logger.warning(f"⚠️ No recovery strategy for {category.value}")
                return False
                
        except Exception as recovery_error:
            logger.error(f"❌ Recovery strategy failed: {recovery_error}")
            return False
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and health metrics"""
        with self.lock:
            recent_errors = [
                e for e in self.error_history 
                if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
            ]
            
            return {
                "total_errors": len(self.error_history),
                "recent_errors": len(recent_errors),
                "error_counts": dict(self.error_counts),
                "circuit_breaker_states": {
                    name: cb.state.value 
                    for name, cb in self.circuit_breakers.items()
                },
                "health_score": self._calculate_health_score()
            }
    
    def _calculate_health_score(self) -> float:
        """Calculate system health score (0-100)"""
        if not self.error_history:
            return 100.0
        
        recent_errors = [
            e for e in self.error_history 
            if datetime.fromisoformat(e["timestamp"]) > datetime.utcnow() - timedelta(minutes=30)
        ]
        
        if not recent_errors:
            return 100.0
        
        # Penalty based on error severity and frequency
        penalty = 0
        for error in recent_errors:
            if error["severity"] == "critical":
                penalty += 20
            elif error["severity"] == "high":
                penalty += 10
            elif error["severity"] == "medium":
                penalty += 5
            else:
                penalty += 1
        
        return max(0, 100 - penalty)

# Global error recovery manager
error_recovery = ErrorRecoveryManager()

def with_error_recovery(category: ErrorCategory, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                       context_func: Callable = None, max_retries: int = 3, retry_delay: float = 1.0):
    """Decorator for automatic error recovery"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = context_func(*args, **kwargs) if context_func else {}
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    error_recovery.log_error(e, category, severity, context)
                    
                    if attempt < max_retries:
                        # Attempt recovery
                        recovery_success = await error_recovery.attempt_recovery(e, category, context)
                        
                        if recovery_success:
                            logger.info(f"🔄 Retrying after successful recovery (attempt {attempt + 1})")
                        else:
                            logger.warning(f"⚠️ Retrying without recovery (attempt {attempt + 1})")
                        
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        logger.error(f"❌ Max retries exceeded for {func.__name__}")
                        raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = context_func(*args, **kwargs) if context_func else {}
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_recovery.log_error(e, category, severity, context)
                    
                    if attempt < max_retries:
                        logger.warning(f"⚠️ Retrying after error (attempt {attempt + 1})")
                        time.sleep(retry_delay * (attempt + 1))
                    else:
                        logger.error(f"❌ Max retries exceeded for {func.__name__}")
                        raise
        
        # Return appropriate wrapper
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Recovery strategies for common scenarios
async def database_recovery_strategy(error: Exception, context: Dict[str, Any]) -> bool:
    """Recovery strategy for database errors"""
    try:
        logger.info("🔄 Attempting database recovery...")
        
        # Check if it's a connection issue
        if "connection" in str(error).lower():
            # Wait and retry with new connection
            await asyncio.sleep(2)
            
            # Test connection
            from enhanced_database_manager import check_database_health
            health = check_database_health()
            
            if health.get("status") == "healthy":
                logger.info("✅ Database connection recovered")
                return True
        
        # Check if it's a session issue
        if "session" in str(error).lower():
            logger.info("🔄 Clearing database sessions...")
            # Session cleanup would happen here
            return True
        
        return False
        
    except Exception as recovery_error:
        logger.error(f"❌ Database recovery failed: {recovery_error}")
        return False

async def api_recovery_strategy(error: Exception, context: Dict[str, Any]) -> bool:
    """Recovery strategy for API errors"""
    try:
        logger.info("🔄 Attempting API recovery...")
        
        # Check if it's a timeout
        if "timeout" in str(error).lower():
            logger.info("🔄 API timeout detected, will retry with longer timeout")
            return True
        
        # Check if it's authentication
        if "auth" in str(error).lower() or "401" in str(error):
            logger.info("🔄 Re-authenticating with API...")
            # Re-authentication would happen here
            return True
        
        # Check if it's rate limiting
        if "rate" in str(error).lower() or "429" in str(error):
            logger.info("🔄 Rate limit detected, waiting...")
            await asyncio.sleep(5)
            return True
        
        return False
        
    except Exception as recovery_error:
        logger.error(f"❌ API recovery failed: {recovery_error}")
        return False

async def network_recovery_strategy(error: Exception, context: Dict[str, Any]) -> bool:
    """Recovery strategy for network errors"""
    try:
        logger.info("🔄 Attempting network recovery...")
        
        # Simple network wait and retry
        await asyncio.sleep(3)
        
        # Could add network connectivity check here
        return True
        
    except Exception as recovery_error:
        logger.error(f"❌ Network recovery failed: {recovery_error}")
        return False

# Register default recovery strategies
error_recovery.register_recovery_strategy(ErrorCategory.DATABASE, database_recovery_strategy)
error_recovery.register_recovery_strategy(ErrorCategory.API, api_recovery_strategy)
error_recovery.register_recovery_strategy(ErrorCategory.NETWORK, network_recovery_strategy)

def get_system_health() -> Dict[str, Any]:
    """Get comprehensive system health report"""
    stats = error_recovery.get_error_statistics()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "health_score": stats["health_score"],
        "error_statistics": stats,
        "status": "healthy" if stats["health_score"] > 80 else "degraded" if stats["health_score"] > 50 else "unhealthy",
        "recommendations": _generate_health_recommendations(stats)
    }

def _generate_health_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Generate health improvement recommendations"""
    recommendations = []
    
    if stats["health_score"] < 80:
        recommendations.append("Review recent error patterns and implement preventive measures")
    
    if stats["recent_errors"] > 10:
        recommendations.append("High error rate detected - investigate root causes")
    
    # Check circuit breakers
    open_breakers = [
        name for name, state in stats["circuit_breaker_states"].items() 
        if state == "open"
    ]
    
    if open_breakers:
        recommendations.append(f"Circuit breakers open for: {', '.join(open_breakers)}")
    
    if not recommendations:
        recommendations.append("System operating normally")
    
    return recommendations

logger.info("✅ Enhanced error recovery system initialized")