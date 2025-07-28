#!/usr/bin/env python3
"""
Simple Admin Web App for Nameword Domain Registration System
Maritime-themed admin interface with database monitoring
"""

import os
import logging
import psycopg2
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'offshore2025_admin_secret')

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'offshore2025'

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Welcome to Nameword Admin Panel', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('simple_login.html')

def get_db_connection():
    """Get database connection using environment variables"""
    return psycopg2.connect(
        host=os.environ.get('PGHOST'),
        port=os.environ.get('PGPORT'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD')
    )

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM registered_domains")
        total_domains = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM wallet_transactions")
        total_transactions = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute("""
            SELECT u.telegram_id, u.username, u.email, u.balance_usd, u.created_at
            FROM users u
            ORDER BY u.created_at DESC
            LIMIT 5
        """)
        recent_users = cursor.fetchall()
        
        cursor.execute("""
            SELECT rd.domain_name, rd.expires_at, rd.created_at
            FROM registered_domains rd
            ORDER BY rd.created_at DESC
            LIMIT 5
        """)
        recent_domains = cursor.fetchall()
        
        stats = {
            'total_users': total_users,
            'total_domains': total_domains,
            'total_orders': total_orders,
            'total_transactions': total_transactions,
            'recent_users': recent_users,
            'recent_domains': recent_domains
        }
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        stats = {
            'total_users': 0,
            'total_domains': 0,
            'total_orders': 0,
            'total_transactions': 0,
            'recent_users': [],
            'recent_domains': []
        }
    
    return render_template('simple_dashboard.html', stats=stats)

@app.route('/users')
def users():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.telegram_id, u.username, u.email, u.balance_usd, u.created_at,
                   us.current_state
            FROM users u
            LEFT JOIN user_states us ON u.telegram_id = us.telegram_id
            ORDER BY u.created_at DESC
        """)
        users_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Users error: {e}")
        users_data = []
    
    return render_template('simple_users.html', users=users_data)

@app.route('/domains')
def domains():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT rd.domain_name, rd.expires_at, rd.openprovider_domain_id,
                   rd.cloudflare_zone_id, rd.nameservers, rd.created_at,
                   u.username
            FROM registered_domains rd
            LEFT JOIN users u ON rd.telegram_id = u.telegram_id
            ORDER BY rd.created_at DESC
        """)
        domains_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Domains error: {e}")
        domains_data = []
    
    return render_template('simple_domains.html', domains=domains_data)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    logger.info("🚀 Starting Simple Nameword Admin on port 8000 (Public Port)")
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)