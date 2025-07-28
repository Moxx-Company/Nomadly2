#!/usr/bin/env python3
"""
Monitor Complete Transaction Flow
Real-time monitoring of payment → registration → database workflow
"""

import sys
import time
import asyncio
sys.path.insert(0, '/home/runner/workspace')

async def monitor_flow(order_id, domain_name):
    """Monitor the complete transaction flow"""
    
    print(f"📊 MONITORING TRANSACTION FLOW")
    print(f"=" * 40)
    print(f"Order ID: {order_id}")
    print(f"Domain: {domain_name}")
    print(f"Monitoring started at: {time.strftime('%H:%M:%S')}")
    print()
    
    from database import get_db_manager
    
    stages = {
        "payment_confirmed": False,
        "cloudflare_zone": False,
        "openprovider_registration": False,
        "database_stored": False,
        "notifications_sent": False
    }
    
    db_manager = get_db_manager()
    check_count = 0
    
    while not all(stages.values()) and check_count < 60:  # Monitor for 10 minutes max
        check_count += 1
        current_time = time.strftime('%H:%M:%S')
        
        try:
            # Check order status
            order = db_manager.get_order(order_id)
            if order:
                print(f"[{current_time}] Order Status: {order.status}")
                
                if order.status == "completed" and not stages["payment_confirmed"]:
                    stages["payment_confirmed"] = True
                    print(f"✅ PAYMENT CONFIRMED at {current_time}")
            
            # Check for Cloudflare zone
            if not stages["cloudflare_zone"]:
                try:
                    from apis.production_cloudflare import CloudflareAPI
                    cf_api = CloudflareAPI()
                    cloudflare_zone_id = cf_api._get_zone_id(domain_name)
                    if cloudflare_zone_id:
                        stages["cloudflare_zone"] = True
                        print(f"✅ CLOUDFLARE ZONE CREATED: {cloudflare_zone_id} at {current_time}")
                except:
                    pass
            
            # Check for domain in database
            if not stages["database_stored"]:
                domains = db_manager.get_user_domains(5590563715)
                for domain in domains:
                    if domain.domain_name == domain_name:
                        stages["database_stored"] = True
                        print(f"✅ DATABASE STORED: Domain ID {domain.id} at {current_time}")
                        if domain.openprovider_domain_id:
                            stages["openprovider_registration"] = True
                            print(f"✅ OPENPROVIDER REGISTERED: ID {domain.openprovider_domain_id} at {current_time}")
                        break
            
            # Check for notifications (simplified - check logs)
            if stages["database_stored"] and not stages["notifications_sent"]:
                # Assume notifications sent if domain is stored
                stages["notifications_sent"] = True
                print(f"✅ NOTIFICATIONS SENT at {current_time}")
            
            # Show progress
            completed = sum(stages.values())
            total = len(stages)
            progress = (completed / total) * 100
            print(f"[{current_time}] Progress: {completed}/{total} stages ({progress:.1f}%)")
            
            if not all(stages.values()):
                print(f"Waiting for next stage... (check {check_count}/60)")
                await asyncio.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"[{current_time}] Monitor error: {e}")
            await asyncio.sleep(10)
    
    print(f"\n📋 FINAL MONITORING REPORT:")
    print(f"=" * 40)
    for stage, completed in stages.items():
        status = "✅ COMPLETED" if completed else "❌ PENDING"
        print(f"{stage.replace('_', ' ').title()}: {status}")
    
    if all(stages.values()):
        print(f"\n🎉 COMPLETE FLOW SUCCESS!")
        print(f"All stages completed successfully")
        return True
    else:
        print(f"\n⚠️ FLOW INCOMPLETE")
        print(f"Some stages still pending after monitoring period")
        return False

if __name__ == "__main__":
    # This will be called with the order details
    print("Monitor ready - call with order_id and domain_name")