"""
Admin Panel for Nomadly2 Bot
Provides administrative interface for system management
"""

import logging
from typing import Dict, List
from datetime import datetime, timedelta
from database import get_db_manager, User, RegisteredDomain, Order, WalletTransaction
from payment_service import get_payment_service
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


class AdminPanel:
    """Administrative interface for bot management"""

    def __init__(self):
        self.db = get_db_manager()
        self.payment_service = get_payment_service()

        # Admin user IDs (telegram IDs of authorized admins)
        self.admin_users = {
            123456789,  # Replace with actual admin telegram IDs
            987654321,  # Add more admin IDs as needed
        }

    def is_admin(self, telegram_id: int) -> bool:
        """Check if user is authorized admin"""
        return telegram_id in self.admin_users

    async def show_admin_dashboard(self, query):
        """Show main admin dashboard"""
        if not self.is_admin(query.from_user.id):
            await query.answer("⚠️ Unauthorized access", show_alert=True)
            return

        # Get system statistics
        stats = self.get_system_statistics()

        dashboard_text = (
            "🏴‍☠️ *Nomadly2 Admin Dashboard*\n\n"
            "📊 *System Overview:*\n"
            f"• **Total Users:** {stats.get('total_users', 0)}\n"
            f"• **Active Users (7d):** {stats.get('active_users_7d', 0)}\n"
            f"• **Total Domains:** {stats.get('total_domains', 0)}\n"
            f"• **Total Orders:** {stats.get('total_orders', 0)}\n\n"
            "💰 *Financial Overview:*\n"
            f"• **Total Revenue:** ${stats.get('total_revenue', 0):.2f}\n"
            f"• **Pending Payments:** {stats.get('pending_payments', 0)}\n"
            f"• **Revenue (30d):** ${stats.get('revenue_30d', 0):.2f}\n\n"
            "🕐 *Last Updated:* " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        keyboard = [
            [
                InlineKeyboardButton("👥 User Management", callback_data="admin_users"),
                InlineKeyboardButton(
                    "💰 Financial Reports", callback_data="admin_finance"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🌐 Domain Management", callback_data="admin_domains"
                ),
                InlineKeyboardButton(
                    "📋 Orders & Payments", callback_data="admin_orders"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📢 Send Broadcast", callback_data="admin_broadcast"
                ),
                InlineKeyboardButton("⚙️ System Status", callback_data="admin_system"),
            ],
            [
                InlineKeyboardButton("📊 Analytics", callback_data="admin_analytics"),
                InlineKeyboardButton("🔧 Settings", callback_data="admin_settings"),
            ],
            [InlineKeyboardButton("⬅️ Main Menu", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            dashboard_text, parse_mode="Markdown", reply_markup=reply_markup
        )

    async def show_user_management(self, query):
        """Show user management interface"""
        if not self.is_admin(query.from_user.id):
            return

        # Get recent users
        recent_users = self.get_recent_users(limit=10)

        user_text = "👥 *User Management*\n\n" "📊 *Recent Users:*\n"

        for user in recent_users:
            joined_date = user.created_at.strftime("%m/%d")
            user_text += f"• {user.telegram_id} - Joined {joined_date} - ${user.balance_usd:.2f}\n"

        user_text += (
            "\n🔧 *Management Actions:*\n"
            "• View detailed user information\n"
            "• Adjust user balances\n"
            "• Send direct messages\n"
            "• Block/unblock users"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔍 Search User", callback_data="admin_search_user"
                ),
                InlineKeyboardButton(
                    "💰 Adjust Balance", callback_data="admin_adjust_balance"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📨 Send Message", callback_data="admin_send_message"
                ),
                InlineKeyboardButton(
                    "🚫 Manage Blocks", callback_data="admin_manage_blocks"
                ),
            ],
            [
                InlineKeyboardButton(
                    "📊 User Statistics", callback_data="admin_user_stats"
                ),
                InlineKeyboardButton(
                    "⬅️ Back to Dashboard", callback_data="admin_dashboard"
                ),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            user_text, parse_mode="Markdown", reply_markup=reply_markup
        )

    async def show_financial_reports(self, query):
        """Show financial reports and statistics"""
        if not self.is_admin(query.from_user.id):
            return

        # Get financial data
        finance_data = self.get_financial_statistics()

        finance_text = (
            "💰 *Financial Reports*\n\n"
            "📊 *Revenue Overview:*\n"
            f"• **Total Revenue:** ${finance_data.get('total_revenue', 0):.2f}\n"
            f"• **This Month:** ${finance_data.get('revenue_month', 0):.2f}\n"
            f"• **Last 7 Days:** ${finance_data.get('revenue_7d', 0):.2f}\n"
            f"• **Today:** ${finance_data.get('revenue_today', 0):.2f}\n\n"
            "💳 *Payment Methods:*\n"
            f"• **Crypto Payments:** {finance_data.get('crypto_payments', 0)}\n"
            f"• **Balance Payments:** {finance_data.get('balance_payments', 0)}\n"
            f"• **Pending Payments:** {finance_data.get('pending_payments', 0)}\n\n"
            "🎯 *Top Services:*\n"
            f"• **Domain Registrations:** {finance_data.get('domain_orders', 0)}\n"
            f"• **Wallet Deposits:** {finance_data.get('deposit_orders', 0)}\n"
            f"• **Other Services:** {finance_data.get('other_orders', 0)}\n\n"
            "💰 *Average Order Value:* ${:.2f}".format(
                finance_data.get("avg_order_value", 0)
            )
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "📈 Detailed Analytics", callback_data="admin_detailed_analytics"
                ),
                InlineKeyboardButton(
                    "💹 Export Report", callback_data="admin_export_finance"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back to Dashboard", callback_data="admin_dashboard"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            finance_text, parse_mode="Markdown", reply_markup=reply_markup
        )

    async def show_domain_management(self, query):
        """Show domain management interface"""
        if not self.is_admin(query.from_user.id):
            return

        # Get domain statistics
        domain_stats = self.get_domain_statistics()

        domain_text = (
            "🌐 *Domain Management*\n\n"
            "📊 *Domain Overview:*\n"
            f"• **Total Domains:** {domain_stats.get('total_domains', 0)}\n"
            f"• **Active Domains:** {domain_stats.get('active_domains', 0)}\n"
            f"• **Recent Registrations:** {domain_stats.get('recent_registrations', 0)}\n"
            f"• **Expiring Soon (30d):** {domain_stats.get('expiring_soon', 0)}\n\n"
            "🔧 *Management Actions:*\n"
            "• View all registered domains\n"
            "• Check domain status\n"
            "• Manage DNS settings\n"
            "• Handle renewals"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "📋 View All Domains", callback_data="admin_view_domains"
                ),
                InlineKeyboardButton(
                    "⚠️ Expiring Domains", callback_data="admin_expiring_domains"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔍 Search Domain", callback_data="admin_search_domain"
                ),
                InlineKeyboardButton(
                    "📊 Domain Analytics", callback_data="admin_domain_analytics"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back to Dashboard", callback_data="admin_dashboard"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            domain_text, parse_mode="Markdown", reply_markup=reply_markup
        )

    async def send_broadcast_message(self, query):
        """Interface for sending broadcast messages"""
        if not self.is_admin(query.from_user.id):
            return

        broadcast_text = (
            "📢 *Broadcast Message*\n\n"
            "⚠️ *Important Notice*\n"
            "This will send a message to ALL active users.\n\n"
            "📝 *Instructions:*\n"
            "1. Type your message in the next response\n"
            "2. Message will be sent to all users\n"
            "3. Use Markdown formatting if needed\n"
            "4. Keep messages professional and relevant\n\n"
            "📊 *Target Audience:*\n"
            f"• Active users: {self.get_system_statistics().get('total_users', 0)}\n"
            "• Message will be sent immediately\n"
            "• Delivery status will be tracked"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Compose Message", callback_data="admin_compose_broadcast"
                ),
                InlineKeyboardButton(
                    "📋 Message Templates", callback_data="admin_broadcast_templates"
                ),
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Back to Dashboard", callback_data="admin_dashboard"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            broadcast_text, parse_mode="Markdown", reply_markup=reply_markup
        )

    def get_system_statistics(self) -> Dict:
        """Get comprehensive system statistics"""
        try:
            session = self.db.get_session()

            # Count users
            total_users = session.query(User).count()

            # Count active users (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            active_users_7d = (
                session.query(User)
                .filter(User.last_activity > week_ago)
                .count()
            )

            # Count domains
            total_domains = session.query(RegisteredDomain).count()

            # Count orders
            total_orders = session.query(Order).count()

            # Calculate revenue
            completed_orders = (
                session.query(Order)
                .filter(Order.payment_status == "completed")
                .all()
            )
            total_revenue = sum(order.amount_usd for order in completed_orders)

            # Revenue last 30 days
            month_ago = datetime.now() - timedelta(days=30)
            recent_orders = (
                session.query(Order)
                .filter(
                    Order.payment_status == "completed",
                    Order.created_at > month_ago,
                )
                .all()
            )
            revenue_30d = sum(order.amount_usd for order in recent_orders)

            # Pending payments
            pending_payments = (
                session.query(Order)
                .filter(Order.payment_status == "pending")
                .count()
            )

            session.close()

            return {
                "total_users": total_users,
                "active_users_7d": active_users_7d,
                "total_domains": total_domains,
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "revenue_30d": revenue_30d,
                "pending_payments": pending_payments,
            }

        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {}

    def get_recent_users(self, limit: int = 10) -> List:
        """Get recently registered users"""
        try:
            session = self.db.get_session()
            users = (
                session.query(User)
                .order_by(User.created_at.desc())
                .limit(limit)
                .all()
            )
            session.close()
            return users
        except Exception as e:
            logger.error(f"Error getting recent users: {e}")
            return []

    def get_financial_statistics(self) -> Dict:
        """Get detailed financial statistics"""
        try:
            session = self.db.get_session()

            # All completed orders
            completed_orders = (
                session.query(Order)
                .filter(Order.payment_status == "completed")
                .all()
            )

            total_revenue = sum(order.amount_usd for order in completed_orders)

            # This month
            month_start = datetime.now().replace(day=1)
            month_orders = [o for o in completed_orders if o.created_at >= month_start]
            revenue_month = sum(order.amount_usd for order in month_orders)

            # Last 7 days
            week_ago = datetime.now() - timedelta(days=7)
            week_orders = [o for o in completed_orders if o.created_at >= week_ago]
            revenue_7d = sum(order.amount_usd for order in week_orders)

            # Today
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_orders = [o for o in completed_orders if o.created_at >= today_start]
            revenue_today = sum(order.amount_usd for order in today_orders)

            # Payment methods
            crypto_payments = len(
                [o for o in completed_orders if o.payment_method.startswith("crypto_")]
            )
            balance_payments = len(
                [o for o in completed_orders if o.payment_method == "balance"]
            )

            # Pending payments
            pending_payments = (
                session.query(Order)
                .filter(Order.payment_status == "pending")
                .count()
            )

            # Service breakdown
            domain_orders = len(
                [o for o in completed_orders if o.service_type == "domain_registration"]
            )
            deposit_orders = len(
                [o for o in completed_orders if o.service_type == "wallet_deposit"]
            )
            other_orders = len(completed_orders) - domain_orders - deposit_orders

            # Average order value
            avg_order_value = (
                total_revenue / len(completed_orders) if completed_orders else 0
            )

            session.close()

            return {
                "total_revenue": total_revenue,
                "revenue_month": revenue_month,
                "revenue_7d": revenue_7d,
                "revenue_today": revenue_today,
                "crypto_payments": crypto_payments,
                "balance_payments": balance_payments,
                "pending_payments": pending_payments,
                "domain_orders": domain_orders,
                "deposit_orders": deposit_orders,
                "other_orders": other_orders,
                "avg_order_value": avg_order_value,
            }

        except Exception as e:
            logger.error(f"Error getting financial statistics: {e}")
            return {}

    def get_domain_statistics(self) -> Dict:
        """Get domain-specific statistics"""
        try:
            session = self.db.get_session()

            total_domains = session.query(RegisteredDomain).count()

            # Active domains (not expired)
            today = datetime.now()
            active_domains = (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.expires_at > today)
                .count()
            )

            # Recent registrations (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_registrations = (
                session.query(RegisteredDomain)
                .filter(RegisteredDomain.created_at > week_ago)
                .count()
            )

            # Expiring soon (next 30 days)
            month_from_now = datetime.now() + timedelta(days=30)
            expiring_soon = (
                session.query(RegisteredDomain)
                .filter(
                    RegisteredDomain.expires_at.between(today, month_from_now)
                )
                .count()
            )

            session.close()

            return {
                "total_domains": total_domains,
                "active_domains": active_domains,
                "recent_registrations": recent_registrations,
                "expiring_soon": expiring_soon,
            }

        except Exception as e:
            logger.error(f"Error getting domain statistics: {e}")
            return {}


# Global admin panel instance
_admin_panel = None


def get_admin_panel():
    """Get global admin panel instance"""
    global _admin_panel
    if _admin_panel is None:
        _admin_panel = AdminPanel()
    return _admin_panel
