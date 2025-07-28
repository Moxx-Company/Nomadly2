"""
Dynopay API Integration for Nomadly2 Bot
Provides comprehensive payment processing through Dynopay platform
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DynopayAPI:
    """Dynopay API client for payment processing"""
    
    def __init__(self):
        self.api_key = os.getenv("DYNOPAY_API_KEY")
        self.base_url = "https://user-api.dynopay.com/api"
        self.timeout = 30
        
        if not self.api_key:
            logger.warning("⚠️ DYNOPAY_API_KEY not configured")
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request to Dynopay"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            # Base headers
            request_headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            # Add authorization token if provided
            if auth_token:
                request_headers["Authorization"] = f"Bearer {auth_token}"
            
            # Add custom headers
            if headers:
                request_headers.update(headers)
            
            logger.info(f"🔄 Dynopay {method.upper()} request to: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.lower() == "get":
                    response = await client.get(url, headers=request_headers)
                else:
                    response = await client.request(
                        method, url, 
                        json=data, 
                        headers=request_headers
                    )
                
                logger.info(f"📊 Dynopay response status: {response.status_code}")
                
                if response.status_code not in [200, 201]:
                    logger.error(f"❌ Dynopay API error: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                
                result = response.json()
                logger.info(f"✅ Dynopay response received")
                return {"success": True, "data": result}
                
        except httpx.TimeoutException:
            logger.error(f"⏰ Dynopay API timeout after {self.timeout}s")
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ Dynopay API error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_user(self, email: str, name: str, mobile: Optional[str] = None) -> Dict[str, Any]:
        """Create new user in Dynopay system"""
        try:
            logger.info(f"👤 Creating Dynopay user: {email}")
            
            user_data = {
                "email": email,
                "name": name
            }
            
            if mobile:
                user_data["mobile"] = mobile
            
            result = await self._make_request("POST", "/user/createUser", user_data)
            
            if result["success"]:
                data = result["data"]
                logger.info(f"✅ User created: {data.get('message', 'Success')}")
                return {
                    "success": True,
                    "token": data.get("data", {}).get("token"),
                    "customer_id": data.get("data", {}).get("customer_id"),
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ User creation failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Create user error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_payment(
        self, 
        user_token: str,
        amount: float, 
        redirect_uri: str,
        meta_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create payment link for user"""
        try:
            logger.info(f"💳 Creating payment for amount: ${amount}")
            
            payment_data = {
                "amount": amount,
                "redirect_uri": redirect_uri
            }
            
            if meta_data:
                payment_data["meta_data"] = meta_data
            
            result = await self._make_request(
                "POST", "/user/createPayment", 
                payment_data, 
                auth_token=user_token
            )
            
            if result["success"]:
                data = result["data"]
                logger.info(f"✅ Payment link created")
                return {
                    "success": True,
                    "redirect_url": data.get("data", {}).get("redirect_url"),
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Payment creation failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Create payment error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def add_funds(
        self, 
        user_token: str,
        amount: float, 
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Add funds to user wallet"""
        try:
            logger.info(f"💰 Adding funds: ${amount}")
            
            funds_data = {
                "amount": amount,
                "redirect_uri": redirect_uri
            }
            
            result = await self._make_request(
                "POST", "/user/addFunds", 
                funds_data, 
                auth_token=user_token
            )
            
            if result["success"]:
                data = result["data"]
                logger.info(f"✅ Funds addition link created")
                return {
                    "success": True,
                    "redirect_url": data.get("data", {}).get("redirect_url"),
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Add funds failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Add funds error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_transactions(self, user_token: str) -> Dict[str, Any]:
        """Get all transactions for user"""
        try:
            logger.info(f"📊 Fetching user transactions")
            
            result = await self._make_request(
                "GET", "/user/getTransactions", 
                auth_token=user_token
            )
            
            if result["success"]:
                data = result["data"]
                transactions = data.get("data", [])
                logger.info(f"✅ Retrieved {len(transactions)} transactions")
                return {
                    "success": True,
                    "transactions": transactions,
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Transaction fetch failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get transactions error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_single_transaction(self, user_token: str, transaction_id: str) -> Dict[str, Any]:
        """Get specific transaction details"""
        try:
            logger.info(f"📋 Fetching transaction: {transaction_id}")
            
            result = await self._make_request(
                "GET", f"/user/getSingleTransaction/{transaction_id}", 
                auth_token=user_token
            )
            
            if result["success"]:
                data = result["data"]
                logger.info(f"✅ Transaction details retrieved")
                return {
                    "success": True,
                    "transaction": data.get("data"),
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Single transaction fetch failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get single transaction error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_user_balance(self, user_token: str) -> Dict[str, Any]:
        """Get user wallet balance"""
        try:
            logger.info(f"💰 Fetching user balance")
            
            result = await self._make_request(
                "GET", "/user/getBalance", 
                auth_token=user_token
            )
            
            if result["success"]:
                data = result["data"]
                balance_data = data.get("data", {})
                logger.info(f"✅ Balance retrieved: {balance_data.get('amount', 'N/A')} {balance_data.get('currency', 'USD')}")
                return {
                    "success": True,
                    "amount": balance_data.get("amount"),
                    "currency": balance_data.get("currency"),
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Balance fetch failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get balance error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_supported_currencies(self) -> Dict[str, Any]:
        """Get supported currencies for crypto payments"""
        try:
            logger.info(f"💱 Fetching supported currencies")
            
            result = await self._make_request("GET", "/user/getSupportedCurrency")
            
            if result["success"]:
                data = result["data"]
                currencies = data.get("data", [])
                logger.info(f"✅ Retrieved {len(currencies)} supported currencies")
                return {
                    "success": True,
                    "currencies": currencies,
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Currencies fetch failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get currencies error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_crypto_payment(
        self, 
        user_token: str,
        amount: float,
        currency: str,
        callback_url: str,
        meta_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create cryptocurrency payment"""
        try:
            logger.info(f"₿ Creating crypto payment: {currency} ${amount}")
            
            crypto_data = {
                "amount": amount,
                "currency": currency,
                "callback_url": callback_url
            }
            
            if meta_data:
                crypto_data["meta_data"] = meta_data
            
            result = await self._make_request(
                "POST", "/user/createCryptoPayment", 
                crypto_data, 
                auth_token=user_token
            )
            
            if result["success"]:
                data = result["data"]
                logger.info(f"✅ Crypto payment created")
                return {
                    "success": True,
                    "payment_data": data.get("data"),
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Crypto payment failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Create crypto payment error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_crypto_transaction_status(
        self, 
        user_token: str,
        transaction_id: str
    ) -> Dict[str, Any]:
        """Get cryptocurrency transaction status"""
        try:
            logger.info(f"🔍 Checking crypto transaction status: {transaction_id}")
            
            result = await self._make_request(
                "GET", f"/user/getCryptoTransactionStatus/{transaction_id}", 
                auth_token=user_token
            )
            
            if result["success"]:
                data = result["data"]
                logger.info(f"✅ Crypto transaction status retrieved")
                return {
                    "success": True,
                    "transaction_status": data.get("data"),
                    "message": data.get("message")
                }
            else:
                logger.error(f"❌ Crypto status check failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Get crypto status error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_webhook_endpoint(self, order_id: str) -> str:
        """Generate webhook endpoint for payment notifications"""
        # Integration with your existing webhook system
        return f"https://nomadly2-webhook.replit.app/webhook/dynopay/{order_id}"
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection and credentials"""
        try:
            if not self.api_key:
                return {
                    "success": False, 
                    "error": "DYNOPAY_API_KEY not configured"
                }
            
            # Test with supported currencies endpoint (no auth required)
            result = await self.get_supported_currencies()
            
            if result["success"]:
                logger.info("✅ Dynopay API connection successful")
                return {"success": True, "message": "API connection verified"}
            else:
                logger.error(f"❌ Dynopay API test failed: {result['error']}")
                return {"success": False, "error": result["error"]}
                
        except Exception as e:
            logger.error(f"❌ Connection test error: {str(e)}")
            return {"success": False, "error": str(e)}