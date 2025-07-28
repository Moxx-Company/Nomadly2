"""
FastForex API Integration for Nomadly3
Complete implementation for USD to cryptocurrency conversion and rate caching
"""

import logging
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from ..core.config import config
from ..core.external_services import FastForexServiceInterface
from ..repositories.external_integration_repo import (
    FastForexIntegrationRepository, APIUsageLogRepository
)

logger = logging.getLogger(__name__)

class FastForexAPI(FastForexServiceInterface):
    """Complete FastForex API integration for currency conversion"""
    
    def __init__(self):
        self.api_key = config.FASTFOREX_API_KEY
        self.base_url = "https://api.fastforex.io"
        
        # Repository dependencies
        self.fastforex_repo = FastForexIntegrationRepository()
        self.api_usage_repo = APIUsageLogRepository()
        
        # Rate caching settings
        self.cache_duration_minutes = 5  # Cache rates for 5 minutes
        
        # Supported currency pairs
        self.supported_currencies = [
            'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR'
        ]
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get current exchange rate between currencies with caching"""
        # Check cache first
        cached_rate = self.fastforex_repo.get_cached_rate(from_currency, to_currency, self.cache_duration_minutes)
        if cached_rate:
            logger.info(f"Using cached exchange rate {from_currency}/{to_currency}: {cached_rate.exchange_rate}")
            return {
                "success": True,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "exchange_rate": cached_rate.exchange_rate,
                "rate_timestamp": cached_rate.rate_timestamp,
                "cached": True
            }
        
        # Fetch fresh rate from API
        start_time = datetime.now()
        
        params = {
            "api_key": self.api_key,
            "from": from_currency,
            "to": to_currency
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/convert",
                    params=params
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/convert",
                        method="GET",
                        status=response.status,
                        request_data=params,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and "result" in response_data:
                        exchange_rate = Decimal(str(response_data["result"][to_currency]))
                        rate_timestamp = datetime.now()
                        
                        # Store rate in cache
                        self.fastforex_repo.store_exchange_rate(
                            from_currency=from_currency,
                            to_currency=to_currency,
                            exchange_rate=exchange_rate,
                            rate_timestamp=rate_timestamp,
                            api_response=response_data
                        )
                        
                        logger.info(f"Fetched fresh exchange rate {from_currency}/{to_currency}: {exchange_rate}")
                        
                        return {
                            "success": True,
                            "from_currency": from_currency,
                            "to_currency": to_currency,
                            "exchange_rate": exchange_rate,
                            "rate_timestamp": rate_timestamp,
                            "cached": False,
                            "fastforex_data": response_data
                        }
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(f"Failed to get exchange rate {from_currency}/{to_currency}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "fastforex_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception getting exchange rate {from_currency}/{to_currency}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def convert_amount(self, amount: Decimal, from_currency: str, 
                            to_currency: str) -> Dict[str, Any]:
        """Convert amount from one currency to another"""
        # Get exchange rate
        rate_result = await self.get_exchange_rate(from_currency, to_currency)
        
        if not rate_result["success"]:
            return rate_result
        
        exchange_rate = rate_result["exchange_rate"]
        converted_amount = amount * exchange_rate
        
        logger.info(f"Converted {amount} {from_currency} to {converted_amount} {to_currency} (rate: {exchange_rate})")
        
        return {
            "success": True,
            "original_amount": amount,
            "converted_amount": converted_amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": exchange_rate,
            "rate_timestamp": rate_result["rate_timestamp"],
            "cached": rate_result["cached"]
        }
    
    async def get_supported_currencies(self) -> List[str]:
        """Get list of supported currencies"""
        return self.supported_currencies.copy()
    
    async def get_multiple_rates(self, from_currency: str, to_currencies: List[str]) -> Dict[str, Any]:
        """Get exchange rates for multiple target currencies"""
        start_time = datetime.now()
        
        # Build comma-separated list of target currencies
        to_currencies_str = ",".join(to_currencies)
        
        params = {
            "api_key": self.api_key,
            "from": from_currency,
            "to": to_currencies_str
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/fetch-multi",
                    params=params
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint="/fetch-multi",
                        method="GET",
                        status=response.status,
                        request_data=params,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and "results" in response_data:
                        rates = {}
                        rate_timestamp = datetime.now()
                        
                        # Process and cache each rate
                        for to_currency, rate_value in response_data["results"].items():
                            exchange_rate = Decimal(str(rate_value))
                            rates[to_currency] = exchange_rate
                            
                            # Store in cache
                            self.fastforex_repo.store_exchange_rate(
                                from_currency=from_currency,
                                to_currency=to_currency,
                                exchange_rate=exchange_rate,
                                rate_timestamp=rate_timestamp,
                                api_response=response_data
                            )
                        
                        logger.info(f"Fetched multiple exchange rates from {from_currency}: {list(rates.keys())}")
                        
                        return {
                            "success": True,
                            "from_currency": from_currency,
                            "rates": rates,
                            "rate_timestamp": rate_timestamp,
                            "fastforex_data": response_data
                        }
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(f"Failed to get multiple exchange rates from {from_currency}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "fastforex_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception getting multiple exchange rates from {from_currency}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def convert_usd_to_crypto_estimate(self, usd_amount: Decimal, cryptocurrency: str) -> Dict[str, Any]:
        """Convert USD to cryptocurrency amount (estimated using forex rates)"""
        # This is an approximation since FastForex doesn't have real crypto rates
        # In production, you'd use a dedicated crypto API like CoinGecko or similar
        
        # Crypto approximation rates (these would come from a crypto API in production)
        crypto_approximations = {
            'BTC': Decimal('45000'),    # $45,000 per BTC
            'ETH': Decimal('2800'),     # $2,800 per ETH  
            'LTC': Decimal('90'),       # $90 per LTC
            'DOGE': Decimal('0.08')     # $0.08 per DOGE
        }
        
        if cryptocurrency.upper() not in crypto_approximations:
            return {
                "success": False,
                "error": f"Cryptocurrency {cryptocurrency} not supported for estimation"
            }
        
        crypto_price = crypto_approximations[cryptocurrency.upper()]
        crypto_amount = usd_amount / crypto_price
        
        logger.info(f"Estimated conversion: ${usd_amount} USD ≈ {crypto_amount} {cryptocurrency.upper()}")
        
        return {
            "success": True,
            "usd_amount": usd_amount,
            "crypto_amount": crypto_amount,
            "cryptocurrency": cryptocurrency.upper(),
            "estimated_price": crypto_price,
            "note": "This is an estimated conversion. Actual crypto rates may vary."
        }
    
    async def get_historical_rates(self, from_currency: str, to_currency: str, 
                                  days_back: int = 30) -> Dict[str, Any]:
        """Get historical exchange rates"""
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        params = {
            "api_key": self.api_key,
            "from": from_currency,
            "to": to_currency,
            "date_from": start_date.strftime("%Y-%m-%d"),
            "date_to": end_date.strftime("%Y-%m-%d")
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/historical",
                    params=params
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and "results" in response_data:
                        historical_data = response_data["results"]
                        
                        logger.info(f"Retrieved {len(historical_data)} historical rates for {from_currency}/{to_currency}")
                        
                        return {
                            "success": True,
                            "from_currency": from_currency,
                            "to_currency": to_currency,
                            "date_range": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                            "historical_rates": historical_data,
                            "fastforex_data": response_data
                        }
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(f"Failed to get historical rates {from_currency}/{to_currency}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "fastforex_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception getting historical rates {from_currency}/{to_currency}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def cleanup_expired_rates(self, max_age_hours: int = 24) -> int:
        """Clean up expired cached rates"""
        try:
            deleted_count = self.fastforex_repo.cleanup_expired_rates(max_age_hours)
            logger.info(f"Cleaned up {deleted_count} expired exchange rates")
            return deleted_count
        except Exception as e:
            logger.error(f"Exception cleaning up expired rates: {str(e)}")
            return 0
    
    async def get_api_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            stats = self.api_usage_repo.get_service_usage_stats("fastforex", days)
            return {
                "success": True,
                "service": "fastforex",
                "period_days": days,
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Exception getting API usage stats: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get usage stats: {str(e)}"
            }
    
    async def _log_api_usage(self, endpoint: str, method: str, status: int,
                            request_data: Dict[str, Any] = None,
                            response_data: Dict[str, Any] = None,
                            response_time_ms: int = None):
        """Log API usage for monitoring"""
        try:
            self.api_usage_repo.log_api_call(
                service_name="fastforex",
                api_endpoint=endpoint,
                http_method=method,
                response_status=status,
                request_data=request_data,
                response_data=response_data,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
    
    async def get_rate_limits(self) -> Dict[str, Any]:
        """Get current API rate limit status"""
        try:
            # FastForex typically allows 1000 requests per month on free tier
            usage_stats = await self.get_api_usage_stats(30)
            
            if usage_stats["success"]:
                monthly_calls = usage_stats["stats"].get("total_calls", 0)
                remaining_calls = max(0, 1000 - monthly_calls)
                
                return {
                    "success": True,
                    "monthly_limit": 1000,
                    "monthly_used": monthly_calls,
                    "monthly_remaining": remaining_calls,
                    "percentage_used": round((monthly_calls / 1000) * 100, 2)
                }
            else:
                return usage_stats
                
        except Exception as e:
            logger.error(f"Exception getting rate limits: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get rate limits: {str(e)}"
            }