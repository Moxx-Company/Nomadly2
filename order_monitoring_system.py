#!/usr/bin/env python3
"""
Comprehensive Order Monitoring System for Nomadly2
Real-time monitoring of domain registration pipeline
"""

import time
import json
from datetime import datetime
from database import get_db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderMonitor:
    """Monitor domain registration orders and detect issues"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.previous_state = {}
        
    def get_current_database_state(self):
        """Get current database state for comparison"""
        session = self.db_manager.get_session()
        try:
            # Get user counts and details
            users = session.execute("SELECT telegram_id, username, first_name, current_state, technical_email FROM users").fetchall()
            
            # Get order details
            orders = session.execute("""
                SELECT order_id, telegram_id, domain_name, status, payment_status, 
                       amount, crypto_currency, crypto_amount, created_at
                FROM orders ORDER BY created_at DESC
            """).fetchall()
            
            # Get domain registration status
            domains = session.execute("""
                SELECT domain_name, telegram_id, openprovider_domain_id, 
                       cloudflare_zone_id, nameserver_mode, created_at
                FROM registered_domains ORDER BY created_at DESC
            """).fetchall()
            
            # Get user states
            user_states = session.execute("""
                SELECT telegram_id, state, data, created_at 
                FROM user_states ORDER BY created_at DESC
            """).fetchall()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'users': [dict(u._mapping) for u in users],
                'orders': [dict(o._mapping) for o in orders],
                'domains': [dict(d._mapping) for d in domains],
                'user_states': [dict(s._mapping) for s in user_states]
            }
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return None
        finally:
            session.close()
    
    def detect_issues(self, current_state):
        """Detect potential issues in the registration pipeline"""
        issues = []
        recommendations = []
        
        if not current_state:
            return ["❌ CRITICAL: Database connection failed"], ["Check database connectivity"]
        
        # Check for stuck orders
        for order in current_state.get('orders', []):
            if order['status'] == 'pending':
                created_time = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00') if 'Z' in str(order['created_at']) else str(order['created_at']))
                time_diff = datetime.now() - created_time.replace(tzinfo=None)
                
                if time_diff.total_seconds() > 300:  # 5 minutes
                    issues.append(f"⏰ STUCK ORDER: {order['order_id']} pending for {time_diff}")
                    recommendations.append(f"Check payment status for order {order['order_id']}")
        
        # Check for orders without domains
        order_domains = {o['order_id']: o['domain_name'] for o in current_state.get('orders', [])}
        registered_domains = {d['domain_name'] for d in current_state.get('domains', [])}
        
        for order_id, domain_name in order_domains.items():
            if domain_name not in registered_domains:
                order = next(o for o in current_state.get('orders', []) if o['order_id'] == order_id)
                if order['status'] == 'completed':
                    issues.append(f"❌ MISSING DOMAIN: Order {order_id} completed but {domain_name} not registered")
                    recommendations.append(f"Manually register domain {domain_name} or refund order {order_id}")
        
        # Check for users without email addresses before domain registration
        for user in current_state.get('users', []):
            if user['current_state'] and 'domain' in user['current_state'] and not user['technical_email']:
                issues.append(f"📧 NO EMAIL: User {user['telegram_id']} attempting domain registration without technical email")
                recommendations.append(f"Prompt user {user['telegram_id']} to set technical email")
        
        # Check for incomplete registrations
        for domain in current_state.get('domains', []):
            if not domain['openprovider_domain_id'] or str(domain['openprovider_domain_id']).startswith('not_manageable'):
                issues.append(f"🌐 INCOMPLETE REGISTRATION: {domain['domain_name']} missing valid OpenProvider ID")
                recommendations.append(f"Check OpenProvider registration status for {domain['domain_name']}")
        
        return issues, recommendations
    
    def monitor_step(self):
        """Single monitoring step"""
        current_state = self.get_current_database_state()
        
        if current_state:
            issues, recommendations = self.detect_issues(current_state)
            
            # Compare with previous state for changes
            changes = []
            if self.previous_state:
                # Check for new orders
                prev_orders = {o['order_id'] for o in self.previous_state.get('orders', [])}
                curr_orders = {o['order_id'] for o in current_state.get('orders', [])}
                new_orders = curr_orders - prev_orders
                
                for order_id in new_orders:
                    order = next(o for o in current_state['orders'] if o['order_id'] == order_id)
                    changes.append(f"🆕 NEW ORDER: {order_id} for {order['domain_name']} by user {order['telegram_id']}")
                
                # Check for status changes
                for order in current_state.get('orders', []):
                    prev_order = next((o for o in self.previous_state.get('orders', []) if o['order_id'] == order['order_id']), None)
                    if prev_order and prev_order['status'] != order['status']:
                        changes.append(f"📊 STATUS CHANGE: Order {order['order_id']} {prev_order['status']} → {order['status']}")
                
                # Check for new domains
                prev_domains = {d['domain_name'] for d in self.previous_state.get('domains', [])}
                curr_domains = {d['domain_name'] for d in current_state.get('domains', [])}
                new_domains = curr_domains - prev_domains
                
                for domain_name in new_domains:
                    domain = next(d for d in current_state['domains'] if d['domain_name'] == domain_name)
                    changes.append(f"🌐 NEW DOMAIN: {domain_name} registered for user {domain['telegram_id']}")
            
            # Store current state
            self.previous_state = current_state
            
            return {
                'timestamp': current_state['timestamp'],
                'summary': {
                    'users': len(current_state.get('users', [])),
                    'orders': len(current_state.get('orders', [])),
                    'domains': len(current_state.get('domains', [])),
                    'user_states': len(current_state.get('user_states', []))
                },
                'changes': changes,
                'issues': issues,
                'recommendations': recommendations,
                'current_activity': self._analyze_current_activity(current_state)
            }
        
        return None
    
    def _analyze_current_activity(self, state):
        """Analyze what users are currently doing"""
        activity = []
        
        for user_state in state.get('user_states', []):
            user_id = user_state['telegram_id']
            current_state = user_state['state']
            data = user_state.get('data', {})
            
            if current_state:
                if 'domain' in current_state:
                    activity.append(f"👤 User {user_id}: Domain registration workflow - {current_state}")
                elif 'payment' in current_state:
                    activity.append(f"💰 User {user_id}: Payment process - {current_state}")
                else:
                    activity.append(f"🔄 User {user_id}: Active in {current_state}")
        
        return activity

def run_monitoring():
    """Run continuous monitoring"""
    monitor = OrderMonitor()
    print("🚀 Starting Order Monitoring System")
    print("=" * 60)
    
    while True:
        try:
            result = monitor.monitor_step()
            
            if result:
                print(f"\n📊 MONITORING REPORT - {result['timestamp']}")
                print("-" * 40)
                
                # Summary
                summary = result['summary']
                print(f"📋 Summary: {summary['users']} users, {summary['orders']} orders, {summary['domains']} domains")
                
                # Current Activity
                if result['current_activity']:
                    print("\n🔄 Current Activity:")
                    for activity in result['current_activity']:
                        print(f"  {activity}")
                else:
                    print("  💤 No active user sessions")
                
                # Changes
                if result['changes']:
                    print("\n📈 Recent Changes:")
                    for change in result['changes']:
                        print(f"  {change}")
                
                # Issues
                if result['issues']:
                    print("\n❌ DETECTED ISSUES:")
                    for issue in result['issues']:
                        print(f"  {issue}")
                    
                    print("\n💡 RECOMMENDATIONS:")
                    for rec in result['recommendations']:
                        print(f"  {rec}")
                else:
                    print("\n✅ No issues detected")
                
                print("-" * 40)
            
            time.sleep(10)  # Monitor every 10 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_monitoring()