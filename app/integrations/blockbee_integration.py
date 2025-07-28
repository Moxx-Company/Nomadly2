"""
BlockBee (Payment Gateway) API Integration for Nomadly3
Complete implementation for cryptocurrency payment verification and processing
"""

import logging
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from ..core.config import config
from ..repositories.external_integration_repo import APIUsageLogRepository

logger = logging.getLogger(__name__)

class BlockBeeAPI:
    """Complete BlockBee API integration for cryptocurrency payments"""
    
    def __init__(self):
        self.api_key = config.BLOCKBEE_API_KEY
        self.base_url = "https://api.blockbee.io"
        
        # Repository dependencies
        self.api_usage_repo = APIUsageLogRepository()
        
        # Supported cryptocurrencies
        self.supported_cryptos = {
            'btc': 'Bitcoin',
            'eth': 'Ethereum', 
            'ltc': 'Litecoin',
            'doge': 'Dogecoin'
        }
    
    async def create_payment_address(self, cryptocurrency: str, callback_url: str, 
                                   order_id: str, user_id: int = None) -> Dict[str, Any]:
        """Create payment address for cryptocurrency payment"""
        start_time = datetime.now()
        
        if cryptocurrency not in self.supported_cryptos:
            return {
                "success": False,
                "error": f"Unsupported cryptocurrency: {cryptocurrency}"
            }
        
        params = {
            "callback": callback_url,
            "apikey": self.api_key,
            "order_id": order_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{cryptocurrency}/create",
                    params=params
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/{cryptocurrency}/create",
                        method="GET",
                        status=response.status,
                        request_data=params,
                        response_data=response_data,
                        response_time_ms=response_time,
                        user_id=user_id
                    )
                    
                    if response.status == 200 and response_data.get("status") == "success":
                        payment_data = response_data
                        
                        logger.info(f"Successfully created {cryptocurrency.upper()} payment address for order {order_id}")
                        
                        return {
                            "success": True,
                            "payment_address": payment_data.get("address_in"),
                            "qr_code": payment_data.get("qr_code"),
                            "cryptocurrency": cryptocurrency,
                            "order_id": order_id,
                            "callback_url": callback_url,
                            "blockbee_data": payment_data
                        }
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(f"Failed to create payment address for {cryptocurrency}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "blockbee_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception creating payment address for {cryptocurrency}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def check_payment_status(self, cryptocurrency: str, payment_address: str) -> Dict[str, Any]:
        """Check payment status for a cryptocurrency address"""
        start_time = datetime.now()
        
        params = {
            "apikey": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{cryptocurrency}/logs",
                    params=params
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/{cryptocurrency}/logs",
                        method="GET",
                        status=response.status,
                        request_data=params,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("status") == "success":
                        # Find payment for specific address
                        logs = response_data.get("data", [])
                        for log in logs:
                            if log.get("address_in") == payment_address:
                                return {
                                    "success": True,
                                    "payment_found": True,
                                    "amount_received": Decimal(str(log.get("value_received", 0))),
                                    "confirmations": log.get("confirmations", 0),
                                    "transaction_hash": log.get("txid_in"),
                                    "status": log.get("status"),
                                    "blockbee_data": log
                                }
                        
                        # No payment found for this address
                        return {
                            "success": True,
                            "payment_found": False,
                            "amount_received": Decimal('0'),
                            "confirmations": 0
                        }
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(f"Failed to check payment status for {cryptocurrency}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "blockbee_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception checking payment status for {cryptocurrency}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_balance(self, cryptocurrency: str, address: str) -> Dict[str, Any]:
        """Get balance for a cryptocurrency address"""
        start_time = datetime.now()
        
        params = {
            "apikey": self.api_key
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{cryptocurrency}/balance",
                    params={**params, "address": address}
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/{cryptocurrency}/balance",
                        method="GET",
                        status=response.status,
                        request_data=params,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("status") == "success":
                        balance = Decimal(str(response_data.get("balance", 0)))
                        
                        return {
                            "success": True,
                            "balance": balance,
                            "address": address,
                            "cryptocurrency": cryptocurrency,
                            "blockbee_data": response_data
                        }
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(f"Failed to get balance for {cryptocurrency} address {address}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "blockbee_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception getting balance for {cryptocurrency} address {address}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_transaction_info(self, cryptocurrency: str, transaction_hash: str) -> Dict[str, Any]:
        """Get detailed transaction information"""
        start_time = datetime.now()
        
        params = {
            "apikey": self.api_key,
            "txid": transaction_hash
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/{cryptocurrency}/tx",
                    params=params
                ) as response:
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    response_data = await response.json()
                    
                    # Log API usage
                    await self._log_api_usage(
                        endpoint=f"/{cryptocurrency}/tx",
                        method="GET",
                        status=response.status,
                        request_data=params,
                        response_data=response_data,
                        response_time_ms=response_time
                    )
                    
                    if response.status == 200 and response_data.get("status") == "success":
                        tx_data = response_data.get("data", {})
                        
                        return {
                            "success": True,
                            "transaction_hash": transaction_hash,
                            "confirmations": tx_data.get("confirmations", 0),
                            "amount": Decimal(str(tx_data.get("value", 0))),
                            "fee": Decimal(str(tx_data.get("fee", 0))),
                            "timestamp": tx_data.get("timestamp"),
                            "block_height": tx_data.get("block_height"),
                            "blockbee_data": tx_data
                        }
                    else:
                        error_msg = response_data.get("error", "Unknown error")
                        logger.error(f"Failed to get transaction info for {transaction_hash}: {error_msg}")
                        
                        return {
                            "success": False,
                            "error": error_msg,
                            "blockbee_response": response_data
                        }
                        
        except Exception as e:
            logger.error(f"Exception getting transaction info for {transaction_hash}: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    async def get_supported_cryptocurrencies(self) -> List[Dict[str, Any]]:
        """Get list of supported cryptocurrencies"""
        return [
            {
                "code": code,
                "name": name,
                "min_confirmations": self._get_min_confirmations(code)
            }
            for code, name in self.supported_cryptos.items()
        ]
    
    def _get_min_confirmations(self, cryptocurrency: str) -> int:
        """Get minimum confirmations required for each cryptocurrency"""
        confirmations = {
            'btc': 1,
            'eth': 12,
            'ltc': 6,
            'doge': 20
        }
        return confirmations.get(cryptocurrency, 1)
    
    async def _log_api_usage(self, endpoint: str, method: str, status: int,
                            request_data: Dict[str, Any] = None,
                            response_data: Dict[str, Any] = None,
                            response_time_ms: int = None,
                            user_id: int = None):
        """Log API usage for monitoring"""
        try:
            self.api_usage_repo.log_api_call(
                service_name="blockbee",
                api_endpoint=endpoint,
                http_method=method,
                response_status=status,
                user_id=user_id,
                request_data=request_data,
                response_data=response_data,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error(f"Failed to log API usage: {str(e)}")
    
    async def validate_address(self, cryptocurrency: str, address: str) -> Dict[str, Any]:
        """Validate a cryptocurrency address format"""
        # Basic validation - could be enhanced with specific format checks
        if not address or len(address) < 10:
            return {
                "success": False,
                "valid": False,
                "error": "Address too short"
            }
        
        # Cryptocurrency-specific validation
        validation_rules = {
            'btc': lambda addr: addr.startswith(('1', '3', 'bc1')),
            'eth': lambda addr: addr.startswith('0x') and len(addr) == 42,
            'ltc': lambda addr: addr.startswith(('L', 'M', '3', 'ltc1')),
            'doge': lambda addr: addr.startswith('D')
        }
        
        if cryptocurrency in validation_rules:
            is_valid = validation_rules[cryptocurrency](address)
            return {
                "success": True,
                "valid": is_valid,
                "cryptocurrency": cryptocurrency,
                "address": address
            }
        
        return {
            "success": False,
            "error": f"Validation not available for {cryptocurrency}"
        }