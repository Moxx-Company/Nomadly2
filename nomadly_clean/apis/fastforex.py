"""
FastForex.io API Integration  
Provides real-time cryptocurrency and forex conversion rates
FastForex supports 500+ cryptocurrencies and forex pairs
"""

import requests
import logging
from typing import Optional, Dict
import os

logger = logging.getLogger(__name__)


class FastForexAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FASTFOREX_API_KEY")
        self.base_url = "https://api.fastforex.io"

    def convert_usd_to_crypto(self, amount: float, cryptocurrency: str) -> Optional[float]:
        """Convert USD amount to cryptocurrency using FastForex /convert endpoint"""
        try:
            if not self.api_key:
                logger.warning("FastForex API key not provided")
                return None

            # FastForex uses uppercase symbols for cryptocurrencies
            crypto_symbol = cryptocurrency.upper()
            
            url = f"{self.base_url}/convert"
            params = {
                "from": "USD",
                "to": crypto_symbol,
                "amount": amount,
                "api_key": self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and crypto_symbol in result["result"]:
                    crypto_amount = float(result["result"][crypto_symbol])
                    logger.info(f"FastForex conversion: ${amount} USD = {crypto_amount:.8f} {crypto_symbol}")
                    return crypto_amount
                else:
                    logger.error(f"FastForex conversion failed: {result}")
                    return None
            else:
                logger.error(f"FastForex API HTTP error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"FastForex conversion exception: {e}")
            return None

    def get_crypto_rate_to_usd(self, cryptocurrency: str) -> Optional[float]:
        """Get how much 1 unit of cryptocurrency equals in USD"""
        try:
            if not self.api_key:
                logger.warning("FastForex API key not provided") 
                return None

            crypto_symbol = cryptocurrency.upper()
            
            url = f"{self.base_url}/fetch-one"
            params = {
                "from": crypto_symbol,
                "to": "USD", 
                "api_key": self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    rate = float(result["result"]["USD"])
                    logger.info(f"FastForex rate: 1 {crypto_symbol} = ${rate} USD")
                    return rate
                else:
                    logger.error(f"FastForex rate fetch failed: {result}")
                    return None
            else:
                logger.error(f"FastForex rate API error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"FastForex rate exception: {e}")
            return None

    def get_supported_currencies(self) -> Dict:
        """Get list of supported currencies including cryptocurrencies"""
        try:
            if not self.api_key:
                return {}

            url = f"{self.base_url}/currencies"
            params = {"api_key": self.api_key}

            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                logger.error(f"FastForex currencies API error: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"FastForex currencies exception: {e}")
            return {}