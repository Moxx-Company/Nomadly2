#!/usr/bin/env python3
"""
Live Order Monitoring System
Real-time tracking of domain registration orders
"""

import time
import json
from datetime import datetime
import subprocess
import os

def run_sql(query):
    """Execute SQL query directly"""
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            return None
            
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)
        
        psql_cmd = [
            'psql',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:],
            '-c', query,
            '--no-password',
            '-t', '--csv'
        ]
        
        env = os.environ.copy()
        if parsed.password:
            env['PGPASSWORD'] = parsed.password
        
        result = subprocess.run(psql_cmd, env=env, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
        
    except Exception as e:
        print(f"SQL Error: {e}")
        return None

def get_current_state():
    """Get current database state"""
    
    # Get user count and latest user activity
    user_query = """
        SELECT u.telegram_id, u.username, u.technical_email, u.created_at,
               COALESCE(us.state, 'idle') as current_state, us.data as state_data
        FROM users u
        LEFT JOIN user_states us ON u.telegram_id = us.telegram_id
        ORDER BY u.created_at DESC
        LIMIT 5
    """
    
    users = run_sql(user_query)
    
    # Get orders
    order_query = """
        SELECT order_id, telegram_id, domain_name, payment_status, 
               amount, crypto_currency, created_at
        FROM orders 
        ORDER BY created_at DESC 
        LIMIT 10
    """
    
    orders = run_sql(order_query)
    
    # Get domains
    domain_query = """
        SELECT domain_name, telegram_id, openprovider_domain_id, 
               nameserver_mode, created_at
        FROM registered_domains 
        ORDER BY created_at DESC 
        LIMIT 10
    """
    
    domains = run_sql(domain_query)
    
    return {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'users': users.split('\n') if users else [],
        'orders': orders.split('\n') if orders else [],
        'domains': domains.split('\n') if domains else []
    }

def detect_changes(prev_state, curr_state):
    """Detect changes between states"""
    changes = []
    
    if not prev_state:
        return changes
    
    # Check for new users
    prev_user_count = len([u for u in prev_state['users'] if u.strip()])
    curr_user_count = len([u for u in curr_state['users'] if u.strip()])
    
    if curr_user_count > prev_user_count:
        changes.append(f"🆕 NEW USER DETECTED (+{curr_user_count - prev_user_count})")
    
    # Check for new orders
    prev_order_count = len([o for o in prev_state['orders'] if o.strip()])
    curr_order_count = len([o for o in curr_state['orders'] if o.strip()])
    
    if curr_order_count > prev_order_count:
        changes.append(f"📋 NEW ORDER CREATED (+{curr_order_count - prev_order_count})")
    
    # Check for new domains
    prev_domain_count = len([d for d in prev_state['domains'] if d.strip()])
    curr_domain_count = len([d for d in curr_state['domains'] if d.strip()])
    
    if curr_domain_count > prev_domain_count:
        changes.append(f"🌐 NEW DOMAIN REGISTERED (+{curr_domain_count - prev_domain_count})")
    
    return changes

def analyze_activity(state):
    """Analyze current user activity"""
    activity = []
    
    for user_line in state['users']:
        if not user_line.strip():
            continue
            
        parts = user_line.split(',')
        if len(parts) >= 6:
            telegram_id = parts[0]
            username = parts[1]
            email = parts[2]
            created = parts[3]
            current_state = parts[4] if parts[4] else "idle"
            
            if current_state and current_state != "idle":
                activity.append(f"👤 User {telegram_id} (@{username}): {current_state}")
            elif email:
                activity.append(f"👤 User {telegram_id} (@{username}): Ready for orders (Email: {email})")
    
    return activity

def monitor_orders():
    """Main monitoring loop"""
    print("🚀 LIVE ORDER MONITORING STARTED")
    print("=" * 50)
    
    previous_state = None
    
    while True:
        try:
            current_state = get_current_state()
            
            print(f"\n📊 {current_state['timestamp']} - ORDER MONITOR STATUS")
            print("-" * 30)
            
            # Show current counts
            user_count = len([u for u in current_state['users'] if u.strip()])
            order_count = len([o for o in current_state['orders'] if o.strip()])
            domain_count = len([d for d in current_state['domains'] if d.strip()])
            
            print(f"📈 Current: {user_count} users, {order_count} orders, {domain_count} domains")
            
            # Detect changes
            changes = detect_changes(previous_state, current_state)
            if changes:
                print("🔥 CHANGES DETECTED:")
                for change in changes:
                    print(f"   {change}")
            
            # Show current activity
            activity = analyze_activity(current_state)
            if activity:
                print("🔄 CURRENT ACTIVITY:")
                for act in activity:
                    print(f"   {act}")
            else:
                print("💤 No active user sessions")
            
            # Show latest orders if any
            if current_state['orders'] and current_state['orders'][0].strip():
                print("📋 LATEST ORDERS:")
                for i, order in enumerate(current_state['orders'][:3]):
                    if order.strip():
                        parts = order.split(',')
                        if len(parts) >= 3:
                            order_id = parts[0][:8] + "..."
                            user_id = parts[1]
                            domain = parts[2]
                            payment_status = parts[3] if len(parts) > 3 else "unknown"
                            print(f"   {i+1}. {domain} (User: {user_id}, Payment: {payment_status}, ID: {order_id})")
            
            previous_state = current_state
            time.sleep(3)  # Check every 3 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Monitor error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    monitor_orders()