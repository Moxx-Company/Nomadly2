#!/usr/bin/env python3
"""
Direct webhook diagnosis and manual processing script
"""
import requests
import json
import logging
import os
from models import DatabaseManager
from handlers.deposit_webhook import DepositWebhookHandler
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_blockbee_logs_for_deposit(deposit_id):
    """Check BlockBee logs for a specific deposit"""
    api_key = os.getenv("BLOCKBEE_API_KEY")
    if not api_key:
        logger.error("BLOCKBEE_API_KEY not found in environment variables")
        return
    
    webhook_url = f"https://a76ed245-5cfb-4d11-81a9-a3ba484b6267-00-xpl9yn4jgt8n.janeway.replit.dev/webhook/deposit/{deposit_id}"

    try:
        url = f"https://api.blockbee.io/ltc/logs/"
        params = {"apikey": api_key, "callback": webhook_url}

        response = requests.get(url, params=params, timeout=30)
        logger.info(f"BlockBee logs for deposit {deposit_id}: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Found logs: {json.dumps(data, indent=2)}")

            # Check for payment confirmations
            callbacks = data.get("callbacks", [])
            if callbacks:
                latest_callback = callbacks[-1]
                confirmations = latest_callback.get("confirmations", 0)
                value_coin = latest_callback.get("value_coin", "0")
                txid_in = latest_callback.get("txid_in", "")

                logger.info(
                    f"Latest payment: {confirmations} confirmations, {value_coin} LTC, tx: {txid_in}"
                )

                # If we have confirmations but payment not processed, do manual processing
                if confirmations >= 1 and value_coin != "0":
                    return {
                        "has_payment": True,
                        "confirmations": confirmations,
                        "value_coin": value_coin,
                        "txid_in": txid_in,
                        "callback_data": latest_callback,
                    }

            return {"has_payment": False, "logs": data}
        else:
            logger.error(f"Failed to get logs: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error checking BlockBee logs: {e}")
        return None


def manually_process_confirmed_deposit(deposit_id, payment_data):
    """Manually process a confirmed deposit that wasn't automatically processed"""
    try:
        config = Config()
        db_manager = DatabaseManager()
        deposit_handler = DepositWebhookHandler(config, db_manager)

        # Simulate webhook data from BlockBee payment info
        webhook_data = {
            "address_in": payment_data.get("address_in", ""),
            "address_out": payment_data.get("address_out", ""),
            "txid_in": payment_data["txid_in"],
            "txid_out": payment_data.get("txid_out", ""),
            "confirmations": payment_data["confirmations"],
            "value": str(
                float(payment_data["value_coin"]) * 100000000
            ),  # Convert to satoshis
            "value_coin": payment_data["value_coin"],
            "value_forwarded": payment_data.get("value_forwarded", "0"),
            "value_forwarded_coin": payment_data.get("value_forwarded_coin", "0"),
            "coin": "ltc",
            "pending": False,
            "manual_processing": True,
        }

        logger.info(
            f"Manually processing deposit {deposit_id} with data: {webhook_data}"
        )

        success = deposit_handler.process_deposit_webhook(deposit_id, webhook_data)

        if success:
            logger.info(f"Successfully manually processed deposit {deposit_id}")
            return True
        else:
            logger.error(f"Failed to manually process deposit {deposit_id}")
            return False

    except Exception as e:
        logger.error(f"Error in manual processing: {e}")
        return False


def main():
    """Main diagnosis and processing routine"""
    logger.info("=== Webhook Diagnosis and Manual Processing ===")

    # Check the latest pending deposits
    db_manager = DatabaseManager()
    session = db_manager.get_session()

    try:
        # Get pending deposits
        from models import DepositRequest

        pending_deposits = (
            session.query(DepositRequest)
            .filter(DepositRequest.payment_status == "pending")
            .order_by(DepositRequest.created_at.desc())
            .limit(5)
            .all()
        )

        logger.info(f"Found {len(pending_deposits)} pending deposits")

        for deposit in pending_deposits:
            logger.info(
                f"Checking deposit {deposit.id} - {deposit.amount} USD - {deposit.crypto_currency}"
            )

            # Check BlockBee logs for this deposit
            payment_info = check_blockbee_logs_for_deposit(deposit.id)

            if payment_info and payment_info.get("has_payment"):
                logger.info(
                    f"Found confirmed payment for deposit {deposit.id}, processing manually..."
                )
                success = manually_process_confirmed_deposit(
                    deposit.id, payment_info["callback_data"]
                )

                if success:
                    logger.info(f"Deposit {deposit.id} successfully processed manually")
                else:
                    logger.error(f"Failed to manually process deposit {deposit.id}")
            else:
                logger.info(f"No confirmed payment found for deposit {deposit.id}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
