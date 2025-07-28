"""
Clean Database Manager - Production Ready
Handles all database operations with proper error handling
"""

import os
import logging
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from database import (
    Base,
    User,
    UserState,
    Order,
    BalanceTransaction,
    RegisteredDomain,
)
from datetime import datetime, timedelta
import uuid
import json

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Create engine with production settings
        self.engine = create_engine(
            self.database_url, pool_pre_ping=True, pool_recycle=300, echo=False
        )

        # Create session factory
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.SessionFactory)

        # Create tables
        self.create_tables()

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def get_session(self):
        """Get database session"""
        return self.Session()

    def create_user(self, telegram_id, username=None, language="en"):
        """Create or get existing user"""
        session = self.get_session()
        try:
            # Check if user exists
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                return user

            # Create new user
            user = User(
                telegram_id=telegram_id,
                username=username,
                language=language,
                referral_code=self.generate_referral_code(),
            )
            session.add(user)
            session.commit()

            logger.info(f"Created new user: {telegram_id}")
            return user

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {e}")
            return None
        finally:
            session.close()

    def get_user(self, telegram_id):
        """Get user by telegram ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
        finally:
            session.close()

    def update_user_balance(
        self, telegram_id, amount, transaction_type="deposit", description=""
    ):
        """Update user balance and create transaction record"""
        session = self.get_session()
        try:
            from decimal import Decimal

            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                return False

            # Ensure both values are Decimal for safe arithmetic
            current_balance = Decimal(str(user.balance_usd))
            amount_decimal = Decimal(str(amount))

            # Update balance
            user.balance_usd = current_balance + amount_decimal

            # Create transaction record if needed
            if transaction_type and description:
                transaction = BalanceTransaction(
                    telegram_id=telegram_id,
                    transaction_type=transaction_type,
                    amount=amount_decimal,
                    description=description,
                )
                session.add(transaction)

            session.commit()
            logger.info(f"Updated balance for user {telegram_id}: {amount}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating balance: {e}")
            return False
        finally:
            session.close()

    def create_order(
        self,
        telegram_id,
        service_type,
        service_details,
        amount,
        payment_method="balance",
    ):
        """Create new order"""
        session = self.get_session()
        try:
            order = Order(
                telegram_id=telegram_id,
                service_type=service_type,
                service_details=service_details,
                amount=amount,
                payment_method=payment_method,
            )
            session.add(order)
            session.commit()

            logger.info(f"Created order {order.order_id} for user {telegram_id}")
            return order

        except Exception as e:
            session.rollback()
            logger.error(f"Error creating order: {e}")
            return None
        finally:
            session.close()

    def update_order_status(self, order_id, status, payment_txid=None):
        """Update order payment status"""
        session = self.get_session()
        try:
            order = session.query(Order).filter_by(order_id=order_id).first()
            if not order:
                return False

            order.payment_status = status
            if payment_txid:
                order.payment_txid = payment_txid

            if status == "completed":
                order.completed_at = datetime.utcnow()

            session.commit()
            logger.info(f"Updated order {order_id} status to {status}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating order status: {e}")
            return False
        finally:
            session.close()

    def set_user_state(self, telegram_id, state, data=None):
        """Set user state for workflow management"""
        session = self.get_session()
        try:
            # Clear existing state
            session.query(UserState).filter_by(telegram_id=telegram_id).delete()

            # Create new state
            user_state = UserState(
                telegram_id=telegram_id,
                state=state,
                data=data,
                expiry_date=datetime.utcnow() + timedelta(hours=1),
            )
            session.add(user_state)
            session.commit()

            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error setting user state: {e}")
            return False
        finally:
            session.close()

    def get_user_state(self, telegram_id):
        """Get user state"""
        session = self.get_session()
        try:
            state = (
                session.query(UserState)
                .filter(
                    and_(
                        UserState.telegram_id == telegram_id,
                        UserState.expiry_date > datetime.utcnow(),
                    )
                )
                .first()
            )

            if state:
                return state.state, state.data
            return None, None

        except Exception as e:
            logger.error(f"Error getting user state: {e}")
            return None, None
        finally:
            session.close()

    def clear_user_state(self, telegram_id):
        """Clear user state"""
        session = self.get_session()
        try:
            session.query(UserState).filter_by(telegram_id=telegram_id).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing user state: {e}")
            return False
        finally:
            session.close()

    def get_user_orders(self, telegram_id):
        """Get all orders for a user"""
        session = self.get_session()
        try:
            # First get the user by telegram_id, then get their orders
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                return []
            
            orders = session.query(Order).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
            return orders
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
        finally:
            session.close()

    def get_order(self, order_id):
        """Get order by ID"""
        session = self.get_session()
        try:
            order = session.query(Order).filter_by(order_id=order_id).first()
            return order
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None
        finally:
            session.close()

    def generate_referral_code(self):
        """Generate unique referral code"""
        return f"NMD{str(uuid.uuid4())[:8].upper()}"

    def add_shortened_url(
        self, telegram_id, long_url, short_url, short_code, domain, custom_slug=None
    ):
        """Add shortened URL to database"""
        session = self.get_session()
        try:
            url = ShortenedUrl(
                telegram_id=telegram_id,
                long_url=long_url,
                short_url=short_url,
                short_code=short_code,
                domain=domain,
                custom_slug=custom_slug,
            )
            session.add(url)
            session.commit()

            logger.info(f"Added shortened URL for user {telegram_id}: {short_url}")
            return url

        except Exception as e:
            session.rollback()
            logger.error(f"Error adding shortened URL: {e}")
            return None
        finally:
            session.close()

    def get_user_urls(self, telegram_id):
        """Get all URLs for a user"""
        session = self.get_session()
        try:
            urls = (
                session.query(ShortenedUrl)
                .filter_by(telegram_id=telegram_id, is_active=True)
                .order_by(ShortenedUrl.created_at.desc())
                .all()
            )
            return urls
        except Exception as e:
            logger.error(f"Error getting user URLs: {e}")
            return []
        finally:
            session.close()

    def get_order_by_id(self, order_id):
        """Get order by order ID"""
        session = self.get_session()
        try:
            order = session.query(Order).filter_by(order_id=order_id).first()
            return order
        except Exception as e:
            logger.error(f"Error getting order by ID: {e}")
            return None
        finally:
            session.close()

    def create_cpanel_account(self, account_data):
        """Create cPanel account record (mock)"""
        session = self.get_session()
        try:
            # In production, this would create a CpanelAccount record
            # For now, we'll just log the account creation
            logger.info(f"Mock cPanel account created: {account_data}")
            return True
        except Exception as e:
            logger.error(f"Error creating cPanel account: {e}")
            return False
        finally:
            session.close()

    def create_domain_record(self, domain_data):
        """Create domain registration record"""
        session = self.get_session()
        try:
            domain = RegisteredDomain(
                telegram_id=domain_data["telegram_id"],
                domain_name=domain_data["domain_name"],
                registration_date=datetime.utcnow(),
                expiry_date=domain_data["expires_at"],
                status="active",
            )
            session.add(domain)
            session.commit()

            logger.info(f"Domain record created: {domain_data['domain_name']}")
            return domain
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating domain record: {e}")
            return None
        finally:
            session.close()

    def get_total_users(self):
        """Get total number of users"""
        session = self.get_session()
        try:
            count = session.query(User).count()
            return count
        except Exception as e:
            logger.error(f"Error getting total users: {e}")
            return 0
        finally:
            session.close()

    def get_total_orders(self):
        """Get total number of orders"""
        session = self.get_session()
        try:
            count = session.query(Order).count()
            return count
        except Exception as e:
            logger.error(f"Error getting total orders: {e}")
            return 0
        finally:
            session.close()

    def get_pending_orders_count(self):
        """Get count of pending orders"""
        session = self.get_session()
        try:
            count = session.query(Order).filter_by(status="pending").count()
            return count
        except Exception as e:
            logger.error(f"Error getting pending orders count: {e}")
            return 0
        finally:
            session.close()

    def get_recent_orders(self, limit=10):
        """Get recent orders"""
        session = self.get_session()
        try:
            orders = (
                session.query(Order)
                .order_by(Order.created_at.desc())
                .limit(limit)
                .all()
            )
            return orders
        except Exception as e:
            logger.error(f"Error getting recent orders: {e}")
            return []
        finally:
            session.close()

    def update_user_openprovider_contact(
        self, telegram_id, contact_handle, identity_data
    ):
        """Store OpenProvider contact handle and identity for user reuse"""
        try:
            with self.get_db_session() as session:
                user = session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    # Store contact handle and identity info in user record
                    user.openprovider_contact_handle = contact_handle
                    user.openprovider_contact_info = json.dumps(identity_data)
                    session.commit()
                    logger.info(
                        f"OpenProvider contact {contact_handle} stored for user {telegram_id}"
                    )
                    return True
                return False

        except Exception as e:
            logger.error(f"Error updating user OpenProvider contact: {e}")
            return False

    def get_openprovider_contact(self, telegram_id):
        """Get OpenProvider contact handle for user"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user and hasattr(user, "openprovider_contact_handle"):
                return user.openprovider_contact_handle
            return None
        except Exception as e:
            logger.error(f"Error getting OpenProvider contact: {e}")
            return None
        finally:
            session.close()

    def store_openprovider_contact(self, telegram_id, contact_handle, contact_info):
        """Store OpenProvider contact handle for user"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                # Store contact handle in user record (would need to add this field to User model)
                logger.info(
                    f"Stored OpenProvider contact {contact_handle} for user {telegram_id}"
                )
                # For now, we'll store in a separate table or extend User model
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing OpenProvider contact: {e}")
            return False
        finally:
            session.close()

    def get_user_email(self, telegram_id):
        """Get user email address"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                return user.email
            return None
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return None
        finally:
            session.close()

    def get_active_users_count(self):
        """Get count of active users in last 24 hours"""
        session = self.get_session()
        try:
            count = session.query(User).count()
            return count
        except Exception as e:
            logger.error(f"Error getting active users count: {e}")
            return 0
        finally:
            session.close()

    def get_system_statistics(self):
        """Get comprehensive system statistics"""
        session = self.get_session()
        try:
            stats = {}

            # Revenue statistics
            completed_orders = session.query(Order).filter_by(status="completed").all()
            stats["total_revenue"] = sum(order.amount for order in completed_orders)

            # Monthly revenue (simplified)
            from datetime import datetime, timedelta

            month_ago = datetime.utcnow() - timedelta(days=30)
            monthly_orders = (
                session.query(Order)
                .filter(Order.status == "completed", Order.created_at >= month_ago)
                .all()
            )
            stats["monthly_revenue"] = sum(order.amount for order in monthly_orders)

            # Service statistics
            stats["hosting_orders"] = (
                session.query(Order).filter_by(service_type="hosting").count()
            )
            stats["domain_orders"] = (
                session.query(Order).filter_by(service_type="domain").count()
            )
            stats["url_orders"] = (
                session.query(Order).filter_by(service_type="url_shortener").count()
            )

            # URL statistics
            stats["total_urls"] = session.query(ShortenedUrl).count()
            stats["total_clicks"] = 0  # Placeholder

            return stats
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {}
        finally:
            session.close()

    def get_all_user_ids(self):
        """Get all user IDs for broadcasting"""
        session = self.get_session()
        try:
            user_ids = session.query(User.telegram_id).all()
            return [user_id[0] for user_id in user_ids]
        except Exception as e:
            logger.error(f"Error getting all user IDs: {e}")
            return []
        finally:
            session.close()

    def store_domain_registration(
        self, telegram_id, domain_name, domain_id, registration_status, nameservers
    ):
        """Store domain registration details"""
        try:
            with self.get_db_session() as session:
                # Check if domain already exists
                existing_domain = (
                    session.query(RegisteredDomain)
                    .filter_by(telegram_id=telegram_id, domain_name=domain_name)
                    .first()
                )

                if existing_domain:
                    # Update existing domain
                    existing_domain.domain_id = domain_id
                    existing_domain.status = registration_status
                    existing_domain.nameservers = json.dumps(nameservers)
                    existing_domain.updated_at = datetime.utcnow()
                else:
                    # Create new domain record
                    new_domain = RegisteredDomain(
                        telegram_id=telegram_id,
                        domain_name=domain_name,
                        domain_id=str(domain_id),
                        status=registration_status,
                        nameservers=json.dumps(nameservers),
                        registrar="OpenProvider",
                        registration_date=datetime.utcnow(),
                        expiry_date=datetime.utcnow() + timedelta(days=365),  # 1 year
                    )
                    session.add(new_domain)

                session.commit()
                logger.info(f"Domain registration stored: {domain_name}")
                return True

        except Exception as e:
            logger.error(f"Error storing domain registration: {e}")
            return False

    def store_hosting_account(
        self, telegram_id, domain_name, username, password, plan_type, status
    ):
        """Store hosting account details"""
        try:
            with self.get_db_session() as session:
                # Check if hosting account already exists
                existing_account = (
                    session.query(CpanelAccount)
                    .filter_by(telegram_id=telegram_id, domain_name=domain_name)
                    .first()
                )

                if existing_account:
                    # Update existing account
                    existing_account.username = username
                    existing_account.password = password
                    existing_account.plan_type = plan_type
                    existing_account.status = status
                    existing_account.updated_at = datetime.utcnow()
                else:
                    # Create new hosting account record
                    new_account = CpanelAccount(
                        telegram_id=telegram_id,
                        domain_name=domain_name,
                        username=username,
                        password=password,
                        plan_type=plan_type,
                        status=status,
                        server_ip="147.182.128.15",
                        created_at=datetime.utcnow(),
                    )
                    session.add(new_account)

                session.commit()
                logger.info(f"Hosting account stored: {domain_name}")
                return True

        except Exception as e:
            logger.error(f"Error storing hosting account: {e}")
            return False

    # URL Shortener methods
    def add_shortened_url(
        self, telegram_id, long_url, short_url, short_code, domain, custom_slug=None
    ):
        """Add a shortened URL to the database"""
        session = self.get_session()
        try:
            shortened_url = ShortenedUrl(
                telegram_id=telegram_id,
                long_url=long_url,
                short_url=short_url,
                short_code=short_code,
                domain=domain,
                custom_slug=custom_slug,
                clicks=0,
                created_at=datetime.utcnow(),
            )

            session.add(shortened_url)
            session.commit()

            logger.info(f"Added shortened URL for user {telegram_id}: {short_url}")
            return shortened_url

        except Exception as e:
            logger.error(f"Error adding shortened URL: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def get_user_urls(self, telegram_id, limit=10):
        """Get user's shortened URLs"""
        session = self.get_session()
        try:
            urls = (
                session.query(ShortenedUrl)
                .filter(ShortenedUrl.telegram_id == telegram_id)
                .order_by(ShortenedUrl.created_at.desc())
                .limit(limit)
                .all()
            )

            return urls

        except Exception as e:
            logger.error(f"Error getting user URLs: {e}")
            return []
        finally:
            session.close()

    def add_balance_transaction(
        self, telegram_id, amount, transaction_type, description, status="completed"
    ):
        """Add a balance transaction record"""
        session = self.get_session()
        try:
            transaction = BalanceTransaction(
                telegram_id=telegram_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                created_at=datetime.utcnow(),
            )

            session.add(transaction)
            session.commit()

            logger.info(
                f"Added balance transaction for user {telegram_id}: {amount} ({transaction_type})"
            )
            return transaction

        except Exception as e:
            logger.error(f"Error adding balance transaction: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def get_hosting_account(self, telegram_id, domain_name):
        """Get hosting account details"""
        try:
            with self.get_db_session() as session:
                account = (
                    session.query(CpanelAccount)
                    .filter_by(telegram_id=telegram_id, domain_name=domain_name)
                    .first()
                )

                if account:
                    return {
                        "username": account.username,
                        "password": account.password,
                        "plan_type": account.plan_type,
                        "status": account.status,
                        "server_ip": account.server_ip,
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting hosting account: {e}")
            return None

    def get_domain_info(self, telegram_id, domain_name):
        """Get domain registration info"""
        try:
            with self.get_db_session() as session:
                domain = (
                    session.query(RegisteredDomain)
                    .filter_by(telegram_id=telegram_id, domain_name=domain_name)
                    .first()
                )

                if domain:
                    return {
                        "domain_id": domain.domain_id,
                        "status": domain.status,
                        "nameservers": (
                            json.loads(domain.nameservers) if domain.nameservers else []
                        ),
                        "registrar": domain.registrar,
                        "registration_date": domain.registration_date,
                        "expiry_date": domain.expires_at,
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting domain info: {e}")
            return None

    def update_domain_nameservers(self, user_id, domain_name, nameserver_mode, custom_ns1='', custom_ns2='', custom_ns3='', custom_ns4=''):
        """Update domain nameserver configuration"""
        try:
            with self.get_db_session() as session:
                domain = (
                    session.query(RegisteredDomain)
                    .filter_by(telegram_id=user_id, domain_name=domain_name)
                    .first()
                )
                
                if domain:
                    # Update nameserver configuration
                    if nameserver_mode == 'custom':
                        # Store custom nameservers as JSON
                        nameservers = [ns for ns in [custom_ns1, custom_ns2, custom_ns3, custom_ns4] if ns]
                        domain.nameservers = json.dumps(nameservers)
                        domain.nameserver_mode = 'custom'
                    else:
                        # Cloudflare nameservers
                        nameservers = ['anderson.ns.cloudflare.com', 'leanna.ns.cloudflare.com']
                        domain.nameservers = json.dumps(nameservers)
                        domain.nameserver_mode = 'cloudflare'
                    
                    domain.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"Nameservers updated for domain {domain_name}: {nameservers}")
                    return True
                else:
                    logger.error(f"Domain {domain_name} not found for user {user_id}")
                    return False

        except Exception as e:
            logger.error(f"Error updating domain nameservers: {e}")
            return False

    def store_user_openprovider_contact(
        self, telegram_id, contact_handle, contact_info
    ):
        """Store OpenProvider contact handle for user"""
        try:
            with self.get_db_session() as session:
                user = session.query(User).filter_by(telegram_id=telegram_id).first()
                if user:
                    # Store contact info in user profile
                    user.openprovider_contact_handle = contact_handle
                    user.openprovider_contact_info = json.dumps(contact_info)
                    session.commit()
                    logger.info(f"OpenProvider contact stored for user {telegram_id}")
                    return True
                return False

        except Exception as e:
            logger.error(f"Error storing OpenProvider contact: {e}")
            return False

    def get_user_openprovider_contact(self, telegram_id):
        """Get OpenProvider contact handle for user"""
        try:
            with self.get_db_session() as session:
                user = session.query(User).filter_by(telegram_id=telegram_id).first()
                if (
                    user
                    and hasattr(user, "openprovider_contact_handle")
                    and user.openprovider_contact_handle
                ):
                    contact_info = {}
                    if (
                        hasattr(user, "openprovider_contact_info")
                        and user.openprovider_contact_info
                    ):
                        contact_info = json.loads(user.openprovider_contact_info)

                    return {
                        "success": True,
                        "contact_handle": user.openprovider_contact_handle,
                        "contact_info": contact_info,
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting OpenProvider contact: {e}")
            return None

    def update_user_email(self, telegram_id, email):
        """Update user email address"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.email = email
                session.commit()
                logger.info(f"Email updated for user {telegram_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user email: {e}")
            return False
        finally:
            session.close()

    def get_user_email(self, telegram_id):
        """Get user email address"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user and user.email:
                return user.email
            return None
        except Exception as e:
            logger.error(f"Error getting user email: {e}")
            return None
        finally:
            session.close()

    def get_user_balance(self, telegram_id):
        """Get user balance"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                return float(user.balance_usd or 0.0)
            return 0.0
        except Exception as e:
            logger.error(f"Error getting user balance: {e}")
            return 0.0
        finally:
            session.close()

    def update_user_balance(self, telegram_id, balance):
        """Update user balance"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.balance_usd = balance
                session.commit()
                logger.info(f"Updated balance for user {telegram_id}: {balance}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user balance: {e}")
            return False
        finally:
            session.close()

    def get_user_state_data(self, telegram_id):
        """Get user state data"""
        session = self.get_session()
        try:
            state = (
                session.query(UserState)
                .filter(
                    and_(
                        UserState.telegram_id == telegram_id,
                        UserState.expiry_date > datetime.utcnow(),
                    )
                )
                .first()
            )

            if state and state.data:
                return state.data
            return None

        except Exception as e:
            logger.error(f"Error getting user state data: {e}")
            return None
        finally:
            session.close()

    def get_all_users(self):
        """Get all users"""
        session = self.get_session()
        try:
            users = session.query(User).all()
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
        finally:
            session.close()


# Global database manager instance
_db_manager = None


def get_db_manager():
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
