#!/usr/bin/env python3
"""
Network Failure Handling System
Comprehensive network failure detection, retry mechanisms, and graceful degradation
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NetworkStatus(Enum):
    """Network status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    OFFLINE = "offline"

class RetryStrategy(Enum):
    """Retry strategy types"""
    EXPONENTIAL_BACKOFF = "exponential"
    LINEAR_BACKOFF = "linear"
    IMMEDIATE = "immediate"
    CIRCUIT_BREAKER = "circuit_breaker"

@dataclass
class NetworkConfig:
    """Network configuration for different services"""
    service_name: str
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    backoff_factor: float = 1.5
    circuit_breaker_threshold: int = 5
    circuit_breaker_reset_time: int = 300  # 5 minutes
    health_check_interval: int = 60  # 1 minute

@dataclass
class FailureRecord:
    """Record of network failures"""
    timestamp: datetime
    error_type: str
    error_message: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None

@dataclass
class ServiceHealth:
    """Health status of a service"""
    service_name: str
    status: NetworkStatus = NetworkStatus.HEALTHY
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    response_times: List[float] = field(default_factory=list)
    failure_history: List[FailureRecord] = field(default_factory=list)
    circuit_breaker_until: Optional[datetime] = None

class NetworkFailureHandler:
    """Comprehensive network failure handling system"""
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.configurations: Dict[str, NetworkConfig] = self._initialize_service_configs()
        self.global_timeout_config = {
            'openprovider_auth': 45.0,
            'openprovider_domain': 60.0,
            'cloudflare_zone': 30.0,
            'cloudflare_dns': 20.0,
            'blockbee_payment': 30.0,
            'blockbee_rates': 15.0,
            'default': 30.0
        }
    
    def _initialize_service_configs(self) -> Dict[str, NetworkConfig]:
        """Initialize network configurations for all services"""
        return {
            'openprovider': NetworkConfig(
                service_name='openprovider',
                base_url='https://api.openprovider.eu',
                timeout=60,
                max_retries=3,
                retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                backoff_factor=2.0,
                circuit_breaker_threshold=5
            ),
            
            'cloudflare': NetworkConfig(
                service_name='cloudflare',
                base_url='https://api.cloudflare.com',
                timeout=30.0,
                max_retries=4,
                retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                backoff_factor=1.5,
                circuit_breaker_threshold=3
            ),
            
            'blockbee': NetworkConfig(
                service_name='blockbee',
                base_url='https://api.blockbee.io',
                timeout=30.0,
                max_retries=3,
                retry_strategy=RetryStrategy.LINEAR_BACKOFF,
                backoff_factor=1.0,
                circuit_breaker_threshold=4
            ),
            
            'fastforex': NetworkConfig(
                service_name='fastforex',
                base_url='https://api.fastforex.io',
                timeout=15.0,
                max_retries=2,
                retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                backoff_factor=1.2,
                circuit_breaker_threshold=3
            )
        }
    
    def get_service_health(self, service_name: str) -> ServiceHealth:
        """Get or create service health record"""
        if service_name not in self.services:
            self.services[service_name] = ServiceHealth(service_name=service_name)
        return self.services[service_name]
    
    def get_service_config(self, service_name: str) -> NetworkConfig:
        """Get service configuration"""
        return self.configurations.get(service_name, NetworkConfig(service_name=service_name))
    
    def record_success(self, service_name: str, response_time: float):
        """Record successful network operation"""
        health = self.get_service_health(service_name)
        config = self.get_service_config(service_name)
        
        health.last_success = datetime.now()
        health.failure_count = max(0, health.failure_count - 1)  # Reduce failure count
        health.response_times.append(response_time)
        
        # Keep only recent response times (last 100)
        if len(health.response_times) > 100:
            health.response_times = health.response_times[-100:]
        
        # Update status based on performance
        avg_response_time = sum(health.response_times) / len(health.response_times)
        
        if health.failure_count == 0 and avg_response_time < config.timeout * 0.5:
            health.status = NetworkStatus.HEALTHY
        elif health.failure_count < config.circuit_breaker_threshold // 2:
            health.status = NetworkStatus.DEGRADED
        
        logger.info(f"✅ {service_name} success: {response_time:.2f}s (avg: {avg_response_time:.2f}s)")
    
    def record_failure(self, service_name: str, error: Exception, response_time: Optional[float] = None, status_code: Optional[int] = None):
        """Record network failure"""
        health = self.get_service_health(service_name)
        config = self.get_service_config(service_name)
        
        failure_record = FailureRecord(
            timestamp=datetime.now(),
            error_type=type(error).__name__,
            error_message=str(error),
            response_time=response_time,
            status_code=status_code
        )
        
        health.last_failure = datetime.now()
        health.failure_count += 1
        health.failure_history.append(failure_record)
        
        # Keep only recent failures (last 50)
        if len(health.failure_history) > 50:
            health.failure_history = health.failure_history[-50:]
        
        # Update status based on failure count
        if health.failure_count >= config.circuit_breaker_threshold:
            health.status = NetworkStatus.OFFLINE
            health.circuit_breaker_until = datetime.now() + timedelta(seconds=config.circuit_breaker_reset_time)
            logger.warning(f"🚫 Circuit breaker tripped for {service_name} until {health.circuit_breaker_until}")
        elif health.failure_count >= config.circuit_breaker_threshold // 2:
            health.status = NetworkStatus.FAILING
        else:
            health.status = NetworkStatus.DEGRADED
        
        logger.error(f"❌ {service_name} failure #{health.failure_count}: {error}")
    
    def is_circuit_breaker_open(self, service_name: str) -> bool:
        """Check if circuit breaker is open"""
        health = self.get_service_health(service_name)
        
        if health.circuit_breaker_until and datetime.now() < health.circuit_breaker_until:
            return True
        
        # Reset circuit breaker if time has passed
        if health.circuit_breaker_until and datetime.now() >= health.circuit_breaker_until:
            health.circuit_breaker_until = None
            health.failure_count = 0
            health.status = NetworkStatus.DEGRADED  # Start with degraded status
            logger.info(f"🔄 Circuit breaker reset for {service_name}")
        
        return False
    
    def calculate_retry_delay(self, service_name: str, attempt: int) -> float:
        """Calculate retry delay based on strategy"""
        config = self.get_service_config(service_name)
        
        if config.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return config.backoff_factor ** attempt
        elif config.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            return config.backoff_factor * attempt
        elif config.retry_strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        
        return 1.0  # Default
    
    async def execute_with_retry(
        self,
        service_name: str,
        operation: Callable,
        *args,
        operation_name: str = "network_operation",
        **kwargs
    ) -> Dict[str, Any]:
        """Execute network operation with retry logic and failure handling"""
        config = self.get_service_config(service_name)
        health = self.get_service_health(service_name)
        
        # Check circuit breaker
        if self.is_circuit_breaker_open(service_name):
            return {
                'success': False,
                'error': 'Circuit breaker open',
                'user_message': f'🔧 {service_name.title()} service is temporarily offline for maintenance. Please try again in a few minutes.',
                'fallback_available': True
            }
        
        last_error = None
        
        for attempt in range(config.max_retries + 1):
            start_time = time.time()
            
            try:
                # Execute the operation
                if asyncio.iscoroutinefunction(operation):
                    result = await operation(*args, **kwargs)
                else:
                    result = operation(*args, **kwargs)
                
                # Record success
                response_time = time.time() - start_time
                self.record_success(service_name, response_time)
                
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'response_time': response_time
                }
                
            except Exception as error:
                last_error = error
                response_time = time.time() - start_time
                
                # Record failure
                status_code = getattr(error, 'status_code', None) or getattr(error, 'code', None)
                self.record_failure(service_name, error, response_time, status_code)
                
                # Check if we should retry
                if attempt < config.max_retries:
                    # Calculate retry delay
                    delay = self.calculate_retry_delay(service_name, attempt + 1)
                    
                    logger.warning(f"🔄 {service_name} {operation_name} failed (attempt {attempt + 1}/{config.max_retries + 1}). Retrying in {delay:.1f}s...")
                    
                    if delay > 0:
                        await asyncio.sleep(delay)
                    
                    continue
                else:
                    # All retries exhausted
                    break
        
        # Prepare failure response
        return self._prepare_failure_response(service_name, last_error, config.max_retries + 1)
    
    def _prepare_failure_response(self, service_name: str, error: Exception, total_attempts: int) -> Dict[str, Any]:
        """Prepare failure response after all retries exhausted"""
        health = self.get_service_health(service_name)
        
        # Generate user-friendly message based on service and error type
        user_message = self._get_user_friendly_failure_message(service_name, error, health.status)
        
        return {
            'success': False,
            'error': str(error),
            'service': service_name,
            'status': health.status.value,
            'total_attempts': total_attempts,
            'user_message': user_message,
            'fallback_available': self._has_fallback_service(service_name),
            'support_contact': health.status == NetworkStatus.OFFLINE
        }
    
    def _get_user_friendly_failure_message(self, service_name: str, error: Exception, status: NetworkStatus) -> str:
        """Generate user-friendly failure message"""
        error_str = str(error).lower()
        
        # Service-specific messages
        if service_name == 'openprovider':
            if 'timeout' in error_str:
                return "🌐 Domain registrar is taking longer than usual. We're working to resolve this quickly."
            elif 'authentication' in error_str:
                return "🔐 Domain registrar authentication issue. Our team is resolving this."
            else:
                return "🌍 Domain registrar temporarily unavailable. Trying alternative methods..."
        
        elif service_name == 'cloudflare':
            if 'timeout' in error_str:
                return "☁️ DNS service responding slowly. Your request is still being processed."
            else:
                return "☁️ DNS service temporarily unavailable. Checking backup systems..."
        
        elif service_name == 'blockbee':
            if 'timeout' in error_str:
                return "💰 Payment system taking longer than usual. Your transaction is secure."
            else:
                return "💰 Payment system temporarily unavailable. Checking alternative payment methods..."
        
        # Generic messages based on status
        if status == NetworkStatus.OFFLINE:
            return f"🔧 {service_name.title()} service is temporarily offline. Please try again in a few minutes."
        elif status == NetworkStatus.FAILING:
            return f"⚠️ {service_name.title()} service is experiencing issues. We're working to restore full functionality."
        elif status == NetworkStatus.DEGRADED:
            return f"🐌 {service_name.title()} service is running slower than usual. Please be patient while we process your request."
        
        return f"🌐 {service_name.title()} service temporarily unavailable. Please try again shortly."
    
    def _has_fallback_service(self, service_name: str) -> bool:
        """Check if service has fallback options"""
        fallback_services = {
            'fastforex': True,  # Has BlockBee and static rates as fallback
            'blockbee': True,   # Has static rates as fallback
            'openprovider': False,  # No fallback for domain registration
            'cloudflare': False     # No fallback for DNS management
        }
        
        return fallback_services.get(service_name, False)
    
    def get_service_status_summary(self) -> Dict[str, Any]:
        """Get summary of all service statuses"""
        summary = {
            'overall_health': 'healthy',
            'services': {},
            'degraded_services': [],
            'offline_services': []
        }
        
        for service_name, health in self.services.items():
            service_info = {
                'status': health.status.value,
                'failure_count': health.failure_count,
                'last_success': health.last_success.isoformat() if health.last_success else None,
                'last_failure': health.last_failure.isoformat() if health.last_failure else None,
                'avg_response_time': sum(health.response_times) / len(health.response_times) if health.response_times else None
            }
            
            summary['services'][service_name] = service_info
            
            if health.status == NetworkStatus.DEGRADED:
                summary['degraded_services'].append(service_name)
            elif health.status in [NetworkStatus.FAILING, NetworkStatus.OFFLINE]:
                summary['offline_services'].append(service_name)
        
        # Determine overall health
        if summary['offline_services']:
            summary['overall_health'] = 'critical'
        elif summary['degraded_services']:
            summary['overall_health'] = 'degraded'
        
        return summary
    
    async def health_check_all_services(self) -> Dict[str, NetworkStatus]:
        """Perform health check on all configured services"""
        health_results = {}
        
        for service_name, config in self.configurations.items():
            try:
                # Simple connectivity test
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    start_time = time.time()
                    async with session.get(f"{config.base_url}/", ssl=False) as response:
                        response_time = time.time() - start_time
                        
                        if response.status < 500:
                            self.record_success(service_name, response_time)
                            health_results[service_name] = NetworkStatus.HEALTHY
                        else:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status
                            )
            
            except Exception as error:
                self.record_failure(service_name, error)
                health = self.get_service_health(service_name)
                health_results[service_name] = health.status
        
        return health_results

# Global network failure handler instance
network_handler = NetworkFailureHandler()

# Decorator for automatic network failure handling
def with_network_retry(service_name: str, operation_name: str = "network_operation"):
    """Decorator for automatic network failure handling"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await network_handler.execute_with_retry(
                service_name, func, *args, operation_name=operation_name, **kwargs
            )
        return wrapper
    return decorator

async def test_network_failure_handling():
    """Test network failure handling system"""
    print("🧪 TESTING NETWORK FAILURE HANDLING")
    print("=" * 50)
    
    handler = NetworkFailureHandler()
    
    # Test service configurations
    print("📋 Service Configurations:")
    for service_name, config in handler.configurations.items():
        print(f"{service_name:15} → Timeout: {config.timeout}s, Max Retries: {config.max_retries}")
    
    # Test retry delay calculations
    print(f"\n🔄 Retry Delay Tests:")
    for service_name in handler.configurations.keys():
        delays = [handler.calculate_retry_delay(service_name, i) for i in range(1, 4)]
        print(f"{service_name:15} → Delays: {[f'{d:.1f}s' for d in delays]}")
    
    # Simulate some failures and successes
    print(f"\n📊 Simulating Network Events:")
    
    # Simulate CloudFlare success
    handler.record_success('cloudflare', 0.5)
    print("✅ CloudFlare success recorded")
    
    # Simulate OpenProvider failures
    for i in range(3):
        handler.record_failure('openprovider', Exception(f"Connection timeout {i+1}"))
    print("❌ OpenProvider failures recorded")
    
    # Get status summary
    summary = handler.get_service_status_summary()
    print(f"\n📈 Service Status Summary:")
    print(f"Overall Health: {summary['overall_health']}")
    for service, info in summary['services'].items():
        print(f"{service:15} → {info['status']} (failures: {info['failure_count']})")

if __name__ == "__main__":
    asyncio.run(test_network_failure_handling())