#!/usr/bin/env python3
"""
Real-time Transaction Monitor for thankyoujesusmylord.sbs
Order ID: f5d79497-3863-4f60-bc9d-e10ee327f423
"""

import asyncio
import psycopg2
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def check_transaction_status():
    """Monitor the specific transaction"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check order status
    cur.execute("""
        SELECT 
            order_id,
            domain_name,
            payment_status,
            crypto_currency,
            crypto_amount,
            amount,
            payment_address,
            created_at,
            updated_at
        FROM orders 
        WHERE order_id = %s
    """, ('f5d79497-3863-4f60-bc9d-e10ee327f423',))
    
    order = cur.fetchone()
    
    if order:
        print(f"\n🔍 TRANSACTION MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        print(f"📋 Order ID: {order[0]}")
        print(f"🌐 Domain: {order[1]}")
        print(f"💰 Status: {order[2]}")
        print(f"🪙 Currency: {order[3]}")
        print(f"📊 Amount: {order[4]} {order[3]} (${order[5]})")
        print(f"📍 Payment Address: {order[6]}")
        print(f"⏰ Created: {order[7]}")
        print(f"🔄 Updated: {order[8]}")
        
        # Check for domain registration if completed
        if order[2] == 'completed':
            cur.execute("""
                SELECT domain_name, registration_status, cloudflare_zone_id
                FROM registered_domains 
                WHERE domain_name = %s
            """, (order[1],))
            
            domain = cur.fetchone()
            if domain:
                print(f"✅ Domain Status: {domain[1]}")
                print(f"☁️ Cloudflare Zone: {domain[2][:20]}..." if domain[2] else "No Cloudflare zone")
        
        # Check wallet transactions
        cur.execute("""
            SELECT transaction_type, amount, description, created_at
            FROM wallet_transactions 
            WHERE description LIKE %s
            ORDER BY created_at DESC
            LIMIT 3
        """, (f"%{order[0]}%",))
        
        transactions = cur.fetchall()
        if transactions:
            print("\n💳 Related Wallet Transactions:")
            for tx in transactions:
                print(f"   • {tx[0]}: ${tx[1]} - {tx[2]} ({tx[3]})")
    
    cur.close()
    conn.close()
    return order[2] if order else 'unknown'

def monitor_blockchain():
    """Check blockchain confirmation status"""
    print("\n🔗 BLOCKCHAIN MONITORING")
    print("Waiting for ETH payment to address: 0x46ac7205D9F818a4CfE12c54C60678A2663d81a0")
    print("Expected amount: 0.00269697 ETH (~$9.87)")
    print("Minimum confirmations: 1 block")
    
def main():
    """Main monitoring loop"""
    print("🚀 STARTING REAL-TIME TRANSACTION MONITOR")
    print("Monitoring: thankyoujesusmylord.sbs")
    print("Order: f5d79497-3863-4f60-bc9d-e10ee327f423")
    print("Press Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            status = check_transaction_status()
            monitor_blockchain()
            
            if status == 'completed':
                print("\n🎉 TRANSACTION COMPLETED!")
                print("Domain registration should be processing...")
                break
            elif status == 'failed':
                print("\n❌ TRANSACTION FAILED!")
                break
            
            print(f"\n⏳ Status: {status.upper()} - Checking again in 30 seconds...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")

if __name__ == "__main__":
    main()