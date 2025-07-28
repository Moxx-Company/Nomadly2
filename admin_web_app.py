"""
Nomadly2 Admin Web Application
Professional admin interface for managing the Telegram bot with maritime theme
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
from decimal import Decimal
import json
from database import get_db_manager, User, RegisteredDomain, Order, WalletTransaction, UserState
from admin_panel import AdminPanel
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'nomadly2-admin-offshore-secure-key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Admin credentials (in production, store these securely)
ADMIN_CREDENTIALS = {
    'admin': generate_password_hash('offshore2025')  # Change this in production
}

admin_panel = AdminPanel()

def login_required(f):
    """Decorator to require login for admin routes"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in ADMIN_CREDENTIALS and check_password_hash(ADMIN_CREDENTIALS[username], password):
            session['logged_in'] = True
            session['username'] = username
            flash('Successfully logged in to Nameword Admin Panel', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout admin user"""
    session.clear()
    flash('Successfully logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Main admin dashboard"""
    try:
        stats = get_system_stats()
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash(f'Error loading dashboard: {e}', 'danger')
        return render_template('dashboard.html', stats={})

@app.route('/users')
@login_required
def users():
    """User management page"""
    try:
        db = get_db_manager()
        session_db = db.get_session()
        
        # Get users with their states and balances
        users_query = session_db.query(User).order_by(User.created_at.desc()).limit(50).all()
        
        users_data = []
        for user in users_query:
            user_state = session_db.query(UserState).filter_by(telegram_id=user.telegram_id).first()
            users_data.append({
                'telegram_id': user.telegram_id,
                'username': user.username or 'N/A',
                'balance_usd': user.balance_usd,
                'technical_email': user.technical_email or 'N/A',
                'created_at': user.created_at,
                'last_activity': user.last_activity or user.created_at,
                'current_state': user_state.current_state if user_state else 'unknown'
            })
        
        session_db.close()
        return render_template('users.html', users=users_data)
    except Exception as e:
        logger.error(f"Users page error: {e}")
        flash(f'Error loading users: {e}', 'danger')
        return render_template('users.html', users=[])

@app.route('/domains')
@login_required
def domains():
    """Domain management page"""
    try:
        db = get_db_manager()
        session_db = db.get_session()
        
        domains_query = session_db.query(RegisteredDomain).order_by(RegisteredDomain.created_at.desc()).all()
        
        domains_data = []
        for domain in domains_query:
            user = session_db.query(User).filter_by(telegram_id=domain.telegram_id).first()
            domains_data.append({
                'domain_name': domain.domain_name,
                'telegram_id': domain.telegram_id,
                'username': user.username if user else 'Unknown',
                'expires_at': domain.expires_at,
                'openprovider_domain_id': domain.openprovider_domain_id,
                'cloudflare_zone_id': domain.cloudflare_zone_id,
                'nameservers': domain.nameservers,
                'created_at': domain.created_at,
                'days_until_expiry': (domain.expires_at - datetime.now()).days if domain.expires_at else 'N/A'
            })
        
        session_db.close()
        return render_template('domains.html', domains=domains_data)
    except Exception as e:
        logger.error(f"Domains page error: {e}")
        flash(f'Error loading domains: {e}', 'danger')
        return render_template('domains.html', domains=[])

@app.route('/orders')
@login_required
def orders():
    """Order management page"""
    try:
        db = get_db_manager()
        session_db = db.get_session()
        
        orders_query = session_db.query(Order).order_by(Order.created_at.desc()).limit(100).all()
        
        orders_data = []
        for order in orders_query:
            user = session_db.query(User).filter_by(telegram_id=order.telegram_id).first()
            orders_data.append({
                'order_id': order.order_id,
                'telegram_id': order.telegram_id,
                'username': user.username if user else 'Unknown',
                'amount_usd': order.amount_usd,
                'payment_method': order.payment_method,
                'payment_status': order.payment_status,
                'service_type': order.service_type,
                'service_details': order.service_details,
                'created_at': order.created_at,
                'payment_address': order.payment_address or 'N/A'
            })
        
        session_db.close()
        return render_template('orders.html', orders=orders_data)
    except Exception as e:
        logger.error(f"Orders page error: {e}")
        flash(f'Error loading orders: {e}', 'danger')
        return render_template('orders.html', orders=[])

@app.route('/transactions')
@login_required
def transactions():
    """Transaction management page"""
    try:
        db = get_db_manager()
        session_db = db.get_session()
        
        transactions_query = session_db.query(WalletTransaction).order_by(WalletTransaction.created_at.desc()).limit(100).all()
        
        transactions_data = []
        for tx in transactions_query:
            user = session_db.query(User).filter_by(telegram_id=tx.telegram_id).first()
            transactions_data.append({
                'transaction_id': tx.transaction_id,
                'telegram_id': tx.telegram_id,
                'username': user.username if user else 'Unknown',
                'amount': tx.amount,
                'transaction_type': tx.transaction_type,
                'description': tx.description or 'N/A',
                'order_id': tx.order_id or 'N/A',
                'created_at': tx.created_at
            })
        
        session_db.close()
        return render_template('transactions.html', transactions=transactions_data)
    except Exception as e:
        logger.error(f"Transactions page error: {e}")
        flash(f'Error loading transactions: {e}', 'danger')
        return render_template('transactions.html', transactions=[])

@app.route('/user/<int:telegram_id>')
@login_required
def user_details(telegram_id):
    """Detailed user information page"""
    try:
        db = get_db_manager()
        session_db = db.get_session()
        
        user = session_db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('users'))
        
        # Get user's domains
        domains = session_db.query(RegisteredDomain).filter_by(telegram_id=telegram_id).all()
        
        # Get user's orders
        orders = session_db.query(Order).filter_by(telegram_id=telegram_id).order_by(Order.created_at.desc()).limit(20).all()
        
        # Get user's transactions
        transactions = session_db.query(WalletTransaction).filter_by(telegram_id=telegram_id).order_by(WalletTransaction.created_at.desc()).limit(20).all()
        
        # Get user state
        user_state = session_db.query(UserState).filter_by(telegram_id=telegram_id).first()
        
        session_db.close()
        
        return render_template('user_details.html', 
                             user=user, 
                             domains=domains, 
                             orders=orders, 
                             transactions=transactions,
                             user_state=user_state)
    except Exception as e:
        logger.error(f"User details error: {e}")
        flash(f'Error loading user details: {e}', 'danger')
        return redirect(url_for('users'))

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics"""
    try:
        stats = get_system_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"API stats error: {e}")
        return jsonify({'error': str(e)}), 500

def get_system_stats():
    """Get comprehensive system statistics"""
    try:
        db = get_db_manager()
        session_db = db.get_session()
        
        # Basic counts
        total_users = session_db.query(User).count()
        total_domains = session_db.query(RegisteredDomain).count()
        total_orders = session_db.query(Order).count()
        
        # Active users (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        active_users = session_db.query(User).filter(User.last_activity > week_ago).count()
        
        # Revenue calculations
        completed_orders = session_db.query(Order).filter(Order.payment_status == 'completed').all()
        total_revenue = sum(Decimal(str(order.amount_usd)) for order in completed_orders)
        
        # Recent revenue (30 days)
        month_ago = datetime.now() - timedelta(days=30)
        recent_orders = [o for o in completed_orders if o.created_at >= month_ago]
        revenue_30d = sum(Decimal(str(order.amount_usd)) for order in recent_orders)
        
        # Pending orders
        pending_orders = session_db.query(Order).filter(Order.payment_status == 'pending').count()
        
        # Domain expiry stats
        today = datetime.now()
        month_from_now = today + timedelta(days=30)
        expiring_domains = session_db.query(RegisteredDomain).filter(
            RegisteredDomain.expires_at.between(today, month_from_now)
        ).count()
        
        session_db.close()
        
        return {
            'total_users': total_users,
            'active_users_7d': active_users,
            'total_domains': total_domains,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'revenue_30d': float(revenue_30d),
            'pending_orders': pending_orders,
            'expiring_domains': expiring_domains
        }
    except Exception as e:
        logger.error(f"Stats calculation error: {e}")
        return {}

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Try different ports to avoid conflicts
    for attempt_port in [5000, 5001, 5002, 5003, 8080, 9000]:
        try:
            logger.info(f"🚀 Starting Nameword Admin Web App on port {attempt_port}")
            app.run(host='0.0.0.0', port=attempt_port, debug=False, threaded=True)
            break
        except OSError as e:
            if "Address already in use" in str(e):
                logger.warning(f"Port {attempt_port} is busy, trying next port...")
                continue
            else:
                raise e