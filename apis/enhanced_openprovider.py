"""
Enhanced OpenProvider API with comprehensive timeout optimization
Implements retry mechanisms, exponential backoff, and operation-specific timeouts
"""

import asyncio
import aiohttp
import time
import random
import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TimeoutConfig:
    """Timeout configuration for different operation types"""
    connect_timeout: int = 15
    read_timeout: int = 90
    total_timeout: int = 180
    
    # Operation-specific timeouts
    authentication_timeout: int = 45
    customer_creation_timeout: int = 90
    domain_registration_timeout: int = 120
    simple_query_timeout: int = 15

@dataclass 
class RetryConfig:
    """Retry configuration with exponential backoff"""
    max_retries: int = 3
    base_delay: float = 2.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True

class EnhancedOpenProviderAPI:
    """Enhanced OpenProvider API with comprehensive timeout handling"""
    
    def __init__(self):
        self.base_url = "https://api.openprovider.eu"
        self.username = os.getenv("OPENPROVIDER_USERNAME")
        self.password = os.getenv("OPENPROVIDER_PASSWORD")
        
        if not self.username or not self.password:
            raise Exception("OpenProvider credentials required: OPENPROVIDER_USERNAME and OPENPROVIDER_PASSWORD")
        
        self.timeout_config = TimeoutConfig()
        self.retry_config = RetryConfig()
        self.session = None
        self.token = None
        self.token_expires_at = 0
        
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create aiohttp session with optimized timeout settings"""
        
        # Create timeout configuration
        timeout = aiohttp.ClientTimeout(
            total=self.timeout_config.total_timeout,
            connect=self.timeout_config.connect_timeout,
            sock_read=self.timeout_config.read_timeout
        )
        
        # Create connector with optimized settings
        connector = aiohttp.TCPConnector(
            limit=100,                    # Connection pool size
            limit_per_host=30,           # Per-host connection limit
            ttl_dns_cache=300,           # DNS cache TTL
            use_dns_cache=True,          # Enable DNS caching
            keepalive_timeout=API_TIMEOUT,        # Keep connections alive
            enable_cleanup_closed=True   # Clean up closed connections
        )
        
        return aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': 'Nomadly2-Bot/1.4',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        )
    
    async def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff and jitter"""
        
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        if self.retry_config.jitter:
            # Add ±25% jitter to prevent thundering herd
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    async def _execute_with_retry(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute operation with retry logic and timeout handling"""
        
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                logger.info(f"🔄 {operation_name} attempt {attempt + 1}/{self.retry_config.max_retries + 1}")
                
                # Execute the operation
                result = await operation_func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✅ {operation_name} succeeded on attempt {attempt + 1}")
                
                return result
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"⏰ {operation_name} timeout on attempt {attempt + 1}: {e}")
                
            except aiohttp.ClientError as e:
                last_exception = e
                logger.warning(f"🌐 {operation_name} client error on attempt {attempt + 1}: {e}")
                
            except Exception as e:
                last_exception = e
                logger.error(f"❌ {operation_name} unexpected error on attempt {attempt + 1}: {e}")
                
                # Don't retry on non-retryable errors
                if not self._is_retryable_error(e):
                    raise
            
            # Calculate and apply retry delay (except on last attempt)
            if attempt < self.retry_config.max_retries:
                delay = await self._calculate_retry_delay(attempt)
                logger.info(f"⏳ Retrying {operation_name} in {delay:.1f}s...")
                await asyncio.sleep(delay)
        
        # All retries exhausted
        logger.error(f"❌ {operation_name} failed after {self.retry_config.max_retries + 1} attempts")
        raise last_exception
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable"""
        
        retryable_patterns = [
            'timeout', 'connection', 'temporary', 'server error',
            'rate limit', '5', 'busy', 'unavailable'
        ]
        
        error_str = str(error).lower()
        return any(pattern in error_str for pattern in retryable_patterns)
    
    async def authenticate_with_timeout(self) -> bool:
        """Authenticate with OpenProvider using optimized timeouts"""
        
        async def _auth_operation():
            if not self.session:
                self.session = await self._create_session()
            
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            # Use authentication-specific timeout
            auth_timeout = aiohttp.ClientTimeout(
                total=self.timeout_config.authentication_timeout
            )
            
            async with self.session.post(
                f"{self.base_url}/v1beta/auth/login",
                json=auth_data,
                timeout=auth_timeout
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.token = result.get("data", {}).get("token")
                    self.token_expires_at = time.time() + 3600  # 1 hour
                    
                    # Update session headers with token
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.token}"
                    })
                    
                    logger.info("✅ Enhanced OpenProvider authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    raise Exception(f"Authentication failed: {response.status} - {error_text}")
        
        return await self._execute_with_retry("Authentication", _auth_operation)
    
    async def create_customer_with_timeout(self, customer_data: Dict[str, Any]) -> str:
        """Create customer with enhanced timeout handling"""
        
        async def _customer_creation():
            # Ensure we're authenticated
            if not self.token or time.time() >= self.token_expires_at:
                await self.authenticate_with_timeout()
            
            # Use customer creation specific timeout
            customer_timeout = aiohttp.ClientTimeout(
                total=self.timeout_config.customer_creation_timeout
            )
            
            logger.info(f"🧑 Creating OpenProvider customer with {self.timeout_config.customer_creation_timeout}s timeout")
            
            async with self.session.post(
                f"{self.base_url}/v1beta/customers",
                json=customer_data,
                timeout=customer_timeout
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    customer_handle = result.get("data", {}).get("handle")
                    
                    if not customer_handle:
                        raise Exception("No customer handle returned")
                    
                    logger.info(f"✅ Customer created successfully: {customer_handle}")
                    return customer_handle
                else:
                    error_text = await response.text()
                    raise Exception(f"Customer creation failed: {response.status} - {error_text}")
        
        return await self._execute_with_retry("Customer Creation", _customer_creation)
    
    async def register_domain_with_timeout(self, domain_data: Dict[str, Any]) -> str:
        """Register domain with comprehensive timeout handling"""
        
        async def _domain_registration():
            # Ensure we're authenticated
            if not self.token or time.time() >= self.token_expires_at:
                await self.authenticate_with_timeout()
            
            # Use domain registration specific timeout
            domain_timeout = aiohttp.ClientTimeout(
                total=self.timeout_config.domain_registration_timeout
            )
            
            logger.info(f"🌐 Registering domain with {self.timeout_config.domain_registration_timeout}s timeout")
            
            async with self.session.post(
                f"{self.base_url}/v1beta/domains",
                json=domain_data,
                timeout=domain_timeout
            ) as response:
                
                if response.status in [200, 201]:
                    result = await response.json()
                    domain_id = result.get("data", {}).get("id")
                    
                    if not domain_id:
                        raise Exception("No domain ID returned")
                    
                    logger.info(f"✅ Domain registered successfully: {domain_id}")
                    return str(domain_id)
                else:
                    error_text = await response.text()
                    raise Exception(f"Domain registration failed: {response.status} - {error_text}")
        
        return await self._execute_with_retry("Domain Registration", _domain_registration)
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            logger.info("🔒 Enhanced OpenProvider session closed")

# Global instance for use throughout the application
enhanced_openprovider_api = EnhancedOpenProviderAPI()