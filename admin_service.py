"""
Nomadly2 - Complete Admin Dashboard Service v1.4
Comprehensive admin management and monitoring system
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database import (
    get_db_manager,
    User,
    RegisteredDomain,
    Order,
    WalletTransaction,
    AdminNotification,
)
from translations import get_translations


class AdminService:
    """Complete admin dashboard and management service"""

    def __init__(self):
        self.db = get_db_manager()
        self.translations = get_translations()
        self.admin_telegram_ids = self._get_admin_telegram_ids()

    def _get_admin_telegram_ids(self) -> List[int]:
        """Get list of admin Telegram IDs from environment"""
        admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS", "")
        if admin_ids_str:
            try:
                return [
                    int(id_str.strip())
                    for id_str in admin_ids_str.split(",")
                    if id_str.strip()
                ]
            except ValueError:
                return []
        return []

    def is_admin(self, telegram_id: int) -> bool:
        """Check if user is admin"""
        if telegram_id in self.admin_telegram_ids:
            return True

        # Check database for admin flag
        with self.db.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            return user.is_admin if user else False

    def get_system_overview(self) -> Dict:
        """Get comprehensive system overview"""
        try:
            stats = self.db.get_system_statistics()

            # Get recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)

            with self.db.get_session() as session:
                # Recent registrations
                recent_domains = (
                    session.query(RegisteredDomain)
                    .filter(RegisteredDomain.registration_date >= yesterday)
                    .count()
                )

                # Recent transactions
                recent_transactions = (
                    session.query(WalletTransaction)
                    .filter(WalletTransaction.created_at >= yesterday)
                    .count()
                )

                # Recent users
                recent_users = (
                    session.query(User).filter(User.created_at >= yesterday).count()
                )

                # Pending payments
                pending_payments = (
                    session.query(Order)
                    .filter(Order.payment_status == "pending")
                    .count()
                )

                # Total revenue (last 30 days)
                last_month = datetime.now() - timedelta(days=30)
                monthly_revenue = (
                    session.query(WalletTransaction)
                    .filter(
                        WalletTransaction.transaction_type == "payment",
                        WalletTransaction.created_at >= last_month,
                    )
                    .with_entities(WalletTransaction.amount)
                    .all()
                )

                total_monthly_revenue = (
                    sum(float(t.amount) for t in monthly_revenue)
                    if monthly_revenue
                    else 0
                )

            return {
                "success": True,
                "overview": {
                    "total_users": stats.get("total_users", 0),
                    "total_domains": stats.get("total_domains", 0),
                    "total_transactions": stats.get("total_transactions", 0),
                    "total_revenue": stats.get("total_revenue", 0),
                    "pending_orders": stats.get("pending_orders", 0),
                },
                "recent_activity": {
                    "new_users_24h": recent_users,
                    "domains_registered_24h": recent_domains,
                    "transactions_24h": recent_transactions,
                    "pending_payments": pending_payments,
                    "monthly_revenue": total_monthly_revenue,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_user_management(self, page: int = 1, limit: int = 50) -> Dict:
        """Get user management interface data"""
        try:
            offset = (page - 1) * limit

            with self.db.get_session() as session:
                # Get users with pagination
                users_query = session.query(User).order_by(User.created_at.desc())
                total_users = users_query.count()
                users = users_query.offset(offset).limit(limit).all()

                user_list = []
                for user in users:
                    # Get user's domain count
                    domain_count = (
                        session.query(RegisteredDomain)
                        .filter(RegisteredDomain.telegram_id == user.telegram_id)
                        .count()
                    )

                    # Get user's transaction count
                    transaction_count = (
                        session.query(WalletTransaction)
                        .filter(WalletTransaction.telegram_id == user.telegram_id)
                        .count()
                    )

                    user_info = {
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "language_code": user.language_code,
                        "balance_usd": float(user.balance_usd),
                        "is_admin": user.is_admin,
                        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "domain_count": domain_count,
                        "transaction_count": transaction_count,
                    }
                    user_list.append(user_info)

                return {
                    "success": True,
                    "users": user_list,
                    "pagination": {
                        "current_page": page,
                        "total_users": total_users,
                        "total_pages": (total_users + limit - 1) // limit,
                        "limit": limit,
                    },
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_domain_portfolio(self, page: int = 1, limit: int = 50) -> Dict:
        """Get all registered domains for admin overview"""
        try:
            offset = (page - 1) * limit

            with self.db.get_session() as session:
                # Get domains with user information
                domains_query = (
                    session.query(RegisteredDomain, User)
                    .join(User, RegisteredDomain.telegram_id == User.telegram_id)
                    .order_by(RegisteredDomain.registration_date.desc())
                )

                total_domains = domains_query.count()
                domains = domains_query.offset(offset).limit(limit).all()

                domain_list = []
                for domain_record, user in domains:
                    domain_info = {
                        "id": domain_record.id,
                        "domain_name": domain_record.domain_name,
                        "owner": {
                            "telegram_id": user.telegram_id,
                            "username": user.username,
                            "first_name": user.first_name,
                        },
                        "status": domain_record.status,
                        "registration_date": (
                            domain_record.registration_date.strftime("%Y-%m-%d")
                            if domain_record.registration_date
                            else None
                        ),
                        "expiry_date": (
                            domain_record.expiry_date.strftime("%Y-%m-%d")
                            if domain_record.expiry_date
                            else None
                        ),
                        "nameserver_mode": domain_record.nameserver_mode,
                        "auto_renew": domain_record.auto_renew,
                        "price_paid": (
                            float(domain_record.price_paid)
                            if domain_record.price_paid
                            else 0
                        ),
                        "payment_method": domain_record.payment_method,
                        "Nameword_domain_id": domain_record.Nameword_domain_id,
                        "cloudflare_zone_id": domain_record.cloudflare_zone_id,
                    }
                    domain_list.append(domain_info)

                return {
                    "success": True,
                    "domains": domain_list,
                    "pagination": {
                        "current_page": page,
                        "total_domains": total_domains,
                        "total_pages": (total_domains + limit - 1) // limit,
                        "limit": limit,
                    },
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_financial_overview(self, days: int = 30) -> Dict:
        """Get financial analytics and revenue tracking"""
        try:
            start_date = datetime.now() - timedelta(days=days)

            with self.db.get_session() as session:
                # Get all transactions in date range
                transactions = (
                    session.query(WalletTransaction)
                    .filter(WalletTransaction.created_at >= start_date)
                    .all()
                )

                # Categorize transactions
                revenue = 0
                deposits = 0
                withdrawals = 0
                transaction_summary = {}

                for transaction in transactions:
                    amount = float(transaction.amount)

                    if transaction.transaction_type == "payment":
                        revenue += amount
                    elif transaction.transaction_type == "deposit":
                        deposits += amount
                    elif transaction.transaction_type == "withdrawal":
                        withdrawals += amount

                    # Count by type
                    t_type = transaction.transaction_type
                    if t_type not in transaction_summary:
                        transaction_summary[t_type] = {"count": 0, "total_amount": 0}

                    transaction_summary[t_type]["count"] += 1
                    transaction_summary[t_type]["total_amount"] += amount

                # Get domain registration revenue
                domain_orders = (
                    session.query(Order)
                    .filter(
                        Order.service_type == "domain_registration",
                        Order.payment_status == "completed",
                        Order.created_at >= start_date,
                    )
                    .all()
                )

                domain_revenue = sum(float(order.amount) for order in domain_orders)
                domain_count = len(domain_orders)

                return {
                    "success": True,
                    "period": f"{days} days",
                    "revenue_summary": {
                        "total_revenue": revenue,
                        "total_deposits": deposits,
                        "total_withdrawals": withdrawals,
                        "domain_revenue": domain_revenue,
                        "domain_sales_count": domain_count,
                        "net_flow": deposits - withdrawals,
                    },
                    "transaction_breakdown": transaction_summary,
                    "period_start": start_date.strftime("%Y-%m-%d"),
                    "period_end": datetime.now().strftime("%Y-%m-%d"),
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_notifications(self, status: str = "unread", limit: int = 100) -> Dict:
        """Get admin notifications"""
        try:
            with self.db.get_session() as session:
                query = session.query(AdminNotification).order_by(
                    AdminNotification.created_at.desc()
                )

                if status == "unread":
                    query = query.filter(AdminNotification.is_read == False)
                elif status == "read":
                    query = query.filter(AdminNotification.is_read == True)

                notifications = query.limit(limit).all()

                notification_list = []
                for notification in notifications:
                    notification_info = {
                        "id": notification.id,
                        "type": notification.notification_type,
                        "title": notification.title,
                        "message": notification.message,
                        "severity": notification.severity,
                        "is_read": notification.is_read,
                        "created_at": notification.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "telegram_id": notification.telegram_id,
                        "metadata": notification.notification_metadata,
                    }
                    notification_list.append(notification_info)

                return {
                    "success": True,
                    "notifications": notification_list,
                    "total_count": len(notification_list),
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def mark_notification_read(self, notification_id: int) -> Dict:
        """Mark notification as read"""
        try:
            with self.db.get_session() as session:
                notification = (
                    session.query(AdminNotification)
                    .filter(AdminNotification.id == notification_id)
                    .first()
                )

                if notification:
                    notification.is_read = True
                    session.commit()
                    return {"success": True}
                else:
                    return {"success": False, "error": "Notification not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def adjust_user_balance(
        self, telegram_id: int, amount: float, description: str = "Admin adjustment"
    ) -> Dict:
        """Adjust user balance (admin action)"""
        try:
            # Update balance and create transaction record
            self.db.update_user_balance(
                telegram_id=telegram_id,
                amount=amount,
                transaction_type="admin_adjustment",
            )

            # Create admin notification
            self.db.create_admin_notification(
                notification_type="balance_adjustment",
                title="Balance Adjusted",
                message=f"Balance adjusted by ${amount} for user {telegram_id}: {description}",
                telegram_id=telegram_id,
                notification_metadata={
                    "adjustment_amount": amount,
                    "description": description,
                },
            )

            return {
                "success": True,
                "message": f"Balance adjusted by ${amount}",
                "new_balance": self.db.get_user_balance(telegram_id),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_users(self, query: str) -> Dict:
        """Search users by username, first name, or Telegram ID"""
        try:
            with self.db.get_session() as session:
                # Try to search by Telegram ID first
                users = []

                if query.isdigit():
                    # Search by Telegram ID
                    user = (
                        session.query(User)
                        .filter(User.telegram_id == int(query))
                        .first()
                    )
                    if user:
                        users = [user]

                if not users:
                    # Search by username or name
                    users = (
                        session.query(User)
                        .filter(
                            (User.username.ilike(f"%{query}%"))
                            | (User.first_name.ilike(f"%{query}%"))
                            | (User.last_name.ilike(f"%{query}%"))
                        )
                        .limit(50)
                        .all()
                    )

                user_list = []
                for user in users:
                    user_info = {
                        "telegram_id": user.telegram_id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "balance_usd": float(user.balance_usd),
                        "is_admin": user.is_admin,
                        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    user_list.append(user_info)

                return {
                    "success": True,
                    "users": user_list,
                    "query": query,
                    "count": len(user_list),
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_system_health(self) -> Dict:
        """Get system health and API status"""
        try:
            # Check database connectivity
            db_status = True
            try:
                self.db.get_system_statistics()
            except:
                db_status = False

            # Get API status from environment or test
            api_status = {
                "Nameword": bool(os.getenv("OPENPROVIDER_USERNAME")),
                "cloudflare": bool(os.getenv("CLOUDFLARE_API_TOKEN")),
                "blockbee": bool(os.getenv("BLOCKBEE_API_KEY")),
            }

            # Get recent error notifications
            with self.db.get_session() as session:
                error_notifications = (
                    session.query(AdminNotification)
                    .filter(
                        AdminNotification.notification_type.in_(
                            ["error", "api_error", "payment_error"]
                        ),
                        AdminNotification.created_at
                        >= datetime.now() - timedelta(hours=24),
                    )
                    .count()
                )

            health_score = 100
            if not db_status:
                health_score -= 30
            if not all(api_status.values()):
                health_score -= 20
            if error_notifications > 10:
                health_score -= 15

            return {
                "success": True,
                "health_score": max(0, health_score),
                "database_status": db_status,
                "api_status": api_status,
                "error_count_24h": error_notifications,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Global service instance
_admin_service = None


def get_admin_service() -> AdminService:
    """Get admin service instance"""
    global _admin_service
    if _admin_service is None:
        _admin_service = AdminService()
    return _admin_service
