"""
BlockBee API Integration
Handles cryptocurrency payment processing and webhook management
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class BlockBeeAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.blockbee.io"

    def get_supported_cryptocurrencies(self) -> List[Dict]:
        """Get list of supported cryptocurrencies"""
        try:
            url = f"{self.base_url}/info/"
            params = {"apikey": self.api_key}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return result.get("data", [])
                else:
                    logger.error(
                        f"Supported currencies retrieval failed: {result.get('message')}"
                    )
                    return []
            else:
                logger.error(
                    f"Supported currencies retrieval failed: {response.status_code}"
                )
                return []

        except Exception as e:
            logger.error(f"Supported currencies retrieval error: {e}")
            return []

    def create_payment_address(
        self, cryptocurrency: str, callback_url: str, amount: float = None
    ) -> Dict:
        """Create payment address for cryptocurrency - Mystery milestone compatible version"""
        try:
            # Fix cryptocurrency mapping for BlockBee API
            crypto_mapping = {
                "bch": "bch",
                "bsc": "erc20/bnb",       # Fix Binance Coin  
                "btc": "btc",
                "eth": "eth", 
                "ltc": "ltc",
                "ustcr": "erc20/usdt",
                "doge": "doge",
                "trx": "trx",
                "usdt": "trc20/usdt",
            }
            
            api_crypto = crypto_mapping.get(cryptocurrency.lower(), cryptocurrency)
            logger.info(f"🔗 BlockBee API: {cryptocurrency} -> {api_crypto}")
            
            params = {"apikey": self.api_key, "callback": callback_url}

            if amount:
                params["value"] = str(amount)

            response = requests.get(
                f"{self.base_url}/{api_crypto}/create/", params=params, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"BlockBee response for {cryptocurrency}: {result}")
                return result

            logger.error(f"BlockBee API error {response.status_code}: {response.text}")
            return {"status": "error", "message": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"BlockBee API exception: {e}")
            return {"status": "error", "message": str(e)}

    def get_payment_info(self, cryptocurrency: str, address: str) -> Optional[Dict]:
        """Get payment information for an address"""
        # BlockBee doesn't have a direct info endpoint for addresses
        # Instead, we need to use the logs endpoint with the callback URL
        # For now, return empty dict to prevent errors
        logger.warning(f"Payment info check for {address} - BlockBee uses callback/webhook system")
        return {}
    
    def check_logs(self, cryptocurrency: str, callback_url: str) -> Optional[Dict]:
        """Check payment logs using the callback URL"""
        try:
            crypto_mapping = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "ltc": "litecoin",
                "usdt": "usdt_erc20",
            }

            crypto_code = crypto_mapping.get(
                cryptocurrency.lower(), cryptocurrency.lower()
            )

            url = f"{self.base_url}/{crypto_code}/logs/"
            params = {"apikey": self.api_key, "callback": callback_url}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Logs response: {result}")
                return result
            else:
                logger.error(f"Logs retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Logs retrieval error: {e}")
            return None

    def get_conversion_rate(
        self, cryptocurrency: str, fiat_currency: str = "USD"
    ) -> Optional[float]:
        """Get conversion rate from cryptocurrency to fiat"""
        try:
            crypto_mapping = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "ltc": "litecoin",
                "usdt": "usdt_erc20",
            }

            crypto_code = crypto_mapping.get(
                cryptocurrency.lower(), cryptocurrency.lower()
            )

            url = f"{self.base_url}/{crypto_code}/convert/"
            params = {"apikey": self.api_key, "value": 1, "from": fiat_currency.lower()}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    # The API returns how much crypto equals 1 USD
                    crypto_amount = float(result.get("value_coin", 0))
                    if crypto_amount > 0:
                        # Return USD per crypto unit
                        return 1.0 / crypto_amount
                    return None
                else:
                    logger.error(
                        f"Conversion rate retrieval failed: {result.get('message')}"
                    )
                    return None
            else:
                logger.error(
                    f"Conversion rate retrieval failed: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Conversion rate retrieval error: {e}")
            return None

    def convert_fiat_to_crypto(
        self, amount: float, cryptocurrency: str
    ) -> Optional[float]:
        """Convert USD amount to cryptocurrency amount"""
        try:
            crypto_mapping = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "ltc": "litecoin",
                "usdt": "usdt_erc20",
            }

            crypto_code = crypto_mapping.get(
                cryptocurrency.lower(), cryptocurrency.lower()
            )

            url = f"{self.base_url}/{crypto_code}/convert/"
            params = {"apikey": self.api_key, "value": amount, "from": "usd"}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    crypto_amount = float(result.get("value_coin", 0))
                    logger.info(
                        f"Converted ${amount} USD to {crypto_amount} {cryptocurrency.upper()}"
                    )
                    return crypto_amount
                else:
                    logger.error(
                        f"Fiat to crypto conversion failed: {result.get('message')}"
                    )
                    return None
            else:
                logger.error(
                    f"Fiat to crypto conversion failed: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Fiat to crypto conversion error: {e}")
            return None

    def check_payment_status(
        self, cryptocurrency: str, address: str
    ) -> Tuple[bool, float, int]:
        """Check payment status and return confirmed, amount, confirmations"""
        try:
            payment_info = self.get_payment_info(cryptocurrency, address)

            if payment_info:
                confirmed = payment_info.get("confirmed", False)
                amount_received = float(payment_info.get("value_coin", 0))
                confirmations = int(payment_info.get("confirmations", 0))

                return confirmed, amount_received, confirmations
            else:
                return False, 0.0, 0

        except Exception as e:
            logger.error(f"Payment status check error: {e}")
            return False, 0.0, 0

    def get_transaction_fees(self, cryptocurrency: str) -> Optional[Dict]:
        """Get current transaction fees for a cryptocurrency"""
        try:
            crypto_mapping = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "ltc": "litecoin",
                "usdt": "usdt_erc20",
            }

            crypto_code = crypto_mapping.get(
                cryptocurrency.lower(), cryptocurrency.lower()
            )

            url = f"{self.base_url}/{crypto_code}/fees/"
            params = {"apikey": self.api_key}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return result.get("data", {})
                else:
                    logger.error(
                        f"Transaction fees retrieval failed: {result.get('message')}"
                    )
                    return None
            else:
                logger.error(
                    f"Transaction fees retrieval failed: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Transaction fees retrieval error: {e}")
            return None

    def validate_address(self, cryptocurrency: str, address: str) -> bool:
        """Validate a cryptocurrency address"""
        try:
            crypto_mapping = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "ltc": "litecoin",
                "usdt": "usdt_erc20",
            }

            crypto_code = crypto_mapping.get(
                cryptocurrency.lower(), cryptocurrency.lower()
            )

            url = f"{self.base_url}/{crypto_code}/validate/"
            params = {"apikey": self.api_key, "address": address}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return result.get("valid", False)
                else:
                    logger.error(f"Address validation failed: {result.get('message')}")
                    return False
            else:
                logger.error(f"Address validation failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Address validation error: {e}")
            return False

    def get_network_stats(self, cryptocurrency: str) -> Optional[Dict]:
        """Get network statistics for a cryptocurrency"""
        try:
            crypto_mapping = {
                "btc": "bitcoin",
                "eth": "ethereum",
                "ltc": "litecoin",
                "usdt": "usdt_erc20",
            }

            crypto_code = crypto_mapping.get(
                cryptocurrency.lower(), cryptocurrency.lower()
            )

            url = f"{self.base_url}/{crypto_code}/stats/"
            params = {"apikey": self.api_key}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    return result.get("data", {})
                else:
                    logger.error(
                        f"Network stats retrieval failed: {result.get('message')}"
                    )
                    return None
            else:
                logger.error(f"Network stats retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Network stats retrieval error: {e}")
            return None
