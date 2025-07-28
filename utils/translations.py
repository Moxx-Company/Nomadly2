"""
Clean Translation System - Multi-language Support
Supports English, French, Hindi, Chinese, Spanish
"""

import logging

logger = logging.getLogger(__name__)


class Translations:

    @staticmethod
    def get_user_language(db_manager, user_id):
        """Get user's preferred language"""
        try:
            user = db_manager.get_user(user_id)
            return user.language if user and user.language else "en"
        except:
            return "en"

    @staticmethod
    def get_text(key, language="en", **kwargs):
        """Get translated text"""
        try:
            text = Translations.TRANSLATIONS.get(language, {}).get(key, key)
            if kwargs:
                return text.format(**kwargs)
            return text
        except:
            return key

    TRANSLATIONS = {
        "en": {
            # Main menu
            "welcome_nomadly": "🌐 Welcome to Nomadly - Global Digital Services",
            "current_balance": "💰 Current Balance: ${balance:.2f} USD",
            "cpanel_hosting": "🖥️ cPanel Hosting",
            "register_domain": "🌐 Register Domain",
            "url_shortener": "🔗 URL Shortener",
            "my_balance": "💰 My Balance",
            "my_services": "📋 My Services",
            "help_message": "🆘 Nomadly Help\n\nAvailable commands:\n/start - Main menu\n/help - Show help",
            # Hosting
            "hosting_menu": "🖥️ Choose Your cPanel Hosting Plan",
            "basic_hosting": "📦 Basic Plan - $9.99/month",
            "pro_hosting": "💼 Professional Plan - $19.99/month",
            "business_hosting": "🏢 Business Plan - $39.99/month",
            # Domains
            "domain_menu": "🌐 Domain Registration",
            "domain_com": ".com - from $11.98/year",
            "domain_net": ".net - $14.99/year",
            "domain_org": ".org - $13.99/year",
            # URL Shortener
            "url_shortener_menu": "🔗 URL Shortener Service",
            "quick_shorten": "⚡ Quick Shorten",
            "custom_slug": "✏️ Custom Slug",
            "my_urls": "📋 My URLs",
            # Balance
            "balance_menu": "💰 Balance: ${balance:.2f} USD",
            "add_funds": "💰 Add Funds",
            "transaction_history": "📊 Transaction History",
            # Services
            "services_menu": "📋 My Active Services",
            "my_domains": "🌐 My Domains",
            "my_hosting": "🖥️ My Hosting",
            "url_stats": "📊 URL Statistics",
            # Navigation
            "back_to_main": "← Back to Main Menu",
            "continue": "Continue",
            # Analytics and Admin Dashboard
            "analytics_dashboard": "📊 Analytics Dashboard",
            "select_analytics_type": "Select Analytics Type",
            "url_analytics": "URL Analytics",
            "payment_analytics": "Payment Analytics",
            "system_stats": "System Statistics",
            "back_to_analytics": "Back to Analytics",
            "back_to_admin": "Back to Admin",
            "refresh_analytics": "Refresh Analytics",
            "detailed_report": "Detailed Report",
            "export_report": "Export Report",
            "test_all_apis": "Test All APIs",
            # URL Analytics
            "url_analytics_title": "URL Shortener Analytics",
            "total_urls_created": "Total URLs Created",
            "total_clicks": "Total Clicks",
            "unique_visitors": "Unique Visitors",
            "top_domains": "Top Domains",
            "recent_activity": "Recent Activity",
            "today": "Today",
            "this_week": "This Week",
            "top_countries": "Top Countries",
            # Payment Analytics
            "payment_analytics_title": "Payment & Revenue Analytics",
            "total_revenue": "Total Revenue",
            "total_orders": "Total Orders",
            "successful_payments": "Successful Payments",
            "success_rate": "Success Rate",
            "revenue_by_service": "Revenue by Service",
            "popular_cryptocurrencies": "Popular Cryptocurrencies",
            "recent_performance": "Recent Performance",
            "bonus_statistics": "Bonus Statistics",
            "total_bonuses_given": "Total Bonuses Given",
            "first_deposit_bonuses": "First Deposit Bonuses",
            # System Analytics
            "system_analytics_title": "System Analytics",
            "total_users": "Total Users",
            "active_users": "Active Users",
            "new_users_today": "New Users Today",
            "service_usage": "Service Usage",
            "hosting_accounts": "Hosting Accounts",
            "registered_domains": "Registered Domains",
            "active_subscriptions": "Active Subscriptions",
            "api_status": "API Status",
            "performance_metrics": "Performance Metrics",
            "avg_response_time": "Average Response Time",
            "system_uptime": "System Uptime",
            # Bonus System
            "first_deposit_bonus": "First Deposit Bonus",
            "bonus_applied": "Bonus Applied",
            "referral_bonus": "Referral Bonus",
            "loyalty_bonus": "Loyalty Bonus",
            "bonus_amount": "Bonus Amount",
            "referral_code": "Referral Code",
            "generate_referral_code": "Generate Referral Code",
            "bonus_history": "Bonus History",
            "referral_stats": "Referral Statistics",
            "total_referrals": "Total Referrals",
            "referral_earnings": "Referral Earnings",
            "minimum_deposit_bonus": "Minimum ${amount} deposit required for bonus",
            "bonus_rate_info": "{rate}% bonus on deposits ${amount}+",
            "referral_bonus_info": "${amount} bonus for you and your friend",
            # Error Messages
            "error_occurred": "An error occurred. Please try again.",
            "cancel": "Cancel",
            # Messages
            "unknown_message": "Please use the menu buttons or /start command.",
            "error_occurred": "An error occurred. Please try again.",
            "processing": "Processing your request...",
        }
    }
