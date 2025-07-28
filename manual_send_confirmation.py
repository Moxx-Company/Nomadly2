#!/usr/bin/env python3
"""
Manually send the confirmation email that should have been sent
"""

import asyncio
import logging
from services.confirmation_service import ConfirmationService
from database import get_db_manager
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_missing_confirmation():
    """Send the confirmation email that was missed"""
    try:
        print("📧 Sending Missing Domain Registration Confirmation")
        print("=" * 55)

        # Get user and latest domain
        db_manager = get_db_manager()
        user = db_manager.get_user(5590563715)

        print(f"👤 User email: {user.technical_email}")

        # Get latest domain from database query
        session = db_manager.get_session()
        try:
            from sqlalchemy import text

            result = session.execute(
                text(
                    "SELECT * FROM registered_domains WHERE telegram_id = :telegram_id ORDER BY registration_date DESC LIMIT 1"
                ),
                {"telegram_id": 5590563715},
            ).fetchone()

            if result:
                domain_name = result[2]  # domain_name is 3rd column
                nameservers_json = result[17]  # nameservers column
                expiry_date = result[20]  # expiry_date column

                # Parse nameservers
                nameservers = []
                if nameservers_json:
                    try:
                        nameservers = json.loads(nameservers_json)
                    except:
                        nameservers = [await get_real_cloudflare_nameservers(domain_name)]

                print(f"🌐 Domain: {domain_name}")
                print(f"📅 Expires: {expiry_date}")
                print(f"🌐 Nameservers: {nameservers}")
                print()

                # Send domain registration confirmation
                confirmation_service = ConfirmationService()

                domain_data = {
                    "domain_name": domain_name,
                    "registration_status": "Active",
                    "expiry_date": str(expiry_date) if expiry_date else "N/A",
                    "nameservers": nameservers,
                    "dns_info": "DNS configured with Cloudflare for optimal performance and speed",
                }

                success = (
                    await confirmation_service.send_domain_registration_confirmation(
                        telegram_id=5590563715, domain_data=domain_data
                    )
                )

                print(
                    f"📨 Domain confirmation sent: {'✅ SUCCESS' if success else '❌ FAILED'}"
                )

                # Also send payment confirmation for completeness
                payment_data = {
                    "order_id": "bae038b2-2d3a-439f-976c-99138e2c6539",
                    "amount_usd": 2.99,
                    "payment_method": "Cryptocurrency (ETH)",
                    "transaction_id": "ETH Payment Confirmed",
                    "service_description": f"Domain Registration: {domain_name}",
                }

                payment_success = await confirmation_service.send_payment_confirmation(
                    telegram_id=5590563715, order_data=payment_data
                )

                print(
                    f"💰 Payment confirmation sent: {'✅ SUCCESS' if payment_success else '❌ FAILED'}"
                )

                return success and payment_success
            else:
                print("❌ No domain found")
                return False

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(send_missing_confirmation())

    print(f"\n{'='*55}")
    print("📋 Results:")
    if success:
        print("✅ Confirmation emails sent successfully!")
        print("📧 Check your email (onarrival21@gmail.com) for:")
        print("   • Payment confirmation")
        print("   • Domain registration confirmation")
        print()
        print("🔧 For future registrations, the webhook system")
        print("   should send confirmations automatically.")
    else:
        print("❌ Failed to send confirmation emails")
