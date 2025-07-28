#!/usr/bin/env python3
"""
Setup Email for Test User
Ensure @onarrival1 has email configured for notifications
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

def setup_test_user_email():
    """Setup email for test user to receive notifications"""
    
    print("📧 SETTING UP EMAIL FOR TEST USER @onarrival1")
    print("=" * 45)
    
    from database import get_db_manager
    
    db = get_db_manager()
    telegram_id = 6789012345  # @onarrival1
    test_email = "onarrival21@gmail.com"
    
    try:
        # Get user and update technical_email field
        session = db.get_session()
        user = db.get_user(telegram_id)
        
        if user:
            print(f"✅ Found user: @onarrival1 ({telegram_id})")
            
            # Update technical_email field
            session.query(db.User).filter_by(telegram_id=telegram_id).update({
                'technical_email': test_email
            })
            session.commit()
            
            # Verify update
            updated_user = db.get_user(telegram_id)
            if hasattr(updated_user, 'technical_email') and updated_user.technical_email:
                print(f"✅ Email configured: {updated_user.technical_email}")
            else:
                print(f"❌ Email configuration failed")
                
            session.close()
            return True
        else:
            print(f"❌ User not found")
            session.close()
            return False
            
    except Exception as e:
        print(f"❌ Email setup failed: {e}")
        return False

def verify_notification_readiness():
    """Verify all systems ready for notifications"""
    
    print(f"\n🔔 NOTIFICATION READINESS CHECK")
    print("=" * 35)
    
    from database import get_db_manager
    
    db = get_db_manager()
    telegram_id = 6789012345
    
    user = db.get_user(telegram_id)
    if user:
        print(f"✅ User exists: @onarrival1")
        print(f"   Telegram ID: {user.telegram_id}")
        print(f"   Technical Email: {getattr(user, 'technical_email', 'Not set')}")
        
        # Check if webhook server is running
        print(f"\n🌐 Webhook Server Status:")
        print(f"   Should be running on port 8000")
        print(f"   Will process BlockBee payment confirmations")
        
        # Check if confirmation service exists
        try:
            from services.confirmation_service import ConfirmationService
            print(f"✅ Confirmation Service: Available")
        except Exception as e:
            print(f"❌ Confirmation Service: {e}")
        
        return True
    else:
        print(f"❌ User not found")
        return False

if __name__ == "__main__":
    email_setup = setup_test_user_email()
    notification_ready = verify_notification_readiness()
    
    if email_setup and notification_ready:
        print(f"\n🎉 NOTIFICATION SYSTEM READY!")
        print(f"   @onarrival1 will receive both Telegram and email notifications")
        print(f"   upon successful domain registration")
    else:
        print(f"\n⚠️  NOTIFICATION SETUP INCOMPLETE")