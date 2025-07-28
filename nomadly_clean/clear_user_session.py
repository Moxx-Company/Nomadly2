#!/usr/bin/env python3
"""Clear user session data"""

import json
import os

# Clear user sessions
if os.path.exists('user_sessions.json'):
    with open('user_sessions.json', 'r') as f:
        sessions = json.load(f)
    
    if '5590563715' in sessions:
        del sessions['5590563715']
        with open('user_sessions.json', 'w') as f:
            json.dump(sessions, f, indent=2)
        print('✅ User session cleared')
    else:
        print('ℹ️ No session found')
else:
    with open('user_sessions.json', 'w') as f:
        json.dump({}, f)
    print('✅ Created empty sessions file')

# Clear payment monitor queue
if os.path.exists('payment_monitor_queue.json'):
    os.remove('payment_monitor_queue.json')
    print('✅ Payment monitor queue cleared')

print('\n✅ User data cleared successfully!')
print('System ready for fresh order test with automatic payment processing.')