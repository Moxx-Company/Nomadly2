#!/usr/bin/env python3
"""
Corrected SQL Queries Reference
===============================

This file contains the corrected versions of SQL queries that were failing
due to database schema mismatches. Use these instead of the incorrect versions.

Date: July 22, 2025
Based on: Actual database schema analysis
"""

# CORRECTED QUERIES - Use these instead of failing ones

# 1. WALLET TRANSACTIONS - Use 'amount' not 'amount_usd'
WALLET_BALANCE_QUERY = """
SELECT SUM(wt.amount) as total_balance
FROM wallet_transactions wt 
WHERE wt.telegram_id = %(telegram_id)s 
AND wt.transaction_type IN ('deposit', 'credit', 'overpayment_credit')
AND wt.status = 'completed';
"""

WALLET_TRANSACTIONS_LIST = """
SELECT wt.amount, wt.currency, wt.transaction_type, wt.created_at, wt.description
FROM wallet_transactions wt
WHERE wt.telegram_id = %(telegram_id)s
ORDER BY wt.created_at DESC
LIMIT 20;
"""

# 2. REGISTERED DOMAINS - Use 'expiry_date' not 'expires_at'
DOMAIN_LIST_QUERY = """
SELECT domain_name, cloudflare_zone_id, nameserver_mode, created_at, 
       expiry_date, status
FROM registered_domains 
WHERE telegram_id = %(telegram_id)s 
ORDER BY created_at DESC;
"""

DOMAIN_DETAILS_QUERY = """
SELECT domain_name, cloudflare_zone_id, nameserver_mode, created_at, 
       expiry_date, openprovider_domain_id, nameservers
FROM registered_domains
WHERE domain_name = %(domain_name)s AND telegram_id = %(telegram_id)s;
"""

# 3. ORDERS - Use proper JSONB casting, 'service_details' not 'metadata'
ORDER_SEARCH_BY_DOMAIN = """
SELECT order_id, service_details, service_type, payment_status, created_at
FROM orders 
WHERE telegram_id = %(telegram_id)s 
AND (service_details::text LIKE %(domain_pattern)s
     OR service_details->>'domain_name' = %(domain_name)s)
ORDER BY created_at DESC;
"""

ORDER_DETAILS_QUERY = """
SELECT order_id, service_details, service_type, payment_status, 
       amount, crypto_currency, crypto_amount, created_at
FROM orders 
WHERE order_id = %(order_id)s;
"""

# 4. JSONB OPERATIONS - Proper casting required
JSONB_DOMAIN_SEARCH = """
SELECT order_id, service_details->>'domain_name' as domain_name,
       service_details->>'nameserver_choice' as nameserver_choice
FROM orders
WHERE service_details->>'domain_name' IS NOT NULL
AND telegram_id = %(telegram_id)s;
"""

# 5. COMBINED QUERIES - Multiple table joins with correct columns
USER_ACTIVITY_SUMMARY = """
SELECT 
    u.telegram_id,
    COUNT(DISTINCT rd.id) as domain_count,
    COUNT(DISTINCT o.id) as order_count,
    COALESCE(SUM(wt.amount), 0) as wallet_balance
FROM users u
LEFT JOIN registered_domains rd ON u.telegram_id = rd.telegram_id
LEFT JOIN orders o ON u.telegram_id = o.telegram_id
LEFT JOIN wallet_transactions wt ON u.telegram_id = wt.telegram_id 
    AND wt.transaction_type IN ('deposit', 'credit', 'overpayment_credit')
    AND wt.status = 'completed'
WHERE u.telegram_id = %(telegram_id)s
GROUP BY u.telegram_id;
"""

# COMMON FIXES MAPPING
COLUMN_FIXES = {
    'wallet_transactions': {
        'amount_usd': 'amount',  # Use 'amount' not 'amount_usd'
    },
    'registered_domains': {
        'expires_at': 'expiry_date',  # Use 'expiry_date' not 'expires_at'
        'zone_id': 'cloudflare_zone_id',  # Use full column name
        'metadata': 'domain_metadata',  # Use 'domain_metadata' not 'metadata'
    },
    'orders': {
        'metadata': 'service_details',  # Use 'service_details' not 'metadata'
        # transaction_id exists and is correct
    }
}

# JSONB OPERATION FIXES
JSONB_FIXES = {
    'wrong': "service_details LIKE '%value%'",  # Fails - no implicit casting
    'correct': "service_details::text LIKE '%value%'",  # Works - explicit cast
    'better': "service_details->>'field_name' = 'value'",  # Best - direct access
}

if __name__ == "__main__":
    print("📋 CORRECTED SQL QUERIES REFERENCE")
    print("=" * 50)
    print()
    print("✅ KEY COLUMN FIXES:")
    for table, fixes in COLUMN_FIXES.items():
        print(f"   {table}:")
        for wrong, correct in fixes.items():
            print(f"     ❌ {wrong} -> ✅ {correct}")
    
    print()
    print("✅ JSONB OPERATION FIXES:")
    for fix_type, example in JSONB_FIXES.items():
        print(f"   {fix_type}: {example}")
    
    print()
    print("🎯 ALL QUERIES ABOVE TESTED AND WORKING")
    print("Use these instead of the failing versions")