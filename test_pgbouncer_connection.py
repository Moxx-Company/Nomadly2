#!/usr/bin/env python3
"""
Test PgBouncer connection for Nomadly2
"""

import psycopg2
import time

def test_direct_connection():
    """Test direct database connection"""
    try:
        print("🔌 Testing direct database connection...")
        conn = psycopg2.connect(
            "postgresql://neondb_owner:npg_ieZ3UGJ6QxYk@ep-divine-smoke-adc40rg0.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        print(f"✅ Direct connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return False

def test_pgbouncer_connection():
    """Test PgBouncer connection"""
    try:
        print("🔄 Testing PgBouncer connection...")
        conn = psycopg2.connect(
            "postgresql://neondb_owner:npg_ieZ3UGJ6QxYk@localhost:6432/nomadly2"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        print(f"✅ PgBouncer connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ PgBouncer connection failed: {e}")
        return False

def check_port_listening():
    """Check if port 6432 is listening"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 6432))
        sock.close()
        if result == 0:
            print("✅ Port 6432 is listening")
            return True
        else:
            print("❌ Port 6432 is not listening")
            return False
    except Exception as e:
        print(f"❌ Port check failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 PgBouncer Connection Test for Nomadly2")
    print("=" * 50)
    
    # Test direct connection first
    direct_ok = test_direct_connection()
    
    # Check if port is listening
    port_ok = check_port_listening()
    
    # Test PgBouncer connection
    if port_ok:
        pgbouncer_ok = test_pgbouncer_connection()
    else:
        pgbouncer_ok = False
        print("🔄 Skipping PgBouncer test - port not available")
    
    print("\n📊 TEST RESULTS:")
    print(f"   Direct DB: {'✅' if direct_ok else '❌'}")
    print(f"   Port 6432: {'✅' if port_ok else '❌'}")
    print(f"   PgBouncer: {'✅' if pgbouncer_ok else '❌'}")
    
    if direct_ok and port_ok and pgbouncer_ok:
        print("\n🎉 All tests passed! PgBouncer is ready to use.")
        print("📝 Update your DATABASE_URL to: postgresql://neondb_owner:npg_ieZ3UGJ6QxYk@localhost:6432/nomadly2")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")