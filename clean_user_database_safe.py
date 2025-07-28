#!/usr/bin/env python3
"""
Safe Database Cleaning Utility for Nomadly2
Provides multiple cleaning options with proper safeguards
"""

import os
import sys
from datetime import datetime
from database import get_db_manager

def display_current_data():
    """Display current database statistics"""
    
    print("📊 CURRENT DATABASE STATUS")
    print("=" * 60)
    
    db_manager = get_db_manager()
    
    try:
        # Get counts
        total_users = db_manager.execute_query("SELECT COUNT(*) FROM users")[0][0]
        total_domains = db_manager.execute_query("SELECT COUNT(*) FROM registered_domains")[0][0]
        total_orders = db_manager.execute_query("SELECT COUNT(*) FROM orders")[0][0]
        
        print(f"👥 Users: {total_users}")
        print(f"🌐 Domains: {total_domains}")
        print(f"📋 Orders: {total_orders}")
        
        # Show user breakdown
        print("\n👥 USER BREAKDOWN:")
        users = db_manager.execute_query("""
            SELECT u.telegram_id, u.username, COUNT(rd.id) as domain_count, u.created_at 
            FROM users u 
            LEFT JOIN registered_domains rd ON u.telegram_id = rd.telegram_id 
            GROUP BY u.telegram_id, u.username, u.created_at 
            ORDER BY u.created_at DESC
        """)
        
        for user in users:
            telegram_id, username, domain_count, created_at = user
            print(f"  📱 {telegram_id} (@{username}) - {domain_count} domains - {created_at}")
        
        # Show domain breakdown  
        print("\n🌐 DOMAIN BREAKDOWN:")
        domains = db_manager.execute_query("""
            SELECT domain_name, telegram_id, openprovider_domain_id, created_at 
            FROM registered_domains 
            ORDER BY created_at DESC
        """)
        
        for domain in domains[:10]:  # Show first 10
            domain_name, telegram_id, op_id, created_at = domain
            status = "✅ Manageable" if str(op_id).isdigit() else "❌ Not Manageable"
            print(f"  🌐 {domain_name} (User: {telegram_id}) - {status} - {created_at}")
        
        if len(domains) > 10:
            print(f"  ... and {len(domains) - 10} more domains")
            
    except Exception as e:
        print(f"❌ Error getting database status: {e}")

def backup_database():
    """Create a backup before cleaning"""
    
    print("\n💾 CREATING BACKUP")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_before_clean_{timestamp}.sql"
    
    # Create backup using pg_dump
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ No DATABASE_URL found")
            return False
            
        import subprocess
        
        # Extract connection details from DATABASE_URL
        # Format: postgresql://user:password@host:port/database
        import urllib.parse
        parsed = urllib.parse.urlparse(database_url)
        
        pg_dump_cmd = [
            'pg_dump',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:],  # Remove leading /
            '--no-password',
            '-f', backup_file
        ]
        
        # Set password via environment
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        result = subprocess.run(pg_dump_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Backup created: {backup_file}")
            return True
        else:
            print(f"❌ Backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Backup error: {e}")
        return False

def clean_test_users():
    """Remove obvious test users and their data"""
    
    print("\n🧹 CLEANING TEST USERS")
    print("=" * 60)
    
    db_manager = get_db_manager()
    
    # Define test user patterns
    test_patterns = [
        '1111111111',  # Obvious test ID
        '6789012345',  # Another test ID
    ]
    
    test_usernames = [
        'onarrival1',  # Test username (but keep main user 5590563715)
    ]
    
    try:
        for test_id in test_patterns:
            # Check if user exists
            user_exists = db_manager.execute_query(
                "SELECT COUNT(*) FROM users WHERE telegram_id = %s", 
                (test_id,)
            )[0][0]
            
            if user_exists:
                print(f"🗑️ Removing test user: {test_id}")
                
                # Remove user's domains first
                db_manager.execute_query(
                    "DELETE FROM registered_domains WHERE telegram_id = %s", 
                    (test_id,)
                )
                
                # Remove user's orders
                db_manager.execute_query(
                    "DELETE FROM orders WHERE telegram_id = %s", 
                    (test_id,)
                )
                
                # Remove user
                db_manager.execute_query(
                    "DELETE FROM users WHERE telegram_id = %s", 
                    (test_id,)
                )
                
                print(f"✅ Removed test user {test_id} and all associated data")
            else:
                print(f"ℹ️ Test user {test_id} not found")
                
    except Exception as e:
        print(f"❌ Error cleaning test users: {e}")

def clean_unmanageable_domains():
    """Remove domains that are not manageable (not in OpenProvider account)"""
    
    print("\n🌐 CLEANING UNMANAGEABLE DOMAINS")
    print("=" * 60)
    
    db_manager = get_db_manager()
    
    try:
        # Find domains with non-numeric OpenProvider IDs (not manageable)
        unmanageable = db_manager.execute_query("""
            SELECT id, domain_name, telegram_id, openprovider_domain_id 
            FROM registered_domains 
            WHERE openprovider_domain_id ~ '^[^0-9]+$'
            OR openprovider_domain_id = 'not_manageable_account_mismatch'
        """)
        
        print(f"Found {len(unmanageable)} unmanageable domains:")
        
        for domain_data in unmanageable:
            domain_id, domain_name, telegram_id, op_id = domain_data
            print(f"  🗑️ {domain_name} (User: {telegram_id}, ID: {op_id})")
        
        if unmanageable:
            confirm = input(f"\n❓ Remove {len(unmanageable)} unmanageable domains? (y/N): ")
            
            if confirm.lower() == 'y':
                for domain_data in unmanageable:
                    domain_id, domain_name, telegram_id, op_id = domain_data
                    
                    # Remove the domain
                    db_manager.execute_query(
                        "DELETE FROM registered_domains WHERE id = %s", 
                        (domain_id,)
                    )
                    print(f"✅ Removed {domain_name}")
                
                print(f"✅ Cleaned {len(unmanageable)} unmanageable domains")
            else:
                print("ℹ️ Keeping unmanageable domains")
        else:
            print("✅ No unmanageable domains found")
            
    except Exception as e:
        print(f"❌ Error cleaning unmanageable domains: {e}")

def clean_duplicate_users():
    """Remove duplicate user entries"""
    
    print("\n👥 CLEANING DUPLICATE USERS")
    print("=" * 60)
    
    db_manager = get_db_manager()
    
    try:
        # Find users with same username but different telegram_id
        duplicates = db_manager.execute_query("""
            SELECT username, COUNT(*), string_agg(telegram_id::text, ', ') as telegram_ids
            FROM users 
            WHERE username IS NOT NULL 
            GROUP BY username 
            HAVING COUNT(*) > 1
        """)
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate username groups:")
            
            for username, count, telegram_ids in duplicates:
                print(f"  👥 Username '{username}': {count} users ({telegram_ids})")
                
                # Get detailed info for this username
                user_details = db_manager.execute_query("""
                    SELECT telegram_id, created_at, 
                           (SELECT COUNT(*) FROM registered_domains WHERE telegram_id = u.telegram_id) as domain_count
                    FROM users u 
                    WHERE username = %s 
                    ORDER BY created_at ASC
                """, (username,))
                
                print(f"    📋 Details:")
                for telegram_id, created_at, domain_count in user_details:
                    print(f"      📱 {telegram_id}: {domain_count} domains, created {created_at}")
                
                # Keep the one with the most domains, or the oldest if tied
                if len(user_details) > 1:
                    # Sort by domain count (descending), then by creation date (ascending)
                    sorted_users = sorted(user_details, key=lambda x: (-x[2], x[1]))
                    keep_user = sorted_users[0][0]
                    remove_users = [u[0] for u in sorted_users[1:]]
                    
                    print(f"    ✅ Would keep: {keep_user}")
                    print(f"    🗑️ Would remove: {', '.join(map(str, remove_users))}")
        else:
            print("✅ No duplicate usernames found")
            
    except Exception as e:
        print(f"❌ Error checking duplicate users: {e}")

def full_reset():
    """Complete database reset (DANGEROUS)"""
    
    print("\n💀 FULL DATABASE RESET")
    print("=" * 60)
    print("⚠️  WARNING: This will delete ALL user data!")
    print("⚠️  This action cannot be undone!")
    
    confirm1 = input("\nType 'RESET' to confirm full database reset: ")
    if confirm1 != 'RESET':
        print("❌ Reset cancelled")
        return
        
    confirm2 = input("Type 'YES DELETE EVERYTHING' to proceed: ")
    if confirm2 != 'YES DELETE EVERYTHING':
        print("❌ Reset cancelled")
        return
    
    db_manager = get_db_manager()
    
    try:
        print("🗑️ Deleting all registered domains...")
        db_manager.execute_query("DELETE FROM registered_domains")
        
        print("🗑️ Deleting all orders...")
        db_manager.execute_query("DELETE FROM orders")
        
        print("🗑️ Deleting all users...")
        db_manager.execute_query("DELETE FROM users")
        
        print("✅ Full database reset complete")
        
    except Exception as e:
        print(f"❌ Error during full reset: {e}")

def main():
    """Main menu for database cleaning options"""
    
    print("🧹 NOMADLY2 DATABASE CLEANING UTILITY")
    print("=" * 60)
    
    while True:
        display_current_data()
        
        print("\n🛠️ CLEANING OPTIONS:")
        print("1. 🧹 Clean test users (safe)")
        print("2. 🌐 Clean unmanageable domains")
        print("3. 👥 Check duplicate users")
        print("4. 💾 Create backup only")
        print("5. 💀 Full reset (DANGEROUS)")
        print("6. 🚪 Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            backup_database()
            clean_test_users()
        elif choice == '2':
            backup_database()
            clean_unmanageable_domains()
        elif choice == '3':
            clean_duplicate_users()
        elif choice == '4':
            backup_database()
        elif choice == '5':
            backup_database()
            full_reset()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")
        print("\n" + "="*60)

if __name__ == "__main__":
    main()