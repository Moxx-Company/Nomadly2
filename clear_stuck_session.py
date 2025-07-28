#!/usr/bin/env python3
"""
Clear stuck nameserver session for user and fix DNS validation issues
"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_user_session():
    """Clear stuck nameserver waiting state"""
    try:
        # Load current sessions
        with open('user_sessions.json', 'r') as f:
            sessions = json.load(f)
        
        print("🔍 CURRENT SESSION STATES")
        print("=" * 30)
        
        for user_id, session in sessions.items():
            print(f"User {user_id}:")
            
            # Check for stuck states
            stuck_states = []
            if "waiting_for_nameservers" in session:
                stuck_states.append("waiting_for_nameservers")
            if "waiting_for_ns" in session:
                stuck_states.append("waiting_for_ns")
            if "waiting_for_dns_edit" in session:
                stuck_states.append("waiting_for_dns_edit")
            if "waiting_for_dns_input" in session:
                stuck_states.append("waiting_for_dns_input")
            
            if stuck_states:
                print(f"  ⚠️ Stuck states found: {stuck_states}")
                
                # Clear all waiting states
                for state in stuck_states:
                    if state in session:
                        del session[state]
                        print(f"  ✅ Cleared {state}")
                
                # Clear related session data
                cleanup_keys = [
                    "editing_dns_record_id",
                    "editing_dns_domain", 
                    "dns_workflow_step",
                    "dns_record_type",
                    "dns_record_name",
                    "dns_domain",
                    "current_dns_domain"
                ]
                
                for key in cleanup_keys:
                    if key in session:
                        del session[key]
                        print(f"  🧹 Cleaned up {key}")
                        
            else:
                print(f"  ✅ No stuck states found")
        
        # Save cleaned sessions
        with open('user_sessions.json', 'w') as f:
            json.dump(sessions, f, indent=2)
        
        print("\n✅ SESSION CLEANUP COMPLETED")
        print("User should now be able to search domains normally")
        
    except Exception as e:
        print(f"❌ Error cleaning sessions: {e}")

if __name__ == "__main__":
    fix_user_session()