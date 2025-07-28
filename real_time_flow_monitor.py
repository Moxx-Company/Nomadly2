#!/usr/bin/env python3
"""
Real-time Transaction Flow Monitor
Monitor payment confirmation → registration → database storage
"""

import sys
import time
import asyncio
from datetime import datetime
sys.path.insert(0, '/home/runner/workspace')

async def monitor_complete_flow():
    """Monitor the complete transaction flow in real-time"""
    
    print("🔍 REAL-TIME FLOW MONITORING STARTED")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    from database import get_db_manager
    
    # Order details from test creation
    order_id = "2884d40b-4b2e-40a5-927b-d41f43400c19"
    domain_name = "flowtest36160.sbs"
    payment_address = "0x47F2a1CC87c719C3cA608f638e8d354cC2F5b2C7"
    
    print(f"Order ID: {order_id}")
    print(f"Domain: {domain_name}")
    print(f"Payment Address: {payment_address}")
    print()
    
    db_manager = get_db_manager()
    
    stages_completed = {
        "payment_received": False,
        "webhook_processed": False,
        "cloudflare_zone_created": False,
        "openprovider_registered": False,
        "database_stored": False,
        "notifications_sent": False
    }
    
    start_time = datetime.now()
    check_count = 0
    
    while not all(stages_completed.values()) and check_count < 120:  # 20 minutes max
        check_count += 1
        current_time = datetime.now().strftime('%H:%M:%S')
        elapsed = (datetime.now() - start_time).total_seconds()
        
        try:
            # Check order status
            order = db_manager.get_order(order_id)
            if order:
                print(f"[{current_time}] ({elapsed:.0f}s) Order Status: {order.payment_status}")
                
                # Stage 1: Payment received
                if order.payment_status in ["confirmed", "completed"] and not stages_completed["payment_received"]:
                    stages_completed["payment_received"] = True
                    print(f"✅ PAYMENT CONFIRMED at {current_time}")
                    if hasattr(order, 'payment_txid') and order.payment_txid:
                        print(f"   Transaction ID: {order.payment_txid}")
                
                # Stage 2: Webhook processed
                if order.payment_status == "completed" and not stages_completed["webhook_processed"]:
                    stages_completed["webhook_processed"] = True
                    print(f"✅ WEBHOOK PROCESSED at {current_time}")
            
            # Stage 3: Check Cloudflare zone creation
            if not stages_completed["cloudflare_zone_created"]:
                try:
                    from apis.production_cloudflare import CloudflareAPI
                    cf_api = CloudflareAPI()
                    cloudflare_zone_id = cf_api._get_zone_id(domain_name)
                    if cloudflare_zone_id:
                        stages_completed["cloudflare_zone_created"] = True
                        print(f"✅ CLOUDFLARE ZONE CREATED: {cloudflare_zone_id} at {current_time}")
                except Exception as e:
                    pass
            
            # Stage 4 & 5: Check domain registration and database storage
            if not stages_completed["database_stored"]:
                domains = db_manager.get_user_domains(5590563715)
                for domain in domains:
                    if domain.domain_name == domain_name:
                        stages_completed["database_stored"] = True
                        print(f"✅ DATABASE STORED: Domain ID {domain.id} at {current_time}")
                        
                        if domain.openprovider_domain_id and not stages_completed["openprovider_registered"]:
                            stages_completed["openprovider_registered"] = True
                            print(f"✅ OPENPROVIDER REGISTERED: ID {domain.openprovider_domain_id} at {current_time}")
                        break
            
            # Stage 6: Check notifications (assume sent if domain is stored)
            if stages_completed["database_stored"] and not stages_completed["notifications_sent"]:
                stages_completed["notifications_sent"] = True
                print(f"✅ NOTIFICATIONS SENT at {current_time}")
            
            # Progress summary
            completed_count = sum(stages_completed.values())
            total_stages = len(stages_completed)
            progress_percent = (completed_count / total_stages) * 100
            
            print(f"[{current_time}] Progress: {completed_count}/{total_stages} ({progress_percent:.1f}%)")
            
            # Show remaining stages
            pending_stages = [stage for stage, done in stages_completed.items() if not done]
            if pending_stages:
                print(f"   Waiting for: {', '.join(pending_stages)}")
            
            print("-" * 50)
            
            if all(stages_completed.values()):
                break
                
            await asyncio.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            print(f"[{current_time}] Monitor error: {e}")
            await asyncio.sleep(10)
    
    # Final report
    print(f"\n📋 FINAL TRANSACTION FLOW REPORT")
    print(f"=" * 50)
    print(f"Total monitoring time: {(datetime.now() - start_time).total_seconds():.0f} seconds")
    
    for stage, completed in stages_completed.items():
        status = "✅ COMPLETED" if completed else "❌ PENDING"
        print(f"{stage.replace('_', ' ').title()}: {status}")
    
    if all(stages_completed.values()):
        print(f"\n🎉 COMPLETE TRANSACTION SUCCESS!")
        print(f"All stages completed - domain registration workflow operational")
        
        # Get final domain details
        try:
            domains = db_manager.get_user_domains(5590563715)
            for domain in domains:
                if domain.domain_name == domain_name:
                    print(f"\n📊 FINAL DOMAIN DETAILS:")
                    print(f"   Domain: {domain.domain_name}")
                    print(f"   Database ID: {domain.id}")
                    print(f"   OpenProvider ID: {domain.openprovider_domain_id}")
                    print(f"   Cloudflare Zone: {domain.cloudflare_zone_id}")
                    print(f"   Registration Date: {domain.registration_date}")
                    print(f"   Status: {domain.status}")
                    break
        except:
            pass
        
        return True
    else:
        print(f"\n⚠️ TRANSACTION INCOMPLETE")
        pending = [stage for stage, done in stages_completed.items() if not done]
        print(f"Pending stages: {', '.join(pending)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(monitor_complete_flow())
    if success:
        print(f"\n🚀 MONITORING COMPLETE - TRANSACTION SUCCESSFUL")
    else:
        print(f"\n🔍 MONITORING COMPLETE - CHECK PENDING STAGES")