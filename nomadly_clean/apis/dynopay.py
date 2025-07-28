import requests
import logging
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class DynopayAPI:
    def __init__(self, api_key: str, token:str):
        self.api_key = api_key
        self.token = token
        self.base_url = "https://user-api.dynopay.com/"


    def create_payment_address(
        self, cryptocurrency: str, callback_url:str ,amount: float = None
    ) -> Dict:
        """Create payment address for cryptocurrency - Mystery milestone compatible version"""
        try:
            # Fix cryptocurrency mapping for Dynopay API
            crypto_mapping = {
                "bch": "BCH",
                "bsc": "BSC",
                "btc": "BTC",
                "eth": "ETH", 
                "ltc": "LTC",
                "ustcr": "USDT-ERC20",
                "doge": "DOGE",
                "trx": "TRX",
                "usdt": "USDT-TRC20",
            }
            
            api_crypto  = crypto_mapping.get(cryptocurrency.lower(), cryptocurrency)
            logger.info(f"🔗 Dynopay API: {cryptocurrency} -> {api_crypto}")
            
            payload = json.dumps({
                "amount": amount,
                "currency": api_crypto,
                "redirect_uri":callback_url
                })

            headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.token}"
            }

            response = requests.request("POST", f"{self.base_url}api/user/cryptoPayment", headers=headers, data=payload)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Dynopay response for {cryptocurrency}: {result}")
                return result

            logger.error(f"Dynopay API error {response.status_code}: {response.text}")
            return {"status": "error", "message": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Dynopay API exception: {e}")
            return {"status": "error", "message": str(e)}

    def get_payment_transaction_status(
        self, addressid: str
    ) -> Dict:
        """Create payment address for cryptocurrency - Mystery milestone compatible version"""
        try:
            
            logger.info(f"🔗 Dynopay API - Payment Address: {addressid}")
            
            headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.token}"
            }

            response = requests.request("GET", f"{self.base_url}api/user/getCryptoTransaction/{addressid}", headers=headers)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Dynopay API - Payment Address response for {addressid}: {result}")
                return result

            logger.error(f"Dynopay API - Payment Address API error {response.status_code}: {response.text}")
            return {"status": "error", "message": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Dynopay API exception: {e}")
            return {"status": "error", "message": str(e)}


    def get_payment_single_transaction(
        self, addressid: str
    ) -> Dict:
        """Create payment address for cryptocurrency - Mystery milestone compatible version"""
        try:
            
            logger.info(f"🔗 Dynopay API - Payment Transaction: {addressid}")
            
            headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.token}"
            }

            response = requests.request("GET", f"{self.base_url}api/user/getSingleTransaction/{addressid}", headers=headers)

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Dynopay API - Payment Transaction response for {addressid}: {result}")
                return result

            logger.error(f"Dynopay API - Payment Transaction API error {response.status_code}: {response.text}")
            return {"status": "error", "message": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Dynopay API exception: {e}")
            return {"status": "error", "message": str(e)}