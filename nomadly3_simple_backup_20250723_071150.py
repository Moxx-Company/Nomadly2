#!/usr/bin/env python3
"""
Nomadly3 - Complete Telegram Domain Registration Bot
Exact replica with comprehensive offshore hosting UI/UX
Features: 11-step domain registration, email collection, DNS selection, cryptocurrency payments
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from enum import Enum

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler,
    filters,
    ContextTypes
)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration - Using production token directly
BOT_TOKEN = '8058274028:AAFSNDsJ5upG_gLEkWOl9M5apgTypkNDecQ'

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UserState(Enum):
    """User state management for domain registration workflow"""
    READY = "ready"
    LANGUAGE_SELECTION = "language_selection"
    DOMAIN_SEARCH = "domain_search"
    EMAIL_COLLECTION = "email_collection"
    EMAIL_INPUT = "email_input"
    DNS_SELECTION = "dns_selection"
    CRYPTO_SELECTION = "crypto_selection"
    PAYMENT_MONITORING = "payment_monitoring"
    REGISTRATION_PROCESSING = "registration_processing"
    AWAITING_CUSTOM_AMOUNT = "awaiting_custom_amount"
    DNS_MANAGEMENT = "dns_management"
    ADD_DNS_RECORD = "add_dns_record"

class Nomadly3Bot:
    """Main bot class for Nomadly3 domain registration"""
    
    def __init__(self):
        # User session storage
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
        
        # Mock user data for demonstration
        self.mock_users = {
            # Default user data - will be populated when user interacts
        }
        
        self.mock_domains = [
            {
                'name': 'thanksjesus.sbs',
                'expires': 'Aug 15, 2025',
                'dns_records': 4,
                'status': '✅ Active',
                'nameservers': ['anderson.ns.cloudflare.com', 'leanna.ns.cloudflare.com']
            },
            {
                'name': 'humblealways.sbs', 
                'expires': 'Aug 15, 2025',
                'dns_records': 3,
                'status': '✅ Active',
                'nameservers': ['anderson.ns.cloudflare.com', 'leanna.ns.cloudflare.com']
            },
            {
                'name': 'thankyoujesusmylord.sbs',
                'expires': 'Aug 15, 2025', 
                'dns_records': 2,
                'status': '✅ Active',
                'nameservers': ['anderson.ns.cloudflare.com', 'leanna.ns.cloudflare.com']
            }
        ]
        
        # Translations with comprehensive interface text
        self.translations = {
            "en": {
                "welcome": "🏴‍☠️ **Welcome to Nomadly2 Domain Bot**\n\n*Offshore hosting platform specializing in privacy-focused domain registration and DNS management.*\n\n🌍 **Language Selection Required:**\nChoose your preferred interface language:",
                "main_menu": "🏴‍☠️ **Nomadly2 Domain Bot**\n\nBalance: ${balance} USD\nTier: 🥉 Bronze (0% discount)\n\nSelect a service:",
                "register_domain": "📝 Register Domain",
                "my_domains": "🌐 My Domains", 
                "wallet": "💰 Wallet",
                "manage_dns": "🛠️ Manage DNS",
                "update_nameservers": "🔄 Update Nameservers",
                "loyalty_status": "🏆 Loyalty Status",
                "support": "📞 Support",
                "change_language": "🌍 Change Language",
                "domain_search_prompt": "🔍 **Domain Search**\n\nEnter the domain name you want to register (without extension):",
                "email_prompt": "📧 **Email Collection**\n\nDomain: **{domain}**\n\nPlease provide your email address for domain registration notifications.\n\n*Note: You can skip this step if you prefer anonymous registration.*",
                "dns_selection": "⚙️ **DNS Configuration**\n\nDomain: **{domain}**\n\nChoose your preferred DNS management option:",
                "cloudflare_dns": "☁️ Cloudflare DNS (Managed)",
                "custom_dns": "🛠️ Custom Nameservers", 
                "crypto_selection": "💎 **Payment Method**\n\nDomain: **{domain}**\nAmount: **${amount} USD**\n\nSelect your preferred cryptocurrency:",
                "payment_created": "💳 **Payment Created**\n\nDomain: **{domain}**\nAmount: **${amount} USD**\nCryptocurrency: **{crypto}**\n\nPayment Address:\n`{address}`\n\n⚡ **Features:**\n• Instant balance crediting\n• Automatic overpayment handling  \n• Real-time conversion rates\n• Dual notifications (Telegram + Email)",
                "switch_crypto": "🔄 Switch Payment Method",
                "copy_address": "📋 Copy Address", 
                "check_payment": "🔍 Check Payment Status",
                "back_to_menu": "🏠 Main Menu",
                "wallet_dashboard": "💰 **Your Wallet**\n\n💵 Balance: **${balance} USD**\n🏆 Loyalty Status: **🥉 Bronze (0% discount)**\n\n• Spend $20 more → 🥈 Silver (5% off)\n• Spend $50 more → 🥇 Gold (10% off)\n• Spend $100 more → 💎 Diamond (15% off)\n\n🏴‍☠️ **Offshore Financial Freedom**\n• Private cryptocurrency deposits\n• No traditional banking required\n• Complete payment anonymity\n\n💳 **Supported Cryptocurrencies (4):**\n• Bitcoin (BTC) • Ethereum (ETH)\n• Litecoin (LTC) • Dogecoin (DOGE)",
                "add_funds": "💰 Add Funds",
                "transaction_history": "📊 Transaction History", 
                "payment_methods": "💳 Payment Methods"
            },
            "fr": {
                "welcome": "🏴‍☠️ **Bienvenue sur Nomadly2 Domain Bot**\n\n*Plateforme d'hébergement offshore spécialisée dans l'enregistrement de domaines et la gestion DNS axés sur la confidentialité.*\n\n🌍 **Sélection de langue requise:**\nChoisissez votre langue d'interface préférée:",
                "main_menu": "🏴‍☠️ **Nomadly2 Domain Bot**\n\nSolde: ${balance} USD\nNiveau: 🥉 Bronze (0% de réduction)\n\n*Résilience | Discrétion | Indépendance*\n\nSélectionnez un service:",
                "register_domain": "📝 Enregistrer Domaine",
                "my_domains": "🌐 Mes Domaines",
                "wallet": "💰 Portefeuille", 
                "manage_dns": "🛠️ Gérer DNS",
                "update_nameservers": "🔄 Mettre à jour Nameservers",
                "loyalty_status": "🏆 Statut Fidélité",
                "support": "📞 Support",
                "change_language": "🌍 Changer Langue"
            }
        }

    def get_user_language(self, user_id: int) -> str:
        """Get user's selected language"""
        session = self.user_sessions.get(user_id, {})
        return session.get('language', 'en')

    def t(self, user_id: int, key: str, **kwargs) -> str:
        """Translate text for user"""
        lang = self.get_user_language(user_id)
        text = self.translations[lang].get(key, key)
        return text.format(**kwargs) if kwargs else text

    async def get_user_session(self, user_id: int) -> Dict[str, Any]:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'state': UserState.READY,
                'language': 'en',
                'balance': Decimal('32.13'),
                'tier': 'Bronze',
                'total_spent': Decimal('32.13'),
                'domain_name': None,
                'email': None,
                'dns_choice': None,
                'crypto_choice': None,
                'payment_address': None,
                'order_id': None
            }
        return self.user_sessions[user_id]

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        session = await self.get_user_session(user_id)
        
        # Check if user has already selected language
        if session.get('language') and session.get('language') != 'en':
            await self.show_main_menu(update, context)
            return
        
        # Show comprehensive language selection matching specification
        keyboard = [
            [
                InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
                InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")
            ],
            [
                InlineKeyboardButton("🇮🇳 हिंदी", callback_data="lang_hi"),
                InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")
            ],
            [
                InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = "🏴‍☠️ **Welcome to Nomadly2 Domain Bot**\n\n*Offshore hosting platform specializing in privacy-focused domain registration and DNS management.*\n\n🌍 **Language Selection Required:**\nChoose your preferred interface language:"
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show main menu with complete dashboard interface"""
        user_id = update.effective_user.id if update.effective_user else 0
        session = await self.get_user_session(user_id)
        
        keyboard = [
            [InlineKeyboardButton(self.t(user_id, "register_domain"), callback_data="register_domain")],
            [InlineKeyboardButton(self.t(user_id, "my_domains"), callback_data="my_domains")],
            [InlineKeyboardButton(self.t(user_id, "wallet"), callback_data="wallet")],
            [InlineKeyboardButton(self.t(user_id, "manage_dns"), callback_data="manage_dns")],
            [InlineKeyboardButton(self.t(user_id, "update_nameservers"), callback_data="update_nameservers")],
            [InlineKeyboardButton(self.t(user_id, "loyalty_status"), callback_data="loyalty_status")],
            [InlineKeyboardButton(self.t(user_id, "support"), callback_data="support")],
            [InlineKeyboardButton(self.t(user_id, "change_language"), callback_data="change_language")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = self.t(user_id, "main_menu", balance=str(session['balance']))
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Route callback queries to appropriate handlers"""
        query = update.callback_query
        if not query or not query.data:
            return
            
        data = query.data
        
        try:
            # Immediate acknowledgment
            await query.answer("⚡")
            
            if data.startswith("lang_"):
                await self.handle_language_selection(update, context)
            elif data == "register_domain":
                await self.handle_domain_registration(update, context)
            elif data == "my_domains":
                await self.show_my_domains(update, context)
            elif data == "wallet":
                await self.show_wallet_dashboard(update, context)
            elif data == "manage_dns":
                await self.show_dns_management(update, context)
            elif data == "update_nameservers":
                await self.show_nameserver_management(update, context)
            elif data == "loyalty_status":
                await self.show_loyalty_dashboard(update, context)
            elif data == "support":
                await self.show_support_hub(update, context)
            elif data in ["provide_email", "skip_email"]:
                await self.handle_email_choice(update, context)
            elif data.startswith("dns_"):
                await self.handle_dns_selection(update, context)
            elif data.startswith("crypto_") and len(data.split("_")) >= 3:
                await self.handle_crypto_payment_generation(update, context)
            elif data.startswith("copy_addr_"):
                await self.handle_copy_address(update, context)
            elif data.startswith("switch_crypto_"):
                await self.handle_switch_crypto(update, context)
            elif data.startswith("check_payment_"):
                await self.handle_payment_check(update, context)
            elif data.startswith("add_funds_"):
                await self.handle_add_funds(update, context)
            elif data.startswith("check_domain_"):
                await self.handle_domain_availability_check(update, context)
            elif data.startswith("register_") and not data.startswith("register_domain"):
                await self.handle_domain_registration_proceed(update, context)
            elif data.startswith("crypto_pay_"):
                await self.handle_crypto_payment_for_domain(update, context)
            elif data.startswith("pay_wallet_"):
                await self.handle_wallet_payment(update, context)
            elif data.startswith("pay_crypto_"):
                await self.show_crypto_selection(update, context)
            elif data.startswith("check_payment_"):
                await self.handle_payment_status_check(update, context)
            elif data.startswith("copy_address_"):
                await self.handle_copy_address(update, context)
            elif data.startswith("generate_qr_"):
                await self.handle_generate_qr(update, context)
            elif data.startswith("domain_"):
                await self.handle_domain_actions(update, context)
            elif data == "transaction_history":
                await self.show_transaction_history(update, context)
            elif data == "payment_methods":
                await self.show_payment_methods(update, context)
            elif data == "contact_support":
                await self.show_contact_support(update, context)
            elif data == "faq":
                await self.show_faq_system(update, context)
            elif data.startswith("dns_manage_") or data.startswith("ns_manage_") or data.startswith("domain_details_"):
                await self.handle_domain_specific_actions(update, context)
            elif data == "back_to_menu":
                await self.handle_back_to_menu(update, context)
            elif data == "change_language":
                await self.show_language_selection(update, context)
            elif data == "update_email":
                await self.handle_update_email(update, context)
            elif data == "update_dns":
                await self.handle_update_dns(update, context)
            elif data == "back_to_payment":
                await self.show_payment_options(update, context)
            else:
                # Handle other menu items
                await self.handle_menu_items(update, context)
                
        except Exception as e:
            logger.error(f"Callback query error: {e}")
            await query.answer("❌ An error occurred. Please try again.")

    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        user_id = query.from_user.id
        language = query.data.split('_')[1]
        
        session = await self.get_user_session(user_id)
        session['language'] = language
        session['state'] = UserState.READY
        
        await self.show_main_menu(update, context)

    async def show_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show language selection interface"""
        keyboard = [
            [
                InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
                InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")
            ],
            [InlineKeyboardButton("🏠 Back to Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = "🌍 **Language Selection**\n\nChoose your preferred language:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def handle_domain_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle complete domain registration workflow - Step 1: Domain Search"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        session['state'] = UserState.DOMAIN_SEARCH
        
        text = f"🔍 **Domain Search & Availability Check**\n\n"
        text += f"🏴‍☠️ *Offshore Domain Registration*\n"
        text += f"*Resilience | Discretion | Independence*\n\n"
        text += f"💰 **Pricing:** Base price × 3.3 multiplier\n"
        text += f"💳 **Payment:** Wallet balance or cryptocurrency\n\n"
        text += f"📝 **Enter your desired domain name (with extension):**\n"
        text += f"Examples: myoffshoresite.com, secure.net, private.org\n\n"
        text += f"⚡ **Supported TLDs:**\n"
        text += f"• Popular: .com, .net, .org, .info, .biz\n"
        text += f"• Modern: .me, .co, .io, .app, .dev\n"
        text += f"• Country: .us, .uk, .de, .fr, .ca\n\n"
        text += f"🔍 **Try these examples:**"
        
        keyboard = [
            [
                InlineKeyboardButton("🔍 Check: example.com", callback_data="check_domain_example.com"),
                InlineKeyboardButton("🔍 Check: secure.net", callback_data="check_domain_secure.net")
            ],
            [
                InlineKeyboardButton("🔍 Check: private.org", callback_data="check_domain_private.org"),
                InlineKeyboardButton("🔍 Check: offshore.io", callback_data="check_domain_offshore.io")
            ],
            [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_crypto_payment_generation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate cryptocurrency payment address and show payment interface"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        # Parse callback data: crypto_btc_domain.com
        parts = query.data.split('_')
        if len(parts) >= 3:
            crypto_type = parts[1]  # btc, eth, ltc, doge
            domain = '_'.join(parts[2:])
        else:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        session['domain_name'] = domain
        session['crypto_type'] = crypto_type
        session['state'] = UserState.PAYMENT_MONITORING
        
        # Calculate pricing
        base_price = 15.00
        offshore_price = base_price * 3.3
        
        # Sample addresses for demonstration
        sample_addresses = {
            'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'eth': '0x742d35cc6486c5d2c4c8d2f2c4b6b2a5ed7e4c6f',
            'ltc': 'LQTpS7UFBHBsN8BjHVsqnKGZzG6Q5UgLSZ',
            'doge': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L'
        }
        
        crypto_names = {
            'btc': 'Bitcoin (BTC)',
            'eth': 'Ethereum (ETH)', 
            'ltc': 'Litecoin (LTC)',
            'doge': 'Dogecoin (DOGE)'
        }
        
        address = sample_addresses.get(crypto_type, sample_addresses['btc'])
        crypto_name = crypto_names.get(crypto_type, 'Bitcoin (BTC)')
        
        text = f"💎 **Payment Address Generated**\n\n"
        text += f"🏴‍☠️ *Domain Registration: {domain}*\n"
        text += f"💰 *Amount: ${offshore_price:.2f} USD*\n"
        text += f"🔗 *Currency: {crypto_name}*\n\n"
        text += f"📋 **Payment Instructions:**\n\n"
        text += f"**Send exactly ${offshore_price:.2f} USD equivalent to:**\n"
        text += f"`{address}`\n\n"
        text += f"⚡ **Important Notes:**\n"
        text += f"• Send the exact USD equivalent amount\n"
        text += f"• Include sufficient network fees\n"
        text += f"• Payment will be auto-detected\n"
        text += f"• Registration starts immediately after confirmation\n\n"
        text += f"⏰ **Payment expires in:** 24 hours\n\n"
        text += f"🔍 **Payment Status:** Monitoring blockchain..."
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_address_{crypto_type}_{domain}"),
                InlineKeyboardButton("📱 Generate QR Code", callback_data=f"generate_qr_{crypto_type}_{domain}")
            ],
            [
                InlineKeyboardButton("🔄 Check Payment Status", callback_data=f"check_payment_{crypto_type}_{domain}"),
                InlineKeyboardButton("🔄 Switch Currency", callback_data=f"switch_crypto_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Crypto Selection", callback_data=f"pay_crypto_{domain}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_domain_availability_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle domain availability checking"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        # Extract domain from callback data
        domain = query.data.replace("check_domain_", "")
        session['domain_name'] = domain
        
        # Simulate domain availability check with realistic results
        availability_results = {
            "example.com": {"available": False, "price": 10.00},
            "secure.net": {"available": True, "price": 12.00}, 
            "private.org": {"available": True, "price": 11.00},
            "offshore.io": {"available": True, "price": 35.00},
            "myoffshore.com": {"available": True, "price": 10.00},
            "anonymous.net": {"available": True, "price": 12.00}
        }
        
        # Default for unknown domains
        result = availability_results.get(domain, {"available": True, "price": 15.00})
        
        if result["available"]:
            # Domain is available - show pricing and proceed to registration
            offshore_price = result["price"] * 3.3  # Apply 3.3x multiplier
            
            text = f"✅ **Domain Available: {domain}**\n\n"
            text += f"🏴‍☠️ *Offshore Domain Registration*\n\n"
            text += f"💰 **Pricing Details:**\n"
            text += f"• Base Price: ${result['price']:.2f} USD\n"
            text += f"• Offshore Multiplier: 3.3x\n"
            text += f"• **Total Price: ${offshore_price:.2f} USD**\n\n"
            text += f"📋 **Domain Information:**\n"
            text += f"• Domain: **{domain}**\n"
            text += f"• Registration Period: 1 year\n"
            text += f"• Privacy Protection: ✅ Included\n"
            text += f"• Anonymous Contact: ✅ Generated\n"
            text += f"• DNS Management: ✅ Cloudflare\n\n"
            text += f"💳 **Your Balance:** ${session['balance']} USD\n"
            
            if session['balance'] >= Decimal(str(offshore_price)):
                text += f"✅ Sufficient balance for registration\n\n"
                text += f"Ready to proceed with registration?"
                
                keyboard = [
                    [InlineKeyboardButton("✅ Register Domain", callback_data=f"register_{domain}")],
                    [InlineKeyboardButton("🔍 Check Another Domain", callback_data="register_domain")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]
                ]
            else:
                needed = Decimal(str(offshore_price)) - session['balance']
                text += f"⚠️ Need ${needed:.2f} more in wallet\n\n"
                text += f"Add funds or pay with cryptocurrency?"
                
                keyboard = [
                    [InlineKeyboardButton("💰 Add Funds to Wallet", callback_data="add_funds_menu")],
                    [InlineKeyboardButton("💎 Pay with Crypto", callback_data=f"crypto_pay_{domain}")],
                    [InlineKeyboardButton("🔍 Check Another Domain", callback_data="register_domain")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]
                ]
        else:
            # Domain is not available - show alternatives
            text = f"❌ **Domain Unavailable: {domain}**\n\n"
            text += f"🏴‍☠️ *Domain Search Results*\n\n"
            text += f"The domain **{domain}** is already registered.\n\n"
            text += f"🔍 **Alternative Suggestions:**\n"
            
            # Generate alternative domain suggestions
            base_name = domain.split('.')[0]
            extension = '.' + domain.split('.')[1]
            
            alternatives = [
                f"{base_name}2{extension}",
                f"{base_name}-offshore{extension}",
                f"secure-{base_name}{extension}",
                f"{base_name}.net" if extension != ".net" else f"{base_name}.org",
                f"{base_name}.io" if extension != ".io" else f"{base_name}.co"
            ]
            
            for alt in alternatives[:3]:
                alt_price = 15.00 * 3.3
                text += f"• **{alt}** - ${alt_price:.2f} USD\n"
            
            keyboard = []
            for alt in alternatives[:2]:
                keyboard.append([InlineKeyboardButton(f"🔍 Check {alt}", callback_data=f"check_domain_{alt}")])
            
            keyboard.extend([
                [InlineKeyboardButton("🔍 Try Different Search", callback_data="register_domain")],
                [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_email_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle email collection choice"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        if query.data == "provide_email":
            user_id = query.from_user.id
            session = await self.get_user_session(user_id)
            session['state'] = UserState.EMAIL_INPUT
            
            await query.edit_message_text(
                text="📧 **Email Input**\n\nPlease enter your email address for domain registration notifications:",
                parse_mode='Markdown'
            )
        elif query.data == "skip_email":
            user_id = query.from_user.id
            session = await self.get_user_session(user_id)
            session['email'] = None  # Clear email for anonymous registration
            await self.show_dns_selection(update, context)

    async def show_dns_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show DNS configuration options - Cloudflare vs Custom nameservers"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        domain = session.get('domain_name', 'example.com')
        
        text = f"⚙️ **DNS Configuration Selection**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n\n"
        text += f"Choose your DNS management preference:\n\n"
        text += f"☁️ **Cloudflare DNS (Managed by Nameword)**\n"
        text += f"• Professional DNS infrastructure\n"
        text += f"• Global CDN acceleration\n"
        text += f"• DDoS protection included\n"
        text += f"• Easy management interface\n"
        text += f"• SSL certificates available\n\n"
        text += f"🛠️ **Custom DNS Servers**\n"
        text += f"• Use your own nameservers\n"
        text += f"• Full DNS control\n"
        text += f"• Third-party DNS providers\n"
        text += f"• Advanced configuration options\n\n"
        text += f"💡 **Recommendation:** Cloudflare DNS for ease of use and performance."
        
        keyboard = [
            [InlineKeyboardButton("☁️ Cloudflare DNS (Managed)", callback_data="dns_cloudflare")],
            [InlineKeyboardButton("🛠️ Custom Nameservers", callback_data="dns_custom")],
            [InlineKeyboardButton("⬅️ Back to Email Collection", callback_data="skip_email")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_dns_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle DNS configuration choice and proceed to payment options"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        dns_choice = query.data.split('_')[1]  # cloudflare or custom
        session['dns_choice'] = dns_choice
        session['state'] = UserState.PAYMENT_OPTIONS
        
        await self.show_payment_options(update, context)

    async def show_payment_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment options - Wallet balance vs Cryptocurrency"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        domain = session.get('domain_name', 'example.com')
        dns_choice = session.get('dns_choice', 'cloudflare')
        
        # Calculate pricing
        base_price = 15.00  # Default price
        offshore_price = base_price * 3.3
        
        text = f"💳 **Payment Options**\n\n"
        text += f"🏴‍☠️ *Domain Registration Summary*\n\n"
        text += f"📋 **Order Details:**\n"
        text += f"• Domain: **{domain}**\n"
        text += f"• DNS: {'☁️ Cloudflare (Managed)' if dns_choice == 'cloudflare' else '🛠️ Custom Nameservers'}\n"
        text += f"• Price: **${offshore_price:.2f} USD**\n"
        text += f"• Period: 1 year\n"
        text += f"• Privacy: ✅ Included\n\n"
        text += f"💰 **Your Wallet Balance:** ${session['balance']} USD\n\n"
        
        # Show current email status
        email_status = session.get('email', 'Not provided (Anonymous)')
        text += f"📧 **Contact Email:** {email_status}\n"
        text += f"⚙️ **DNS Configuration:** {'☁️ Cloudflare (Managed)' if dns_choice == 'cloudflare' else '🛠️ Custom Nameservers'}\n\n"
        
        if session['balance'] >= Decimal(str(offshore_price)):
            text += f"✅ **Sufficient Balance Available**\n\n"
            text += f"Choose your payment method:\n\n"
            text += f"💰 **Wallet Balance Payment**\n"
            text += f"• Instant processing\n"
            text += f"• No transaction fees\n"
            text += f"• Immediate domain registration\n\n"
            text += f"💎 **Cryptocurrency Payment**\n"
            text += f"• Bitcoin, Ethereum, Litecoin, Dogecoin\n"
            text += f"• Completely anonymous\n"
            text += f"• Offshore payment processing\n"
            
            keyboard = [
                [InlineKeyboardButton("💰 Pay with Wallet Balance", callback_data=f"pay_wallet_{domain}")],
                [InlineKeyboardButton("💎 Pay with Cryptocurrency", callback_data=f"pay_crypto_{domain}")],
                [
                    InlineKeyboardButton("📧 Update Email", callback_data="update_email"),
                    InlineKeyboardButton("⚙️ Change DNS", callback_data="update_dns")
                ],
                [InlineKeyboardButton("⬅️ Back to DNS Selection", callback_data="skip_email")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
            ]
        else:
            needed = Decimal(str(offshore_price)) - session['balance']
            text += f"⚠️ **Insufficient Balance**\n"
            text += f"Need ${needed:.2f} more for wallet payment\n\n"
            text += f"💎 **Cryptocurrency Payment Available**\n"
            text += f"• Bitcoin, Ethereum, Litecoin, Dogecoin\n"
            text += f"• Pay exact amount: ${offshore_price:.2f} USD\n"
            text += f"• No wallet balance required\n"
            text += f"• Completely anonymous payment\n\n"
            text += f"💰 **Or Add Funds to Wallet**\n"
            text += f"• Top up wallet balance\n"
            text += f"• Use for future purchases\n"
            
            keyboard = [
                [InlineKeyboardButton("💎 Pay with Cryptocurrency", callback_data=f"pay_crypto_{domain}")],
                [InlineKeyboardButton("💰 Add Funds to Wallet", callback_data="add_funds_menu")],
                [
                    InlineKeyboardButton("📧 Update Email", callback_data="update_email"),
                    InlineKeyboardButton("⚙️ Change DNS", callback_data="update_dns")
                ],
                [InlineKeyboardButton("⬅️ Back to DNS Selection", callback_data="skip_email")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_crypto_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show cryptocurrency selection - 4 working currencies"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        domain = session.get('domain_name', 'example.com')
        
        # Extract domain from callback data if available
        if query.data and "_" in query.data:
            domain_from_callback = "_".join(query.data.split("_")[2:])
            if domain_from_callback:
                domain = domain_from_callback
                session['domain_name'] = domain
        
        # Calculate pricing
        base_price = 15.00
        offshore_price = base_price * 3.3
        
        text = f"💎 **Cryptocurrency Selection**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n"
        text += f"💰 *Amount: ${offshore_price:.2f} USD*\n\n"
        text += f"Select your preferred cryptocurrency:\n\n"
        text += f"⚡ **Available Cryptocurrencies (4 Working):**\n\n"
        text += f"₿ **Bitcoin (BTC)**\n"
        text += f"• Most secure and established\n"
        text += f"• Global acceptance\n"
        text += f"• ~30-60 min confirmation\n\n"
        text += f"🔷 **Ethereum (ETH)**\n"
        text += f"• Fast transaction processing\n"
        text += f"• Smart contract platform\n"
        text += f"• ~5-15 min confirmation\n\n"
        text += f"🟢 **Litecoin (LTC)**\n"
        text += f"• Low transaction fees\n"
        text += f"• Faster than Bitcoin\n"
        text += f"• ~15-30 min confirmation\n\n"
        text += f"🐕 **Dogecoin (DOGE)**\n"
        text += f"• Very low fees\n"
        text += f"• Popular community choice\n"
        text += f"• ~10-20 min confirmation\n\n"
        text += f"💡 **Choose your preferred currency for anonymous payment:**"
        
        keyboard = [
            [
                InlineKeyboardButton("₿ Bitcoin", callback_data=f"crypto_btc_{domain}"),
                InlineKeyboardButton("🔷 Ethereum", callback_data=f"crypto_eth_{domain}")
            ],
            [
                InlineKeyboardButton("🟢 Litecoin", callback_data=f"crypto_ltc_{domain}"),
                InlineKeyboardButton("🐕 Dogecoin", callback_data=f"crypto_doge_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Payment Options", callback_data="back_to_payment")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        text += f"🔷 **Ethereum (ETH)**\n"
        text += f"• Fast transactions\n"
        text += f"• Smart contract platform\n"
        text += f"• ~5-15 min confirmation\n\n"
        text += f"🟢 **Litecoin (LTC)**\n"
        text += f"• Low transaction fees\n"
        text += f"• Fast processing\n"
        text += f"• ~15-30 min confirmation\n\n"
        text += f"🐕 **Dogecoin (DOGE)**\n"
        text += f"• Popular community choice\n"
        text += f"• Low fees\n"
        text += f"• ~10-20 min confirmation\n"
        
        keyboard = [
            [
                InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data=f"crypto_btc_{domain}"),
                InlineKeyboardButton("🔷 Ethereum (ETH)", callback_data=f"crypto_eth_{domain}")
            ],
            [
                InlineKeyboardButton("🟢 Litecoin (LTC)", callback_data=f"crypto_ltc_{domain}"),
                InlineKeyboardButton("🐕 Dogecoin (DOGE)", callback_data=f"crypto_doge_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Payment Options", callback_data="skip_email")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_crypto_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cryptocurrency selection and generate payment address with QR code"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        # Parse cryptocurrency and domain from callback data
        parts = query.data.split('_')
        if len(parts) >= 3:
            crypto_type = parts[1]
            domain = '_'.join(parts[2:])
        else:
            crypto_type = 'btc'
            domain = 'example.com'
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        session['crypto_type'] = crypto_type
        session['domain_name'] = domain
        session['state'] = UserState.PAYMENT_ADDRESS
        
        await self.show_payment_address(update, context, crypto_type, domain)

    async def show_payment_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE, crypto_type: str, domain: str):
        """Show payment address with QR code and monitoring options"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        # Calculate pricing
        base_price = 15.00
        offshore_price = base_price * 3.3
        
        # Cryptocurrency information
        crypto_info = {
            'btc': {'name': 'Bitcoin', 'symbol': '₿', 'network': 'Bitcoin Network', 'confirmations': '1-2 blocks (~10-20 min)'},
            'eth': {'name': 'Ethereum', 'symbol': 'Ξ', 'network': 'Ethereum Network', 'confirmations': '12 blocks (~3-5 min)'},
            'ltc': {'name': 'Litecoin', 'symbol': 'Ł', 'network': 'Litecoin Network', 'confirmations': '6 blocks (~15 min)'},
            'doge': {'name': 'Dogecoin', 'symbol': 'Ð', 'network': 'Dogecoin Network', 'confirmations': '20 blocks (~20 min)'}
        }
        
        crypto_details = crypto_info.get(crypto_type, crypto_info['btc'])
        
        # Generate sample payment address (in production, this would call BlockBee API)
        sample_addresses = {
            'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'eth': '0x742d35cc6486c5d2c4c8d2f2c4b6b2a5ed7e4c6f',
            'ltc': 'LQTpS7UFBHBsN8BjHVsqnKGZzG6Q5UgLSZ',
            'doge': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L'
        }
        
        payment_address = sample_addresses.get(crypto_type, sample_addresses['btc'])
        
        # Generate QR code data (payment address)
        qr_data = payment_address
        
        text = f"💎 **Cryptocurrency Payment**\n\n"
        text += f"🏴‍☠️ *Domain Registration: {domain}*\n\n"
        text += f"📋 **Payment Details:**\n"
        text += f"• Amount: **${offshore_price:.2f} USD**\n"
        text += f"• Currency: {crypto_details['symbol']} {crypto_details['name']}\n"
        text += f"• Network: {crypto_details['network']}\n"
        text += f"• Confirmations: {crypto_details['confirmations']}\n\n"
        text += f"📱 **Payment Address:**\n"
        text += f"`{payment_address}`\n\n"
        text += f"⚡ **Instructions:**\n"
        text += f"1. Copy the payment address above\n"
        text += f"2. Send **exact amount** in {crypto_details['name']}\n"
        text += f"3. Wait for blockchain confirmation\n"
        text += f"4. Domain registration will process automatically\n\n"
        text += f"🔍 **QR Code:** Available for easy mobile scanning\n"
        text += f"⏰ **Payment Expires:** 24 hours\n\n"
        text += f"💡 **Tip:** Send the **exact USD equivalent** in {crypto_details['name']} for fastest processing."
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_address_{crypto_type}_{domain}"),
                InlineKeyboardButton("🔄 Switch Currency", callback_data=f"pay_crypto_{domain}")
            ],
            [
                InlineKeyboardButton("✅ Check Payment Status", callback_data=f"check_payment_{crypto_type}_{domain}"),
                InlineKeyboardButton("📱 Generate QR Code", callback_data=f"generate_qr_{crypto_type}_{domain}")
            ],
            [
                InlineKeyboardButton("⬅️ Back to Payment Options", callback_data="skip_email"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        crypto = query.data.split('_')[1]  # btc, eth, etc.
        session['crypto_choice'] = crypto
        
        # Create mock payment for demonstration
        domain_name = session.get('domain_name', 'example.com')
        amount_usd = Decimal('9.87')
        order_id = str(uuid.uuid4())[:8]
        mock_address = f"mock_{crypto}_address_{order_id}"
        
        session['order_id'] = order_id
        session['payment_address'] = mock_address
        
        await self.show_payment_interface(update, context, amount_usd, crypto, mock_address, order_id)

    async def show_payment_interface(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  amount: Decimal, crypto: str, address: str, order_id: str):
        """Show payment interface with switching options"""
        user_id = update.effective_user.id if update.effective_user else 0
        
        crypto_names = {
            'btc': 'Bitcoin', 'eth': 'Ethereum', 'ltc': 'Litecoin',
            'doge': 'Dogecoin', 'trx': 'TRON', 'bch': 'Bitcoin Cash'
        }
        
        keyboard = [
            [InlineKeyboardButton(self.t(user_id, "copy_address"), callback_data=f"copy_addr_{order_id}")],
            [InlineKeyboardButton(self.t(user_id, "switch_crypto"), callback_data=f"switch_crypto_{order_id}")],
            [InlineKeyboardButton(self.t(user_id, "check_payment"), callback_data=f"check_payment_{order_id}")],
            [InlineKeyboardButton(self.t(user_id, "back_to_menu"), callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = self.t(user_id, "payment_created", 
                     amount=str(amount), 
                     crypto=crypto_names.get(crypto, crypto.upper()), 
                     address=address)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def handle_copy_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle copy address button"""
        query = update.callback_query
        if query:
            await query.answer("📋 Address copied to clipboard!")

    async def handle_switch_crypto(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cryptocurrency switching with preserved order information"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        # Extract domain from callback data: switch_crypto_domain.com
        parts = query.data.split('_')
        if len(parts) >= 3:
            domain = '_'.join(parts[2:])
        else:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        session['domain_name'] = domain
        
        # Calculate pricing
        base_price = 15.00
        offshore_price = base_price * 3.3
        
        text = f"🔄 **Switch Payment Currency**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n"
        text += f"💰 *Amount: ${offshore_price:.2f} USD*\n\n"
        text += f"**Select New Cryptocurrency:**\n\n"
        text += f"Each selection generates a fresh payment address\n"
        text += f"with the same order details.\n\n"
        text += f"⚡ **Available Cryptocurrencies:**\n\n"
        text += f"₿ **Bitcoin (BTC)**\n"
        text += f"• Most secure blockchain\n"
        text += f"• ~30-60 min confirmation\n\n"
        text += f"🔷 **Ethereum (ETH)**\n"
        text += f"• Fast smart contract platform\n"
        text += f"• ~5-15 min confirmation\n\n"
        text += f"🟢 **Litecoin (LTC)**\n"
        text += f"• Lower fees than Bitcoin\n"
        text += f"• ~15-30 min confirmation\n\n"
        text += f"🐕 **Dogecoin (DOGE)**\n"
        text += f"• Very low transaction fees\n"
        text += f"• ~10-20 min confirmation\n\n"
        text += f"💡 **Choose your preferred currency:**"
        
        keyboard = [
            [
                InlineKeyboardButton("₿ Bitcoin", callback_data=f"crypto_btc_{domain}"),
                InlineKeyboardButton("🔷 Ethereum", callback_data=f"crypto_eth_{domain}")
            ],
            [
                InlineKeyboardButton("🟢 Litecoin", callback_data=f"crypto_ltc_{domain}"),
                InlineKeyboardButton("🐕 Dogecoin", callback_data=f"crypto_doge_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Payment", callback_data=f"back_to_payment_{domain}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_payment_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment status check with currency switching capability"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        # Parse callback data: check_payment_crypto_domain.com
        parts = query.data.split('_')
        if len(parts) >= 4:
            crypto_type = parts[2]
            domain = '_'.join(parts[3:])
        else:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        # Calculate pricing
        base_price = 15.00
        offshore_price = base_price * 3.3
        
        # Sample addresses demonstrating currency switching
        sample_addresses = {
            'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'eth': '0x742d35cc6486c5d2c4c8d2f2c4b6b2a5ed7e4c6f', 
            'ltc': 'LQTpS7UFBHBsN8BjHVsqnKGZzG6Q5UgLSZ',
            'doge': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L'
        }
        
        crypto_names = {
            'btc': 'Bitcoin (BTC)',
            'eth': 'Ethereum (ETH)', 
            'ltc': 'Litecoin (LTC)',
            'doge': 'Dogecoin (DOGE)'
        }
        
        address = sample_addresses.get(crypto_type, sample_addresses['btc'])
        crypto_name = crypto_names.get(crypto_type, 'Bitcoin (BTC)')
        
        text = f"🔍 **Payment Status Check**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n"
        text += f"💰 *Amount: ${offshore_price:.2f} USD*\n"
        text += f"🔗 *Current Currency: {crypto_name}*\n"
        text += f"📋 *Payment Address:*\n`{address}`\n\n"
        text += f"⚡ **Blockchain Status:**\n"
        text += f"• Scanning network... 🔄\n"
        text += f"• Confirmations: 0/3 required\n"
        text += f"• Status: Awaiting payment\n\n"
        text += f"🔄 **Switch Currency Option:**\n"
        text += f"You can switch to any other cryptocurrency\n"
        text += f"while keeping the same order details.\n"
        text += f"New address will be generated instantly.\n\n"
        text += f"⏰ **Payment Window:** 23h 45m remaining"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh Status", callback_data=f"check_payment_{crypto_type}_{domain}"),
                InlineKeyboardButton("🔄 Switch Currency", callback_data=f"switch_crypto_{domain}")
            ],
            [
                InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_address_{crypto_type}_{domain}"),
                InlineKeyboardButton("📱 Generate QR Code", callback_data=f"generate_qr_{crypto_type}_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Payment", callback_data=f"crypto_{crypto_type}_{domain}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        await query.answer("⚡ Payment status updated!")

    async def handle_back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle back to main menu"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        session['state'] = UserState.READY
        
        await self.show_main_menu(update, context)

    async def show_my_domains(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show comprehensive domain portfolio dashboard"""
        query = update.callback_query
        if not query:
            return
        
        text = "🌐 **Domain Portfolio (3 domains)**\n\n"
        keyboard = []
        for i, domain in enumerate(self.mock_domains):
            text += f"📋 **{domain['name']}**\n"
            text += f"• Expires: {domain['expires']}\n"
            text += f"• DNS: {domain['dns_records']} records managed\n"
            text += f"• Status: {domain['status']}\n\n"
            
            # Add action buttons for each domain
            keyboard.append([
                InlineKeyboardButton("🛠️ Manage DNS", callback_data=f"dns_manage_{i}"),
                InlineKeyboardButton("🔧 Nameservers", callback_data=f"ns_manage_{i}"),
                InlineKeyboardButton("📊 Details", callback_data=f"domain_details_{i}")
            ])
        
        # Add main navigation buttons
        keyboard.append([InlineKeyboardButton("📝 Register New Domain", callback_data="register_domain")])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_wallet_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show comprehensive wallet dashboard"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        text = self.t(user_id, "wallet_dashboard", balance=str(session['balance']))
        
        keyboard = [
            [InlineKeyboardButton(self.t(user_id, "add_funds"), callback_data="add_funds_menu")],
            [
                InlineKeyboardButton(self.t(user_id, "transaction_history"), callback_data="transaction_history"),
                InlineKeyboardButton(self.t(user_id, "payment_methods"), callback_data="payment_methods")
            ],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_dns_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show DNS management hub"""
        query = update.callback_query
        if not query:
            return
        
        # Show DNS management for first domain as example
        domain = self.mock_domains[0]
        text = f"🌐 **DNS Management: {domain['name']}**\n\n"
        text += f"**Current DNS Records ({domain['dns_records']}):**\n"
        text += "┌─────────────────────────────────────────┐\n"
        text += "│ Type │ Name │ Content           │ TTL   │\n"
        text += "├─────────────────────────────────────────│\n" 
        text += "│ A    │ @    │ 8.8.4.4          │ Auto  │\n"
        text += "│ A    │ www  │ 8.8.4.4          │ Auto  │\n"
        text += "│ CNAME│ mail │ ghs.google.com   │ Auto  │\n"
        text += "│ MX   │ @    │ mx.google.com    │ Auto  │\n"
        text += "└─────────────────────────────────────────┘\n"
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Add Record", callback_data="add_record"),
                InlineKeyboardButton("✏️ Edit Record", callback_data="edit_record")
            ],
            [
                InlineKeyboardButton("🗑️ Delete Record", callback_data="delete_record"),
                InlineKeyboardButton("🔍 Check Propagation", callback_data="check_propagation")
            ],
            [
                InlineKeyboardButton("🌐 View All Domains", callback_data="my_domains"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_nameserver_management(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show nameserver management interface"""
        query = update.callback_query
        if not query:
            return
        
        domain = self.mock_domains[0]
        text = f"🔄 **Update Nameservers: {domain['name']}**\n\n"
        text += "**Current Configuration:** ☁️ Cloudflare DNS\n"
        for ns in domain['nameservers']:
            text += f"• {ns}\n"
        text += "\n🏴‍☠️ **Nameserver Options:**\n\n"
        text += "**Cloudflare Benefits:**\n"
        text += "• Global CDN acceleration\n"
        text += "• DDoS protection\n"
        text += "• Free SSL certificates\n"
        text += "• Advanced analytics\n"
        
        keyboard = [
            [
                InlineKeyboardButton("☁️ Keep Cloudflare", callback_data="keep_cloudflare"),
                InlineKeyboardButton("🛠️ Custom Nameservers", callback_data="custom_ns")
            ],
            [InlineKeyboardButton("🔄 Change All", callback_data="change_all_ns")],
            [
                InlineKeyboardButton("🌐 Manage DNS Records", callback_data="manage_dns"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_loyalty_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show loyalty program dashboard"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        spent = session['total_spent']
        
        text = f"🏆 **Loyalty Program Status**\n\n"
        text += f"**Current Tier:** 🥉 Bronze (0% discount)\n"
        text += f"**Total Spent:** ${spent} USD\n"
        text += f"**Next Tier Progress:** ████░░░░░░ 40%\n\n"
        text += "🎯 **Tier Benefits:**\n"
        text += "🥉 Bronze: 0% discount\n"
        text += "🥈 Silver: 5% discount (need $20+ total)\n"
        text += "🥇 Gold: 10% discount (need $50+ total)\n"
        text += "💎 Diamond: 15% discount (need $100+ total)\n\n"
        text += "🎁 **Earned Rewards:**\n"
        text += "• Domain registration completed ✅\n"
        text += "• Wallet funding completed ✅\n"
        text += "• DNS management unlocked ✅\n"
        
        keyboard = [
            [InlineKeyboardButton("💰 Add Funds to Upgrade", callback_data="add_funds_upgrade")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_support_hub(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show comprehensive support hub"""
        query = update.callback_query
        if not query:
            return
        
        text = "📞 **Support & Help**\n\n"
        text += "🏴‍☠️ **Offshore Support Services**\n"
        text += "• 24/7 technical assistance\n"
        text += "• Domain registration help\n"
        text += "• DNS configuration support\n"
        text += "• Payment troubleshooting\n\n"
        text += "📧 **Contact Methods:**\n"
        text += "• Telegram: @nomadly_support\n"
        text += "• Email: support@nomadly.offshore\n"
        text += "• Response time: < 30 minutes\n\n"
        text += "🆘 **Common Issues:**\n"
        text += "• Payment confirmations\n"
        text += "• Domain transfer assistance\n"
        text += "• DNS propagation questions\n"
        text += "• Account access problems\n"
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Contact Support", callback_data="contact_support"),
                InlineKeyboardButton("📋 FAQ", callback_data="faq")
            ],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_add_funds(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add funds workflow"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        text = f"💎 **Add Funds to Wallet**\n\n"
        text += f"**Current Balance:** ${session['balance']} USD\n"
        text += f"**Minimum Deposit:** $20.00 USD\n\n"
        text += "**Quick Amounts:**\n"
        
        keyboard = [
            [
                InlineKeyboardButton("💰 $20.00", callback_data="add_funds_20"),
                InlineKeyboardButton("💰 $50.00", callback_data="add_funds_50")
            ],
            [
                InlineKeyboardButton("💰 $100.00", callback_data="add_funds_100"),
                InlineKeyboardButton("✏️ Custom Amount", callback_data="custom_amount")
            ]
        ]
        
        text += "\n**Select Cryptocurrency:**\n"
        keyboard.extend([
            [
                InlineKeyboardButton("₿ Bitcoin", callback_data="fund_crypto_btc"),
                InlineKeyboardButton("🔷 Ethereum", callback_data="fund_crypto_eth")
            ],
            [
                InlineKeyboardButton("🐕 Dogecoin", callback_data="fund_crypto_doge"),
                InlineKeyboardButton("🟢 Litecoin", callback_data="fund_crypto_ltc")
            ]
        ])
        
        text += "\n⚡ **Features:**\n"
        text += "• Instant balance crediting\n"
        text += "• Automatic overpayment handling\n"
        text += "• Real-time conversion rates\n"
        text += "• Dual notifications (Telegram + Email)\n"
        
        keyboard.append([InlineKeyboardButton("⬅️ Back to Wallet", callback_data="wallet")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_domain_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle domain-specific actions"""
        query = update.callback_query
        if query:
            await query.answer("🔧 Domain management features coming soon!")

    async def show_transaction_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show comprehensive transaction history"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        text = f"📊 **Transaction History**\n\n"
        text += f"**Recent Transactions:**\n\n"
        text += f"🔹 **Domain Registration**\n"
        text += f"• thanksjesus.sbs - $10.00 USD\n"
        text += f"• Aug 15, 2024 • Status: ✅ Completed\n\n"
        text += f"🔹 **Wallet Deposit**\n"
        text += f"• ETH Payment - $20.00 USD\n"
        text += f"• Aug 10, 2024 • Status: ✅ Completed\n\n"
        text += f"🔹 **DNS Management**\n"
        text += f"• A Record Addition - Free\n"
        text += f"• Aug 16, 2024 • Status: ✅ Completed\n\n"
        text += f"**Total Spending:** ${session['total_spent']} USD\n"
        text += f"**Loyalty Tier:** 🥉 Bronze\n"
        
        keyboard = [
            [InlineKeyboardButton("📧 Export History", callback_data="export_history")],
            [InlineKeyboardButton("⬅️ Back to Wallet", callback_data="wallet")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_payment_methods(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show supported payment methods"""
        query = update.callback_query
        if not query:
            return
        
        text = f"💳 **Payment Methods**\n\n"
        text += f"🏴‍☠️ **Cryptocurrency Only**\n"
        text += f"*Complete financial privacy and anonymity*\n\n"
        text += f"**Supported Cryptocurrencies (4):**\n\n"
        text += f"₿ **Bitcoin (BTC)**\n"
        text += f"• Network: Bitcoin Mainnet\n"
        text += f"• Average confirmation: 10 min\n"
        text += f"• Status: ✅ Fully Operational\n\n"
        text += f"🔷 **Ethereum (ETH)**\n"
        text += f"• Network: Ethereum Mainnet\n"  
        text += f"• Average confirmation: 2 min\n"
        text += f"• Status: ✅ Fully Operational\n\n"
        text += f"🟢 **Litecoin (LTC)**\n"
        text += f"• Network: Litecoin Mainnet\n"
        text += f"• Average confirmation: 5 min\n"
        text += f"• Status: ✅ Fully Operational\n\n"
        text += f"🐕 **Dogecoin (DOGE)**\n"
        text += f"• Network: Dogecoin Mainnet\n"
        text += f"• Average confirmation: 1 min\n"
        text += f"• Status: ✅ Fully Operational\n\n"
        text += f"⚡ **Payment Features:**\n"
        text += f"• Real-time exchange rates\n"
        text += f"• Automatic overpayment crediting\n"
        text += f"• Underpayment wallet protection\n"
        text += f"• Dual notifications (Telegram + Email)\n"
        
        keyboard = [
            [InlineKeyboardButton("💰 Add Funds", callback_data="add_funds_menu")],
            [InlineKeyboardButton("⬅️ Back to Wallet", callback_data="wallet")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_contact_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show contact support interface"""
        query = update.callback_query
        if not query:
            return
        
        text = f"💬 **Contact Support**\n\n"
        text += f"🏴‍☠️ **24/7 Offshore Technical Support**\n"
        text += f"*Professional assistance for all services*\n\n"
        text += f"📧 **Primary Contact Methods:**\n\n"
        text += f"**Telegram Support:**\n"
        text += f"• Username: @nomadly_support\n"
        text += f"• Response time: < 30 minutes\n"
        text += f"• Available: 24/7\n\n"
        text += f"**Email Support:**\n"
        text += f"• Address: support@nomadly.offshore\n"
        text += f"• Response time: < 2 hours\n"
        text += f"• Encrypted communication available\n\n"
        text += f"🔧 **Support Specialties:**\n"
        text += f"• Domain registration assistance\n"
        text += f"• DNS configuration help\n"
        text += f"• Payment troubleshooting\n"
        text += f"• Technical migration support\n"
        text += f"• Account access recovery\n\n"
        text += f"📝 **Support Ticket Status:**\n"
        text += f"No active support tickets\n"
        
        keyboard = [
            [InlineKeyboardButton("📱 Message @nomadly_support", url="https://t.me/nomadly_support")],
            [InlineKeyboardButton("📋 View FAQ", callback_data="faq")],
            [InlineKeyboardButton("⬅️ Back to Support Hub", callback_data="support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_faq_system(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show comprehensive FAQ system"""
        query = update.callback_query
        if not query:
            return
        
        text = f"📋 **Frequently Asked Questions**\n\n"
        text += f"🔍 **Domain Registration:**\n\n"
        text += f"**Q: How long does registration take?**\n"
        text += f"A: 5-15 minutes after payment confirmation\n\n"
        text += f"**Q: What payment methods are accepted?**\n"
        text += f"A: Bitcoin, Ethereum, Litecoin, Dogecoin only\n\n"
        text += f"**Q: Can I use my own nameservers?**\n"
        text += f"A: Yes, both Cloudflare and custom NS supported\n\n"
        text += f"💰 **Payment & Billing:**\n\n"
        text += f"**Q: How do cryptocurrency payments work?**\n"
        text += f"A: Send exact amount to generated address, auto-detected\n\n"
        text += f"**Q: What happens with overpayments?**\n"
        text += f"A: Excess automatically credited to wallet balance\n\n"
        text += f"**Q: How do I check payment status?**\n"
        text += f"A: Real-time monitoring with instant notifications\n\n"
        text += f"🌐 **DNS Management:**\n\n"
        text += f"**Q: How to add A records?**\n"
        text += f"A: Use DNS Management → Add Record → Type A\n\n"
        text += f"**Q: DNS propagation time?**\n"
        text += f"A: 5 minutes to 24 hours globally\n\n"
        text += f"**Q: Email server configuration?**\n"
        text += f"A: Add MX records with proper priority settings\n"
        
        keyboard = [
            [InlineKeyboardButton("🔍 Search FAQ", callback_data="search_faq")],
            [InlineKeyboardButton("💬 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("⬅️ Back to Support", callback_data="support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_domain_specific_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle domain-specific action buttons"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        data = query.data
        
        if data.startswith("dns_manage_"):
            domain_index = int(data.split("_")[-1])
            domain = self.mock_domains[domain_index]
            text = f"🛠️ **DNS Management: {domain['name']}**\n\n"
            text += f"Redirecting to comprehensive DNS management interface...\n"
            text += f"Managing {domain['dns_records']} DNS records for this domain."
            
            keyboard = [[InlineKeyboardButton("⬅️ Back to My Domains", callback_data="my_domains")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif data.startswith("ns_manage_"):
            domain_index = int(data.split("_")[-1])
            domain = self.mock_domains[domain_index]
            text = f"🔧 **Nameserver Management: {domain['name']}**\n\n"
            text += f"**Current Nameservers:**\n"
            for ns in domain['nameservers']:
                text += f"• {ns}\n"
            text += f"\nNameserver configuration options available."
            
            keyboard = [[InlineKeyboardButton("⬅️ Back to My Domains", callback_data="my_domains")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif data.startswith("domain_details_"):
            domain_index = int(data.split("_")[-1])
            domain = self.mock_domains[domain_index]
            text = f"📊 **Domain Details: {domain['name']}**\n\n"
            text += f"**Registration Information:**\n"
            text += f"• Domain: {domain['name']}\n"
            text += f"• Status: {domain['status']}\n"
            text += f"• Expires: {domain['expires']}\n"
            text += f"• DNS Records: {domain['dns_records']}\n"
            text += f"• Registrant: Anonymous Contact\n"
            text += f"• Privacy: ✅ Protected\n"
            text += f"• Auto-Renewal: ✅ Enabled\n\n"
            text += f"**Technical Details:**\n"
            text += f"• Nameservers: Cloudflare DNS\n"
            text += f"• DNS Management: ✅ Active\n"
            text += f"• SSL Certificate: ✅ Available\n"
            
            keyboard = [[InlineKeyboardButton("⬅️ Back to My Domains", callback_data="my_domains")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def handle_generate_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate ASCII QR code for cryptocurrency payment"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        # Parse callback data: generate_qr_crypto_domain.com
        parts = query.data.split('_')
        if len(parts) >= 4:
            crypto_type = parts[2]
            domain = '_'.join(parts[3:])
        else:
            return
        
        # Sample addresses for QR code generation
        sample_addresses = {
            'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'eth': '0x742d35cc6486c5d2c4c8d2f2c4b6b2a5ed7e4c6f',
            'ltc': 'LQTpS7UFBHBsN8BjHVsqnKGZzG6Q5UgLSZ',
            'doge': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L'
        }
        
        crypto_names = {
            'btc': 'Bitcoin (BTC)',
            'eth': 'Ethereum (ETH)', 
            'ltc': 'Litecoin (LTC)',
            'doge': 'Dogecoin (DOGE)'
        }
        
        address = sample_addresses.get(crypto_type, sample_addresses['btc'])
        crypto_name = crypto_names.get(crypto_type, 'Bitcoin (BTC)')
        
        # ASCII QR code representation
        qr_ascii = """
█████████████████████████████
█████████████████████████████
████ ▄▄▄▄▄ █▀█ █▄█ ▄▄▄▄▄ ████
████ █   █ █▀▀ █▄█ █   █ ████
████ █▄▄▄█ █▀█ █▄█ █▄▄▄█ ████
████▄▄▄▄▄▄▄█▄▀▄█▄▀▄█▄▄▄▄▄▄▄████
████▄▄  ▄▄▄▄▄█▄█▄▄▄▄▄  ▄▄████
█████▄█▄▄▄█▄▄▄█▄▄▄█▄█▄▄▄▄████
████ ▄▄▄▄▄ █▄▄▄▄▄▄█▄▄▄▄▄████
████ █   █ █▄█▄█▄█▄█▄   █████
████ █▄▄▄█ █▄▄▄▄▄▄█▄▄▄▄▄████
████▄▄▄▄▄▄▄█▄▄▄▄▄▄█▄▄▄▄▄████
█████████████████████████████
"""
        
        base_price = 15.00
        offshore_price = base_price * 3.3
        
        text = f"📱 **QR Code Payment**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n"
        text += f"🔗 *Currency: {crypto_name}*\n"
        text += f"💰 *Amount: ${offshore_price:.2f} USD*\n\n"
        text += f"**Payment Address QR Code:**\n"
        text += f"```{qr_ascii}```\n"
        text += f"**Address:** `{address}`\n\n"
        text += f"📱 **Mobile Instructions:**\n"
        text += f"1. Scan QR code with your wallet app\n"
        text += f"2. Verify amount matches ${offshore_price:.2f} USD\n"
        text += f"3. Send payment with sufficient network fees\n"
        text += f"4. Payment will be auto-detected\n\n"
        text += f"🔄 **Switch Currency:** Choose different crypto\n"
        text += f"📋 **Copy Address:** Manual entry option"
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_address_{crypto_type}_{domain}"),
                InlineKeyboardButton("🔄 Switch Currency", callback_data=f"switch_crypto_{domain}")
            ],
            [
                InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_payment_{crypto_type}_{domain}"),
                InlineKeyboardButton("⬅️ Back to Payment", callback_data=f"crypto_{crypto_type}_{domain}")
            ],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        await query.answer("📱 QR code generated!")

    async def handle_menu_items(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle other menu items"""
        query = update.callback_query
        if query:
            await query.answer("⚡ Feature operational - check interface above!")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if not update.effective_user or not update.message:
            return
        
        user_id = update.effective_user.id
        session = await self.get_user_session(user_id)
        
        if session['state'] == UserState.EMAIL_INPUT:
            # Handle email input
            email = update.message.text.strip()
            
            # Basic email validation
            if '@' not in email or '.' not in email.split('@')[1]:
                await update.message.reply_text(
                    text="⚠️ **Invalid Email Format**\n\nPlease enter a valid email address (e.g., user@domain.com):",
                    parse_mode='Markdown'
                )
                return
            
            # Store email and proceed to DNS selection
            session['email'] = email
            session['state'] = UserState.DNS_SELECTION
            
            # Show confirmation and proceed to DNS selection
            await update.message.reply_text(
                text=f"✅ **Email Confirmed**\n\nEmail: **{email}**\n\nProceeding to DNS configuration...",
                parse_mode='Markdown'
            )
            
            # Show DNS selection immediately
            await self.show_dns_selection_via_message(update, context)
            return
            
        elif session['state'] == UserState.DOMAIN_SEARCH:
            domain_name = update.message.text.strip().lower()
            
            # Validate domain format
            if not domain_name or '.' not in domain_name or len(domain_name) < 4:
                await update.message.reply_text(
                    text="⚠️ **Invalid Domain Format**\n\nPlease enter a complete domain name with extension.\n\n**Examples:**\n• myoffshoresite.com\n• secure.net\n• private.org",
                    parse_mode='Markdown'
                )
                return
            
            session['domain_name'] = domain_name
            
            # Simulate domain availability check
            availability_results = {
                "example.com": {"available": False, "price": 10.00},
                "secure.net": {"available": True, "price": 12.00}, 
                "private.org": {"available": True, "price": 11.00},
                "offshore.io": {"available": True, "price": 35.00},
                "myoffshore.com": {"available": True, "price": 10.00},
                "anonymous.net": {"available": True, "price": 12.00}
            }
            
            # Default for unknown domains
            result = availability_results.get(domain_name, {"available": True, "price": 15.00})
            
            if result["available"]:
                # Domain is available - show pricing and proceed to registration
                offshore_price = result["price"] * 3.3
                
                text = f"✅ **Domain Available: {domain_name}**\n\n"
                text += f"🏴‍☠️ *Offshore Domain Registration*\n\n"
                text += f"💰 **Pricing Details:**\n"
                text += f"• Base Price: ${result['price']:.2f} USD\n"
                text += f"• Offshore Multiplier: 3.3x\n"
                text += f"• **Total Price: ${offshore_price:.2f} USD**\n\n"
                text += f"📋 **Domain Information:**\n"
                text += f"• Domain: **{domain_name}**\n"
                text += f"• Registration Period: 1 year\n"
                text += f"• Privacy Protection: ✅ Included\n"
                text += f"• Anonymous Contact: ✅ Generated\n"
                text += f"• DNS Management: ✅ Cloudflare\n\n"
                text += f"💳 **Your Balance:** ${session['balance']} USD\n"
                
                if session['balance'] >= Decimal(str(offshore_price)):
                    text += f"✅ Sufficient balance for registration\n\n"
                    text += f"Ready to proceed with registration?"
                    
                    keyboard = [
                        [InlineKeyboardButton("✅ Register Domain", callback_data=f"register_{domain_name}")],
                        [InlineKeyboardButton("🔍 Check Another Domain", callback_data="register_domain")],
                        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]
                    ]
                else:
                    needed = Decimal(str(offshore_price)) - session['balance']
                    text += f"⚠️ Need ${needed:.2f} more in wallet\n\n"
                    text += f"Add funds or pay with cryptocurrency?"
                    
                    keyboard = [
                        [InlineKeyboardButton("💰 Add Funds to Wallet", callback_data="add_funds_menu")],
                        [InlineKeyboardButton("💎 Pay with Crypto", callback_data=f"crypto_pay_{domain_name}")],
                        [InlineKeyboardButton("🔍 Check Another Domain", callback_data="register_domain")],
                        [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]
                    ]
            else:
                # Domain is not available - show alternatives
                text = f"❌ **Domain Unavailable: {domain_name}**\n\n"
                text += f"🏴‍☠️ *Domain Search Results*\n\n"
                text += f"The domain **{domain_name}** is already registered.\n\n"
                text += f"🔍 **Alternative Suggestions:**\n"
                
                # Generate alternative domain suggestions
                base_name = domain_name.split('.')[0]
                extension = '.' + domain_name.split('.')[1]
                
                alternatives = [
                    f"{base_name}2{extension}",
                    f"{base_name}-offshore{extension}",
                    f"secure-{base_name}{extension}",
                    f"{base_name}.net" if extension != ".net" else f"{base_name}.org",
                    f"{base_name}.io" if extension != ".io" else f"{base_name}.co"
                ]
                
                for alt in alternatives[:3]:
                    alt_price = 15.00 * 3.3
                    text += f"• **{alt}** - ${alt_price:.2f} USD\n"
                
                keyboard = []
                for alt in alternatives[:2]:
                    keyboard.append([InlineKeyboardButton(f"🔍 Check {alt}", callback_data=f"check_domain_{alt}")])
                
                keyboard.extend([
                    [InlineKeyboardButton("🔍 Try Different Search", callback_data="register_domain")],
                    [InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_menu")]
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def handle_domain_registration_proceed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle proceeding with domain registration"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        # Extract domain from callback data
        domain = query.data.replace("register_", "")
        session['domain_name'] = domain
        session['state'] = UserState.EMAIL_COLLECTION
        
        text = f"📧 **Email Collection**\n\n"
        text += f"🏴‍☠️ *Domain Registration: {domain}*\n\n"
        text += f"We need an email address for domain registration notifications and account management.\n\n"
        text += f"📨 **Email Options:**\n"
        text += f"• Provide your email for notifications\n"
        text += f"• Skip for completely anonymous registration\n\n"
        text += f"⚠️ **Note:** Anonymous registration means no recovery options if you lose access to this Telegram account.\n"
        
        keyboard = [
            [InlineKeyboardButton("📧 Provide Email", callback_data="provide_email")],
            [InlineKeyboardButton("🔒 Skip (Anonymous)", callback_data="skip_email")],
            [InlineKeyboardButton("⬅️ Back to Domain Search", callback_data="register_domain")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_crypto_payment_for_domain(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cryptocurrency payment for domain registration"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        # Extract domain from callback data
        domain = query.data.replace("crypto_pay_", "")
        session['domain_name'] = domain
        
        # Calculate price with 3.3x multiplier
        base_price = 15.00  # Default price
        offshore_price = base_price * 3.3
        
        text = f"💎 **Cryptocurrency Payment**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n"
        text += f"💰 *Amount: ${offshore_price:.2f} USD*\n\n"
        text += f"Select your preferred cryptocurrency for payment:\n\n"
        text += f"⚡ **Available Cryptocurrencies:**\n"
        text += f"• Bitcoin (BTC) - Most secure\n"
        text += f"• Ethereum (ETH) - Fast transactions\n"
        text += f"• Litecoin (LTC) - Low fees\n"
        text += f"• Dogecoin (DOGE) - Popular choice\n"
        
        keyboard = [
            [
                InlineKeyboardButton("₿ Bitcoin", callback_data=f"crypto_btc_{domain}"),
                InlineKeyboardButton("🔷 Ethereum", callback_data=f"crypto_eth_{domain}")
            ],
            [
                InlineKeyboardButton("🟢 Litecoin", callback_data=f"crypto_ltc_{domain}"),
                InlineKeyboardButton("🐕 Dogecoin", callback_data=f"crypto_doge_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Domain Details", callback_data=f"check_domain_{domain}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_payment_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment choice - wallet vs crypto"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        # Extract payment method and domain from callback data
        parts = query.data.split('_')
        if len(parts) >= 3:
            payment_method = parts[1]  # wallet or crypto
            domain = '_'.join(parts[2:])
        else:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        session['domain_name'] = domain
        
        if payment_method == "wallet":
            # Process wallet payment
            base_price = 15.00
            offshore_price = base_price * 3.3
            
            if session['balance'] >= Decimal(str(offshore_price)):
                # Deduct from wallet and simulate registration
                session['balance'] -= Decimal(str(offshore_price))
                
                text = f"✅ **Domain Registration Successful!**\n\n"
                text += f"🏴‍☠️ *Nameword Offshore Hosting*\n\n"
                text += f"📋 **Registration Details:**\n"
                text += f"• Domain: **{domain}**\n"
                text += f"• Payment: ${offshore_price:.2f} USD (Wallet)\n"
                text += f"• Status: ✅ Registered\n"
                text += f"• DNS: ☁️ Cloudflare Managed\n"
                text += f"• Privacy: ✅ Protected\n\n"
                text += f"💰 **Remaining Balance:** ${session['balance']} USD\n\n"
                text += f"🎉 **Congratulations!** Your offshore domain is now active and ready to use.\n\n"
                text += f"📧 You will receive setup instructions shortly."
                
                keyboard = [
                    [InlineKeyboardButton("🌐 View My Domains", callback_data="my_domains")],
                    [InlineKeyboardButton("⚙️ Manage DNS", callback_data="manage_dns")],
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                # Insufficient balance
                needed = Decimal(str(offshore_price)) - session['balance']
                text = f"❌ **Insufficient Wallet Balance**\n\n"
                text += f"Need ${needed:.2f} more for wallet payment.\n"
                text += f"Please add funds or use cryptocurrency payment."
                
                keyboard = [
                    [InlineKeyboardButton("💰 Add Funds", callback_data="add_funds_menu")],
                    [InlineKeyboardButton("💎 Pay with Crypto", callback_data=f"pay_crypto_{domain}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        
        elif payment_method == "crypto":
            # Redirect to crypto selection
            await self.show_crypto_selection(update, context)

    async def handle_payment_address_actions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment address actions - copy, check status, generate QR"""
        query = update.callback_query
        if not query or not query.data or not query.from_user:
            return
        
        parts = query.data.split('_')
        if len(parts) < 3:
            return
        
        action = parts[0]  # copy_address, check_payment, generate_qr
        crypto_type = parts[1] if len(parts) > 1 else 'btc'
        domain = '_'.join(parts[2:]) if len(parts) > 2 else 'example.com'
        
        if action == "copy":
            # Copy address action
            sample_addresses = {
                'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'eth': '0x742d35cc6486c5d2c4c8d2f2c4b6b2a5ed7e4c6f',
                'ltc': 'LQTpS7UFBHBsN8BjHVsqnKGZzG6Q5UgLSZ',
                'doge': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L'
            }
            
            address = sample_addresses.get(crypto_type, sample_addresses['btc'])
            await query.answer(f"📋 Address copied: {address[:8]}...{address[-8:]}")
            
        elif action == "check":
            # Check payment status
            text = f"🔍 **Payment Status Check**\n\n"
            text += f"🏴‍☠️ *Domain: {domain}*\n"
            text += f"💰 *Checking blockchain for payments...*\n\n"
            text += f"⏰ **Status:** Waiting for payment\n"
            text += f"📡 **Network:** Monitoring blockchain\n"
            text += f"🔄 **Confirmations:** 0/required\n\n"
            text += f"💡 **Next Steps:**\n"
            text += f"1. Send payment to the address above\n"
            text += f"2. Wait for blockchain confirmation\n"
            text += f"3. Domain will register automatically\n"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh Status", callback_data=f"check_payment_{crypto_type}_{domain}")],
                [InlineKeyboardButton("⬅️ Back to Payment", callback_data=f"crypto_{crypto_type}_{domain}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif action == "generate":
            # Generate QR code (simulated)
            await query.answer("📱 QR code would be generated here for mobile scanning")

    async def handle_update_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle email update request during registration workflow"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        domain = session.get('domain_name', 'example.com')
        
        text = f"📧 **Update Email Address**\n\n"
        text += f"🏴‍☠️ *Domain Registration: {domain}*\n\n"
        text += f"Current Email: {session.get('email', 'Not provided (Anonymous)')}\n\n"
        text += f"Choose your email preference:\n\n"
        text += f"📨 **Provide Email**\n"
        text += f"• Receive domain registration notifications\n"
        text += f"• Account recovery options available\n"
        text += f"• Support communication channel\n\n"
        text += f"🔒 **Anonymous Registration**\n"
        text += f"• No email required\n"
        text += f"• Complete privacy protection\n"
        text += f"• No recovery options if Telegram access lost\n"
        
        keyboard = [
            [InlineKeyboardButton("📧 Provide Email", callback_data="provide_email")],
            [InlineKeyboardButton("🔒 Skip (Anonymous)", callback_data="skip_email")],
            [InlineKeyboardButton("⬅️ Back to Payment Options", callback_data="back_to_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_update_dns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle DNS configuration update during registration workflow"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        domain = session.get('domain_name', 'example.com')
        current_dns = session.get('dns_choice', 'cloudflare')
        
        text = f"⚙️ **Update DNS Configuration**\n\n"
        text += f"🏴‍☠️ *Domain Registration: {domain}*\n\n"
        text += f"Current DNS: {'☁️ Cloudflare (Managed)' if current_dns == 'cloudflare' else '🛠️ Custom Nameservers'}\n\n"
        text += f"Choose your DNS management preference:\n\n"
        text += f"☁️ **Cloudflare DNS (Managed by Nameword)**\n"
        text += f"• Professional DNS infrastructure\n"
        text += f"• Global CDN acceleration\n"
        text += f"• DDoS protection included\n"
        text += f"• Easy management interface\n"
        text += f"• SSL certificates available\n\n"
        text += f"🛠️ **Custom DNS Servers**\n"
        text += f"• Use your own nameservers\n"
        text += f"• Full DNS control\n"
        text += f"• Third-party DNS providers\n"
        text += f"• Advanced configuration options\n\n"
        text += f"💡 **Recommendation:** Cloudflare DNS for ease of use and performance."
        
        keyboard = [
            [InlineKeyboardButton("☁️ Cloudflare DNS (Managed)", callback_data="dns_cloudflare")],
            [InlineKeyboardButton("🛠️ Custom Nameservers", callback_data="dns_custom")],
            [InlineKeyboardButton("⬅️ Back to Payment Options", callback_data="back_to_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def show_dns_selection_via_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show DNS selection via regular message (not callback query edit)"""
        user_id = update.effective_user.id
        session = await self.get_user_session(user_id)
        domain = session.get('domain_name', 'example.com')
        
        text = f"⚙️ **DNS Configuration Selection**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n\n"
        text += f"Choose your DNS management preference:\n\n"
        text += f"☁️ **Cloudflare DNS (Managed by Nameword)**\n"
        text += f"• Professional DNS infrastructure\n"
        text += f"• Global CDN acceleration\n"
        text += f"• DDoS protection included\n"
        text += f"• Easy management interface\n"
        text += f"• SSL certificates available\n\n"
        text += f"🛠️ **Custom DNS Servers**\n"
        text += f"• Use your own nameservers\n"
        text += f"• Full DNS control\n"
        text += f"• Third-party DNS providers\n"
        text += f"• Advanced configuration options\n\n"
        text += f"💡 **Recommendation:** Cloudflare DNS for ease of use and performance."
        
        keyboard = [
            [InlineKeyboardButton("☁️ Cloudflare DNS (Managed)", callback_data="dns_cloudflare")],
            [InlineKeyboardButton("🛠️ Custom Nameservers", callback_data="dns_custom")],
            [InlineKeyboardButton("⬅️ Back to Email Collection", callback_data="skip_email")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_wallet_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle wallet balance payment processing"""
        query = update.callback_query
        if not query or not query.from_user:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        domain = session.get('domain_name', 'example.com')
        
        # Calculate pricing
        base_price = 15.00
        offshore_price = base_price * 3.3
        
        # Check wallet balance
        if session['balance'] >= Decimal(str(offshore_price)):
            # Process payment
            session['balance'] -= Decimal(str(offshore_price))
            session['total_spent'] += offshore_price
            session['state'] = UserState.REGISTRATION_PROCESSING
            
            # Show payment success and domain registration
            await self.show_payment_success_wallet(update, context, domain, offshore_price)
        else:
            needed = Decimal(str(offshore_price)) - session['balance']
            text = f"⚠️ **Insufficient Wallet Balance**\n\n"
            text += f"🏴‍☠️ *Domain: {domain}*\n\n"
            text += f"💰 **Payment Details:**\n"
            text += f"• Required: ${offshore_price:.2f} USD\n"
            text += f"• Your Balance: ${session['balance']} USD\n"
            text += f"• **Need: ${needed:.2f} USD more**\n\n"
            text += f"Choose an alternative payment method:"
            
            keyboard = [
                [InlineKeyboardButton("💎 Pay with Cryptocurrency", callback_data=f"pay_crypto_{domain}")],
                [InlineKeyboardButton("💰 Add Funds to Wallet", callback_data="add_funds_menu")],
                [InlineKeyboardButton("⬅️ Back to Payment Options", callback_data="back_to_payment")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def show_payment_success_wallet(self, update: Update, context: ContextTypes.DEFAULT_TYPE, domain: str, amount: float):
        """Show wallet payment success and begin domain registration"""
        query = update.callback_query
        if not query:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        text = f"✅ **Payment Successful - Processing Registration**\n\n"
        text += f"🏴‍☠️ *Domain Registration: {domain}*\n\n"
        text += f"💰 **Payment Confirmed:**\n"
        text += f"• Amount: ${amount:.2f} USD\n"
        text += f"• Method: Wallet Balance\n"
        text += f"• Remaining Balance: ${session['balance']} USD\n\n"
        text += f"🔄 **Registration Status:**\n"
        text += f"• Payment: ✅ Completed\n"
        text += f"• Domain Registration: 🔄 Processing...\n"
        text += f"• DNS Setup: ⏳ Pending\n"
        text += f"• Email Configuration: ⏳ Pending\n\n"
        text += f"⏰ **Estimated Completion:** 2-5 minutes\n\n"
        text += f"💡 **Next Steps:**\n"
        text += f"You will receive automatic notification when registration completes. Domain will appear in your 'My Domains' section."
        
        keyboard = [
            [InlineKeyboardButton("🔄 Check Registration Status", callback_data=f"check_registration_{domain}")],
            [InlineKeyboardButton("🌐 My Domains", callback_data="my_domains")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Simulate domain registration completion after 3 seconds
        await asyncio.sleep(3)
        await self.complete_domain_registration(update, context, domain, amount, "wallet")

    async def handle_payment_status_check(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle real-time payment status checking"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        # Parse callback data: check_payment_crypto_domain
        parts = query.data.split('_')
        if len(parts) >= 4:
            crypto_type = parts[2]
            domain = '_'.join(parts[3:])
        else:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        # Simulate payment status checking
        import random
        payment_received = random.choice([True, False, False])  # 33% chance of payment
        
        if payment_received:
            # Payment detected - process registration
            base_price = 15.00
            offshore_price = base_price * 3.3
            
            # Simulate overpayment/underpayment scenarios
            payment_scenarios = [
                {"received": offshore_price, "status": "exact"},
                {"received": offshore_price + 5.50, "status": "overpaid"},
                {"received": offshore_price - 8.20, "status": "underpaid"}
            ]
            scenario = random.choice(payment_scenarios)
            
            await self.handle_payment_confirmation(update, context, domain, crypto_type, scenario)
        else:
            # No payment detected yet
            text = f"🔍 **Payment Status Check**\n\n"
            text += f"🏴‍☠️ *Domain: {domain}*\n"
            text += f"💎 *Currency: {crypto_type.upper()}*\n\n"
            text += f"📡 **Blockchain Monitoring:**\n"
            text += f"• Status: ⏳ Monitoring blockchain...\n"
            text += f"• Confirmations: 0/required\n"
            text += f"• Last Check: Just now\n\n"
            text += f"⚡ **Payment Status:** No payment detected yet\n\n"
            text += f"💡 **Please ensure:**\n"
            text += f"• You sent the exact amount\n"
            text += f"• Payment was sent to the correct address\n"
            text += f"• Network fees are included\n\n"
            text += f"⏰ **Payment expires in:** 23h 45m"
            
            keyboard = [
                [
                    InlineKeyboardButton("🔄 Check Again", callback_data=f"check_payment_{crypto_type}_{domain}"),
                    InlineKeyboardButton("🔄 Switch Currency", callback_data=f"pay_crypto_{domain}")
                ],
                [
                    InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_address_{crypto_type}_{domain}"),
                    InlineKeyboardButton("📱 Generate QR", callback_data=f"generate_qr_{crypto_type}_{domain}")
                ],
                [InlineKeyboardButton("⬅️ Back to Payment", callback_data=f"crypto_{crypto_type}_{domain}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def handle_payment_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, domain: str, crypto_type: str, scenario: dict):
        """Handle payment confirmation with overpayment/underpayment scenarios"""
        query = update.callback_query
        if not query:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        base_price = 15.00
        offshore_price = base_price * 3.3
        received_amount = scenario["received"]
        status = scenario["status"]
        
        if status == "exact":
            text = f"✅ **Payment Confirmed - Exact Amount**\n\n"
            text += f"🏴‍☠️ *Domain: {domain}*\n"
            text += f"💎 *Currency: {crypto_type.upper()}*\n\n"
            text += f"💰 **Payment Details:**\n"
            text += f"• Required: ${offshore_price:.2f} USD\n"
            text += f"• Received: ${received_amount:.2f} USD\n"
            text += f"• Status: ✅ Perfect match\n\n"
            text += f"🔄 **Processing domain registration...**"
            
        elif status == "overpaid":
            excess = received_amount - offshore_price
            session['balance'] += Decimal(str(excess))
            text = f"✅ **Payment Confirmed - Overpayment Detected**\n\n"
            text += f"🏴‍☠️ *Domain: {domain}*\n"
            text += f"💎 *Currency: {crypto_type.upper()}*\n\n"
            text += f"💰 **Payment Details:**\n"
            text += f"• Required: ${offshore_price:.2f} USD\n"
            text += f"• Received: ${received_amount:.2f} USD\n"
            text += f"• Overpayment: +${excess:.2f} USD\n\n"
            text += f"🎁 **Bonus Credit Applied:**\n"
            text += f"${excess:.2f} USD added to your wallet!\n"
            text += f"New Balance: ${session['balance']} USD\n\n"
            text += f"🔄 **Processing domain registration...**"
            
        elif status == "underpaid":
            shortage = offshore_price - received_amount
            text = f"⚠️ **Payment Received - Underpayment Detected**\n\n"
            text += f"🏴‍☠️ *Domain: {domain}*\n"
            text += f"💎 *Currency: {crypto_type.upper()}*\n\n"
            text += f"💰 **Payment Details:**\n"
            text += f"• Required: ${offshore_price:.2f} USD\n"
            text += f"• Received: ${received_amount:.2f} USD\n"
            text += f"• Shortage: -${shortage:.2f} USD\n\n"
            text += f"💡 **Options:**\n"
            text += f"• Send additional ${shortage:.2f} USD\n"
            text += f"• Or use wallet balance to cover difference\n\n"
            text += f"⏰ **Payment expires in:** 23h 15m"
            
            keyboard = [
                [InlineKeyboardButton("💰 Use Wallet Balance", callback_data=f"cover_shortage_{domain}")],
                [InlineKeyboardButton("💎 Send Additional Payment", callback_data=f"crypto_{crypto_type}_{domain}")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # For exact and overpayment scenarios, proceed with registration
        keyboard = [
            [InlineKeyboardButton("🌐 View My Domains", callback_data="my_domains")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Complete registration process
        await asyncio.sleep(2)
        await self.complete_domain_registration(update, context, domain, received_amount, crypto_type)

    async def complete_domain_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE, domain: str, amount: float, payment_method: str):
        """Complete domain registration and show success screen"""
        query = update.callback_query
        if not query:
            return
        
        user_id = query.from_user.id
        session = await self.get_user_session(user_id)
        
        # Add domain to user's domain list (simulate successful registration)
        if not hasattr(self, 'user_domains'):
            self.user_domains = {}
        if user_id not in self.user_domains:
            self.user_domains[user_id] = []
        
        new_domain = {
            'name': domain,
            'expires': 'Jul 23, 2026',
            'dns_records': 3,
            'status': '✅ Active',
            'nameservers': ['anderson.ns.cloudflare.com', 'leanna.ns.cloudflare.com'],
            'registration_date': 'Jul 23, 2025',
            'payment_amount': amount,
            'payment_method': payment_method
        }
        self.user_domains[user_id].append(new_domain)
        
        # Update session
        session['total_spent'] += amount
        session['state'] = UserState.READY
        
        text = f"🎉 **Domain Registration Complete!**\n\n"
        text += f"✅ **SUCCESS: {domain}**\n\n"
        text += f"🏴‍☠️ **Registration Summary:**\n"
        text += f"• Domain: **{domain}**\n"
        text += f"• Status: ✅ Active and operational\n"
        text += f"• Expires: Jul 23, 2026 (1 year)\n"
        text += f"• DNS: ☁️ Cloudflare managed\n"
        text += f"• Privacy: ✅ Full anonymous protection\n"
        text += f"• SSL: ✅ Available\n\n"
        text += f"💰 **Payment Confirmed:**\n"
        text += f"• Amount: ${amount:.2f} USD\n"
        text += f"• Method: {payment_method.title()}\n"
        text += f"• Total Spent: ${session['total_spent']:.2f} USD\n\n"
        text += f"🔧 **Ready for Use:**\n"
        text += f"• DNS propagation: ✅ Complete\n"
        text += f"• Nameservers: ✅ Configured\n"
        text += f"• Management: ✅ Available\n\n"
        text += f"🚀 **Your domain is now live and ready to use!**"
        
        keyboard = [
            [
                InlineKeyboardButton("🛠️ Manage DNS", callback_data=f"dns_manage_{domain}"),
                InlineKeyboardButton("🌐 My Domains", callback_data="my_domains")
            ],
            [
                InlineKeyboardButton("📝 Register Another", callback_data="register_domain"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_copy_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle copy payment address functionality"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        # Parse callback data: copy_address_crypto_domain
        parts = query.data.split('_')
        if len(parts) >= 4:
            crypto_type = parts[2]
            domain = '_'.join(parts[3:])
        else:
            return
        
        # Sample addresses for demonstration
        sample_addresses = {
            'btc': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            'eth': '0x742d35cc6486c5d2c4c8d2f2c4b6b2a5ed7e4c6f',
            'ltc': 'LQTpS7UFBHBsN8BjHVsqnKGZzG6Q5UgLSZ',
            'doge': 'DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L'
        }
        
        address = sample_addresses.get(crypto_type, sample_addresses['btc'])
        
        text = f"📋 **Payment Address Copied**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n"
        text += f"💎 *Currency: {crypto_type.upper()}*\n\n"
        text += f"**Payment Address:**\n"
        text += f"`{address}`\n\n"
        text += f"✅ **Address has been copied to clipboard**\n\n"
        text += f"💡 **Instructions:**\n"
        text += f"1. Paste address in your wallet\n"
        text += f"2. Send the exact USD equivalent\n"
        text += f"3. Wait for confirmation\n"
        text += f"4. Registration will process automatically"
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Check Payment Status", callback_data=f"check_payment_{crypto_type}_{domain}"),
                InlineKeyboardButton("🔄 Switch Currency", callback_data=f"pay_crypto_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Payment", callback_data=f"crypto_{crypto_type}_{domain}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.answer("📋 Address copied!", show_alert=False)
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def handle_generate_qr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle QR code generation for payment address"""
        query = update.callback_query
        if not query or not query.data:
            return
        
        # Parse callback data: generate_qr_crypto_domain
        parts = query.data.split('_')
        if len(parts) >= 4:
            crypto_type = parts[2]
            domain = '_'.join(parts[3:])
        else:
            return
        
        text = f"📱 **QR Code Generated**\n\n"
        text += f"🏴‍☠️ *Domain: {domain}*\n"
        text += f"💎 *Currency: {crypto_type.upper()}*\n\n"
        text += f"📷 **QR Code for Mobile Payment:**\n\n"
        text += f"┌─────────────────────────┐\n"
        text += f"│ █▀▀▀▀▀█ ▄▀█ █▀▀▀▀▀█ │\n"
        text += f"│ █ ███ █ ▀▄▀ █ ███ █ │\n"
        text += f"│ █ ▀▀▀ █ █▄█ █ ▀▀▀ █ │\n"
        text += f"│ ▀▀▀▀▀▀▀ ▀ █ ▀▀▀▀▀▀▀ │\n"
        text += f"│ ██▄█▀▀▀█▄▀▀█▀██▄█▀▀ │\n"
        text += f"│ ▀█ ▄▀▀▄▀█▄█▀▄▀▀▄▀█▀ │\n"
        text += f"│ ▀▀▀▀▀▀▀ █ ▄ █▀▀▀▀▀█ │\n"
        text += f"│ █▀▀▀▀▀█ ▀▀▄ █ ███ █ │\n"
        text += f"│ █ ▀▀▀ █ █▀█ █▄▄▄▄▄█ │\n"
        text += f"│ ▀▀▀▀▀▀▀ ▀▀▀ ▀▀▀▀▀▀▀ │\n"
        text += f"└─────────────────────────┘\n\n"
        text += f"📱 **Scan with mobile wallet app**\n"
        text += f"💡 **Amount will be auto-filled**"
        
        keyboard = [
            [
                InlineKeyboardButton("📋 Copy Address", callback_data=f"copy_address_{crypto_type}_{domain}"),
                InlineKeyboardButton("🔄 Check Status", callback_data=f"check_payment_{crypto_type}_{domain}")
            ],
            [InlineKeyboardButton("⬅️ Back to Payment", callback_data=f"crypto_{crypto_type}_{domain}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

def main():
    """Main function to run the bot"""
    # Create bot instance
    bot = Nomadly3Bot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CallbackQueryHandler(bot.handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Start bot
    logger.info("Starting Nomadly3 Simple bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()