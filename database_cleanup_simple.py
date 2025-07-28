#!/usr/bin/env python3
"""
Simple Database Cleanup Utility for Nomadly2
Uses SQL tool for reliable database cleaning
"""

import subprocess
import sys
import os

def run_sql_command(query):
    """Execute SQL command using the execute_sql_tool equivalent"""
    try:
        # Get database URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL not found")
            return None
            
        # Parse the URL to extract connection details
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        
        # Run psql command
        psql_cmd = [
            'psql',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:],  # Remove leading /
            '-c', query,
            '--no-password',
            '-t',  # Tuples only
            '--csv'  # CSV output
        ]
        
        # Set password via environment
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        result = subprocess.run(psql_cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"❌ SQL Error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        return None

def show_database_status():
    """Show current database status"""
    print("📊 CURRENT DATABASE STATUS")
    print("=" * 60)
    
    # Get counts
    queries = [
        ("Users", "SELECT COUNT(*) FROM users"),
        ("Domains", "SELECT COUNT(*) FROM registered_domains"), 
        ("Orders", "SELECT COUNT(*) FROM orders"),
        ("User States", "SELECT COUNT(*) FROM user_states"),
        ("Wallet Transactions", "SELECT COUNT(*) FROM wallet_transactions")
    ]
    
    for name, query in queries:
        result = run_sql_command(query)
        if result:
            print(f"📋 {name}: {result}")
    
    print("\n👥 USER DETAILS:")
    user_query = """
        SELECT telegram_id, username, first_name, language_code, 
               balance_usd, technical_email, created_at
        FROM users 
        ORDER BY created_at DESC
        LIMIT 10
    """
    
    result = run_sql_command(user_query)
    if result:
        lines = result.split('\n')
        for line in lines:
            if line.strip():
                parts = line.split(',')
                if len(parts) >= 7:
                    telegram_id, username, first_name, lang, balance, email, created = parts[:7]
                    print(f"  📱 {telegram_id} (@{username}) - {first_name} - Balance: ${balance} - {email}")

def clean_all_users():
    """Clean all user data"""
    print("\n🧹 CLEANING ALL USER DATA")
    print("=" * 60)
    
    confirm = input("⚠️  This will delete ALL user data. Type 'YES' to confirm: ")
    if confirm != 'YES':
        print("❌ Cleanup cancelled")
        return
    
    # Clean in proper order (foreign key constraints)
    cleanup_queries = [
        "DELETE FROM user_states",
        "DELETE FROM wallet_transactions", 
        "DELETE FROM registered_domains",
        "DELETE FROM orders",
        "DELETE FROM openprovider_contacts",
        "DELETE FROM users"
    ]
    
    for query in cleanup_queries:
        result = run_sql_command(query)
        if result is not None:
            print(f"✅ Executed: {query}")
        else:
            print(f"❌ Failed: {query}")
    
    print("✅ Database cleanup complete!")

def main():
    """Main cleanup interface"""
    print("🧹 SIMPLE DATABASE CLEANUP UTILITY")
    print("=" * 60)
    
    while True:
        show_database_status()
        
        print("\n🛠️ OPTIONS:")
        print("1. 🔍 Refresh status")
        print("2. 🧹 Clean all user data")
        print("3. 🚪 Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            continue
        elif choice == '2':
            clean_all_users()
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")
        print("\n" + "="*60)

if __name__ == "__main__":
    main()