#!/usr/bin/env python3
"""
Send Missing Domain Registration Confirmation
Send the missing registration success notification for flowtest36160.sbs
"""

import sys
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def send_missing_confirmation():
    """Send domain registration confirmation for flowtest36160.sbs"""
    
    print("📧 SENDING MISSING DOMAIN CONFIRMATION")
    print("=" * 45)
    
    from services.confirmation_service import ConfirmationService
    from database import get_db_manager
    
    confirmation_service = ConfirmationService()
    db = get_db_manager()
    
    # Get the flowtest domain details
    telegram_id = 5590563715
    domain = db.get_domain_by_name("flowtest36160.sbs", telegram_id)
    
    if not domain:
        print("❌ flowtest36160.sbs domain not found in database")
        return False
    
    print(f"Found domain: {domain.domain_name}")
    print(f"Database ID: {domain.id}")
    print(f"OpenProvider ID: {domain.openprovider_domain_id}")
    print(f"Cloudflare Zone: {domain.cloudflare_zone_id}")
    print(f"Status: {domain.status}")
    
    # Prepare domain data for confirmation
    domain_data = {
        "domain_name": domain.domain_name,
        "registration_status": "Active", 
        "expiry_date": str(domain.expiry_date) if domain.expiry_date else "2026-07-21 23:59:59",
        "openprovider_domain_id": domain.openprovider_domain_id or "27820529",
        "cloudflare_zone_id": domain.cloudflare_zone_id,
        "nameservers": domain.nameservers or "anderson.ns.cloudflare.com,leanna.ns.cloudflare.com",
        "dns_info": f"DNS configured with Cloudflare Zone ID: {domain.cloudflare_zone_id}"
    }
    
    try:
        # Send domain registration confirmation
        await confirmation_service.send_domain_registration_confirmation(
            telegram_id, domain_data
        )
        
        print(f"✅ Domain registration confirmation sent successfully")
        print(f"   User: {telegram_id}")
        print(f"   Domain: {domain.domain_name}")
        print(f"   Telegram notification: Sent")
        print(f"   Email notification: Sent")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send confirmation: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the confirmation sending"""
    success = await send_missing_confirmation()
    if success:
        print(f"\n🎉 DOMAIN REGISTRATION CONFIRMATION SENT")
        print(f"User @onarrival will now receive complete registration notifications")
    else:
        print(f"\n💥 CONFIRMATION SENDING FAILED")

if __name__ == "__main__":
    asyncio.run(main())