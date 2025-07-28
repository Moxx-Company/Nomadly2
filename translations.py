"""
Nomadly2 - Translation System v1.4
Bilingual support for English and French
"""

from typing import Dict, Optional
from database import get_db_manager, Translation


class TranslationService:
    """Manage translations for bilingual bot"""

    def __init__(self):
        self.db = get_db_manager()
        self.cache = {}
        self.load_default_translations()

    def get_text(self, key: str, language_code: str = "en", **kwargs) -> str:
        """Get translated text with parameter substitution"""
        cache_key = f"{key}_{language_code}"

        if cache_key not in self.cache:
            session = self.db.get_session()
            try:
                translation = (
                    session.query(Translation)
                    .filter(
                        Translation.key == key,
                        Translation.language_code == language_code,
                    )
                    .first()
                )

                if translation:
                    self.cache[cache_key] = translation.translation_text
                else:
                    # Fallback to English if translation not found
                    if language_code != "en":
                        return self.get_text(key, "en", **kwargs)
                    # Return key if no translation found
                    self.cache[cache_key] = f"[{key}]"
            finally:
                session.close()

        text = self.cache[cache_key]

        # Substitute parameters
        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError):
                pass

        return text

    def get_user_language(self, telegram_id: int) -> str:
        """Get user's preferred language"""
        session = self.db.get_session()
        try:
            user = (
                session.query(self.db.User)
                .filter(self.db.User.telegram_id == telegram_id)
                .first()
            )
            return user.language_code if user else "en"
        except:
            return "en"
        finally:
            session.close()

    def load_default_translations(self):
        """Load default translations into database"""
        default_translations = {
            # Welcome and onboarding
            "welcome_message": {
                "en": "🌊 Welcome to Nomadly2\nOffshore Domain Management\n\n🏴‍☠️ Resilience | Discretion | Independence\n\nChoose your language:",
                "fr": "🌊 Bienvenue sur Nomadly2\nGestion de Domaines Offshore\n\n🏴‍☠️ Résilience | Discrétion | Indépendance\n\nChoisissez votre langue:",
            },
            "language_confirmed": {
                "en": "✅ Language set to English\n\n🏴‍☠️ Nomadly2 Domain Bot\nResilience | Discretion | Independence\n\nReady to manage domains with complete privacy.\n\nYour secure gateway to offshore domain registration.",
                "fr": "✅ Langue définie en Français\n\n🏴‍☠️ Bot de Domaine Nomadly2\nRésilience | Discrétion | Indépendance\n\nPrêt à gérer les domaines en toute confidentialité.\n\nVotre passerelle sécurisée vers l'enregistrement de domaines offshore.",
            },
            # Main menu
            "main_menu_title": {
                "en": "🏴‍☠️ Nomadly2 Domain Bot\nBalance: ${balance} USD\n\nSelect a service:",
                "fr": "🏴‍☠️ Bot de Domaine Nomadly2\nSolde: ${balance} USD\n\nSélectionnez un service:",
            },
            "search_domain": {
                "en": "🔍 Search Domain",
                "fr": "🔍 Rechercher un Domaine",
            },
            "my_domains": {"en": "🌐 My Domains", "fr": "🌐 Mes Domaines"},
            "wallet": {"en": "💰 Wallet", "fr": "💰 Portefeuille"},
            "manage_dns": {"en": "🛠️ Manage DNS", "fr": "🛠️ Gérer DNS"},
            "update_nameservers": {
                "en": "🔄 Update Nameservers",
                "fr": "🔄 Mettre à jour les Serveurs de Noms",
            },
            "support": {"en": "📞 Support", "fr": "📞 Support"},
            "change_language": {
                "en": "🌍 Change Language",
                "fr": "🌍 Changer de Langue",
            },
            # Domain search
            "domain_search_title": {
                "en": "🔍 Domain Search\n\n🏴‍☠️ Offshore Domain Registration\nComplete privacy • Anonymous contacts • Crypto payments\n\nEnter the domain name you want to search:\nExample: mynewdomain.com\n\n🌐 Real-time Nameword Pricing:\n• .com (from $11.98/year) • .net (from $15.53/year)\n• .org (from $8.99/year) • .info (from $3.99/year)\n• .sbs (from $2.99/year) • .biz (from $11.99/year)\n\n💡 Tips:\n• Enter domain without 'www' prefix\n• Use only letters, numbers, and hyphens\n• Maximum 63 characters\n\n⏳ Live pricing and availability via Nameword API",
                "fr": "🔍 Recherche de Domaine\n\nEntrez le nom de domaine que vous souhaitez rechercher:\nExemple: `monnouveudomaine.com`\n\nTLD supportés:\n• .com • .net • .org • .info • .biz\n\n💡 Conseil: Entrez le domaine sans préfixe 'www'",
            },
            "domain_available": {
                "en": "✅ Domain Available: {domain}\nPrice: ${price}/year\n\nThis domain is available for registration!",
                "fr": "✅ Domaine Disponible: {domain}\nPrix: ${price}/an\n\nCe domaine est disponible pour l'enregistrement!",
            },
            "domain_unavailable": {
                "en": "❌ Domain Unavailable: {domain}\n\nThis domain is already registered or not available.",
                "fr": "❌ Domaine Indisponible: {domain}\n\nCe domaine est déjà enregistré ou indisponible.",
            },
            # Wallet
            "wallet_title": {
                "en": "💰 Wallet & Payments\n\n💵 Current Balance: ${balance} USD\n\nSupported Cryptocurrencies:\n• 🟠 Bitcoin (BTC)\n• 🔵 Ethereum (ETH)\n• 🟢 Litecoin (LTC)\n• 🟡 Tether (USDT)\n• 🐕 Dogecoin (DOGE)\n• 🔴 TRON (TRX)\n• 🟨 Binance Coin (BNB)\n• 🟠 Bitcoin Cash (BCH)\n• 🔵 Dash (DASH)\n• 🟣 Polygon (MATIC)\n\nAll payments processed securely via BlockBee",
                "fr": "💰 Portefeuille & Paiements\n\n💵 Solde Actuel: ${balance} USD\n\nCryptomonnaies Supportées:\n• 🟠 Bitcoin (BTC)\n• 🔵 Ethereum (ETH)\n• 🟢 Litecoin (LTC)\n• 🟡 Tether (USDT)\n• 🐕 Dogecoin (DOGE)\n• 🔴 TRON (TRX)\n• 🟨 Binance Coin (BNB)\n• 🟠 Bitcoin Cash (BCH)\n• 🔵 Dash (DASH)\n• 🟣 Polygon (MATIC)\n\nTous les paiements traités en sécurité via BlockBee",
            },
            # DNS Management
            "dns_management_title": {
                "en": "🛠️ DNS Management\n\nManage DNS records for your domains:\n\nSupported Record Types:\n• A - Point to IPv4 address\n• AAAA - Point to IPv6 address\n• MX - Mail exchange records\n• TXT - Text records\n• CNAME - Canonical name records\n• SRV - Service records\n• NS - Name server records\n\n⚡ Changes apply instantly via Cloudflare\n🔄 Select a domain to manage its DNS",
                "fr": "🛠️ Gestion DNS\n\nGérez les enregistrements DNS pour vos domaines:\n\nTypes d'Enregistrements Supportés:\n• A - Pointer vers une adresse IPv4\n• AAAA - Pointer vers une adresse IPv6\n• MX - Enregistrements d'échange de courrier\n• TXT - Enregistrements de texte\n• CNAME - Enregistrements de nom canonique\n• SRV - Enregistrements de service\n• NS - Enregistrements de serveur de noms\n\n⚡ Les changements s'appliquent instantanément via Cloudflare\n🔄 Sélectionnez un domaine pour gérer son DNS",
            },
            # Nameserver Management
            "nameserver_management_title": {
                "en": "🔄 Nameserver Management\n\nRegistration Options:\n✅ Use Cloudflare nameservers (default & secure)\n✅ Use custom nameservers\n✅ Skip (OpenProvider defaults)\n\nPost-Registration Management:\n🔁 Switch between NS modes\n🛠️ Manually update NS1–NS4\n🔍 View current NS records\n♻️ Revert to Cloudflare nameservers\n\nSelect a domain to manage nameservers:",
                "fr": "🔄 Gestion des Serveurs de Noms\n\nOptions d'Enregistrement:\n✅ Utiliser les serveurs de noms Cloudflare (par défaut et sécurisé)\n✅ Utiliser des serveurs de noms personnalisés\n✅ Ignorer (par défaut OpenProvider)\n\nGestion Post-Enregistrement:\n🔁 Basculer entre les modes NS\n🛠️ Mettre à jour manuellement NS1–NS4\n🔍 Voir les enregistrements NS actuels\n♻️ Revenir aux serveurs de noms Cloudflare\n\nSélectionnez un domaine pour gérer les serveurs de noms:",
            },
            # Support
            "support_title": {
                "en": "📞 Support & Help\n\n🆘 Need assistance?\n\nContact Options:\n📱 Telegram: @nomadlysupport\n💬 Community: @NomadlyHQ\n\nCommon Topics:\n• Domain registration help\n• DNS configuration assistance\n• Payment and wallet support\n• Technical troubleshooting\n\n🕐 Support Hours: 24/7\n⚡ Response Time: Usually within 1 hour\n\n🔒 All communications are private and secure",
                "fr": "📞 Support & Aide\n\n🆘 Besoin d'assistance?\n\nOptions de Contact:\n📱 Telegram: @nomadlysupport\n💬 Communauté: @NomadlyHQ\n\nSujets Courants:\n• Aide à l'enregistrement de domaine\n• Assistance de configuration DNS\n• Support de paiement et portefeuille\n• Dépannage technique\n\n🕐 Heures de Support: 24/7\n⚡ Temps de Réponse: Généralement dans l'heure\n\n🔒 Toutes les communications sont privées et sécurisées",
            },
            # Common buttons
            "back_to_menu": {"en": "⬅️ Back to Menu", "fr": "⬅️ Retour au Menu"},
            "add_funds": {"en": "💰 Add Funds", "fr": "💰 Ajouter des Fonds"},
            "transaction_history": {
                "en": "📊 Transaction History",
                "fr": "📊 Historique des Transactions",
            },
            "enter_main_menu": {
                "en": "🚀 Enter Main Menu",
                "fr": "🚀 Accéder au Menu Principal",
            },
            # Main menu and navigation
            "main_menu": {
                "en": "🏴‍☠️ Main Menu - Choose an option:",
                "fr": "🏴‍☠️ Menu Principal - Choisissez une option:",
            },
            "yes": {"en": "✅ Yes", "fr": "✅ Oui"},
            "no": {"en": "❌ No", "fr": "❌ Non"},
            "try_again": {"en": "🔄 Try Again", "fr": "🔄 Réessayer"},
            # Domain management
            "domain_search": {
                "en": "🔍 Domain Search",
                "fr": "🔍 Recherche de Domaine",
            },
            "register_domain": {
                "en": "📝 Register Domain",
                "fr": "📝 Enregistrer Domaine",
            },
            "domain_price": {"en": "💰 Price: ${price}", "fr": "💰 Prix: ${price}"},
            "dns_setup": {"en": "🌐 DNS Setup", "fr": "🌐 Configuration DNS"},
            "cloudflare_dns": {"en": "☁️ Cloudflare DNS", "fr": "☁️ DNS Cloudflare"},
            "registrar_default": {
                "en": "🔧 Registrar Default",
                "fr": "🔧 Par Défaut Registraire",
            },
            "custom_nameservers": {
                "en": "⚙️ Custom Nameservers",
                "fr": "⚙️ Serveurs de Noms Personnalisés",
            },
            "domain_registered": {
                "en": "✅ Domain Registered Successfully!",
                "fr": "✅ Domaine Enregistré avec Succès!",
            },
            "registration_failed": {
                "en": "❌ Registration Failed",
                "fr": "❌ Échec de l'Enregistrement",
            },
            # Payment system
            "payment_methods": {
                "en": "💳 Payment Methods",
                "fr": "💳 Méthodes de Paiement",
            },
            "balance_payment": {
                "en": "💰 Pay with Balance",
                "fr": "💰 Payer avec le Solde",
            },
            "crypto_payment": {
                "en": "🔗 Cryptocurrency Payment",
                "fr": "🔗 Paiement Cryptomonnaie",
            },
            "payment_failed": {"en": "❌ Payment Failed", "fr": "❌ Paiement Échoué"},
            "insufficient_balance": {
                "en": "⚠️ Insufficient Balance",
                "fr": "⚠️ Solde Insuffisant",
            },
            "choose_cryptocurrency": {
                "en": "🔗 Choose Cryptocurrency:",
                "fr": "🔗 Choisir Cryptomonnaie:",
            },
            # Cryptocurrency names
            "bitcoin": {"en": "₿ Bitcoin (BTC)", "fr": "₿ Bitcoin (BTC)"},
            "ethereum": {"en": "⟠ Ethereum (ETH)", "fr": "⟠ Ethereum (ETH)"},
            "usdt": {"en": "💲 Tether (USDT)", "fr": "💲 Tether (USDT)"},
            "litecoin": {"en": "🔷 Litecoin (LTC)", "fr": "🔷 Litecoin (LTC)"},
            "dogecoin": {"en": "🐕 Dogecoin (DOGE)", "fr": "🐕 Dogecoin (DOGE)"},
            "tron": {"en": "🔴 Tron (TRX)", "fr": "🔴 Tron (TRX)"},
            # Loyalty system
            "loyalty_tier": {"en": "🏆 Loyalty Tier", "fr": "🏆 Niveau de Fidélité"},
            "loyalty_points": {
                "en": "⭐ Loyalty Points",
                "fr": "⭐ Points de Fidélité",
            },
            "discount_applied": {
                "en": "💰 Discount Applied: {discount}%",
                "fr": "💰 Remise Appliquée: {discount}%",
            },
            "referral_code": {"en": "👥 Referral Code", "fr": "👥 Code de Parrainage"},
            "referral_bonus": {
                "en": "🎁 Referral Bonus",
                "fr": "🎁 Bonus de Parrainage",
            },
            "bronze_tier": {"en": "🥉 Bronze Tier", "fr": "🥉 Niveau Bronze"},
            "silver_tier": {"en": "🥈 Silver Tier", "fr": "🥈 Niveau Argent"},
            "gold_tier": {"en": "🥇 Gold Tier", "fr": "🥇 Niveau Or"},
            "platinum_tier": {"en": "💎 Platinum Tier", "fr": "💎 Niveau Platine"},
            "diamond_tier": {"en": "💍 Diamond Tier", "fr": "💍 Niveau Diamant"},
            # Invoice system
            "invoice": {"en": "📄 Invoice", "fr": "📄 Facture"},
            "invoice_number": {"en": "🔢 Invoice Number", "fr": "🔢 Numéro de Facture"},
            "payment_address": {
                "en": "📍 Payment Address",
                "fr": "📍 Adresse de Paiement",
            },
            "total_amount": {"en": "💰 Total Amount", "fr": "💰 Montant Total"},
            "qr_code": {"en": "📱 QR Code", "fr": "📱 Code QR"},
            "payment_instructions": {
                "en": "📋 Payment Instructions",
                "fr": "📋 Instructions de Paiement",
            },
            "scan_qr_code": {"en": "📱 Scan QR Code", "fr": "📱 Scanner le Code QR"},
            "copy_address": {"en": "📋 Copy Address", "fr": "📋 Copier l'Adresse"},
            # Additional missing translations
            "invalid_input": {
                "en": "⚠️ Invalid input. Please try again.",
                "fr": "⚠️ Entrée invalide. Veuillez réessayer.",
            },
            "network_error": {
                "en": "🌐 Network error. Please check connection.",
                "fr": "🌐 Erreur réseau. Vérifiez la connexion.",
            },
            "api_error": {
                "en": "🔧 API error. Please try again later.",
                "fr": "🔧 Erreur API. Réessayez plus tard.",
            },
            "admin_panel": {"en": "🛠️ Admin Panel", "fr": "🛠️ Panneau d'Administration"},
            "system_stats": {
                "en": "📊 System Statistics",
                "fr": "📊 Statistiques du Système",
            },
            "revenue_report": {
                "en": "💰 Revenue Report",
                "fr": "💰 Rapport de Revenus",
            },
            "broadcast_message": {
                "en": "📢 Broadcast Message",
                "fr": "📢 Message de Diffusion",
            },
            "contact_support": {
                "en": "📞 Contact Support",
                "fr": "📞 Contacter le Support",
            },
            "help_message": {"en": "❓ Help & FAQ", "fr": "❓ Aide & FAQ"},
            "faq": {"en": "❓ FAQ", "fr": "❓ FAQ"},
            "technical_support": {
                "en": "🔧 Technical Support",
                "fr": "🔧 Support Technique",
            },
            "select_language": {
                "en": "🌍 Select Language",
                "fr": "🌍 Sélectionnez la Langue",
            },
            "english": {"en": "🇺🇸 English", "fr": "🇺🇸 Anglais"},
            "french": {"en": "🇫🇷 French", "fr": "🇫🇷 Français"},
            "language_changed": {
                "en": "✅ Language changed to English",
                "fr": "✅ Langue changée en Français",
            },
            # Error messages
            "error_occurred": {
                "en": "❌ An error occurred. Please try again.",
                "fr": "❌ Une erreur s'est produite. Veuillez réessayer.",
            },
            "api_not_configured": {
                "en": "⚠️ API not configured. Please contact administrator.",
                "fr": "⚠️ API non configurée. Veuillez contacter l'administrateur.",
            },
            "unauthorized_admin": {
                "en": "❌ Unauthorized. Admin access required.",
                "fr": "❌ Non autorisé. Accès administrateur requis.",
            },
            # Success messages
            "language_updated": {
                "en": "✅ Language updated to English",
                "fr": "✅ Langue mise à jour en Français",
            },
            "balance_updated": {
                "en": "✅ Balance updated: ${amount} USD",
                "fr": "✅ Solde mis à jour: ${amount} USD",
            },
            # Admin panel translations
            "admin_panel_title": {
                "en": "🛠️ Admin Panel\n\nSystem Management Dashboard",
                "fr": "🛠️ Panneau d'Administration\n\nTableau de Bord de Gestion du Système",
            },
            "view_orders": {"en": "📋 View Orders", "fr": "📋 Voir les Commandes"},
            "user_management": {
                "en": "👥 User Management",
                "fr": "👥 Gestion des Utilisateurs",
            },
            "payment_status": {
                "en": "💰 Payment Status",
                "fr": "💰 Statut des Paiements",
            },
            "domain_status": {"en": "🌐 Domain Status", "fr": "🌐 Statut des Domaines"},
            "analytics": {"en": "📊 Analytics", "fr": "📊 Analytique"},
            "broadcast": {"en": "📢 Broadcast", "fr": "📢 Diffusion"},
            "back_to_main_menu": {
                "en": "← Back to Main Menu",
                "fr": "← Retour au Menu Principal",
            },
            "back_to_admin": {"en": "← Back to Admin", "fr": "← Retour à l'Admin"},
            "refresh": {"en": "🔄 Refresh", "fr": "🔄 Actualiser"},
            "search_order": {
                "en": "🔍 Search Order",
                "fr": "🔍 Rechercher une Commande",
            },
            "user_stats": {
                "en": "📊 User Stats",
                "fr": "📊 Statistiques des Utilisateurs",
            },
            "find_user": {"en": "🔍 Find User", "fr": "🔍 Trouver un Utilisateur"},
            "balance_admin": {"en": "💰 Balance Admin", "fr": "💰 Admin Balance"},
            "ban_unban": {"en": "🚫 Ban/Unban", "fr": "🚫 Bannir/Débannir"},
            "export_report": {"en": "📈 Export Report", "fr": "📈 Exporter le Rapport"},
            "cancel": {"en": "❌ Cancel", "fr": "❌ Annuler"},
            "broadcast_completed": {
                "en": "✅ Broadcast completed!",
                "fr": "✅ Diffusion terminée!",
            },
            "empty_message_error": {
                "en": "❌ Empty message. Please try again.",
                "fr": "❌ Message vide. Veuillez réessayer.",
            },
            # URL Shortener translations
            "edit_url": {"en": "✏️ Edit URL", "fr": "✏️ Modifier l'URL"},
            "refresh_stats": {
                "en": "🔄 Refresh Stats",
                "fr": "🔄 Actualiser les Stats",
            },
            "back_to_my_urls": {"en": "← Back to My URLs", "fr": "← Retour à Mes URLs"},
            "url_not_found": {"en": "URL not found.", "fr": "URL introuvable."},
            # Payment and domain messages
            "payment_confirmed": {
                "en": "✅ Payment Confirmed!",
                "fr": "✅ Paiement Confirmé!",
            },
            "payment_pending": {
                "en": "⏳ Payment Pending...",
                "fr": "⏳ Paiement en Attente...",
            },
            "domain_registration_successful": {
                "en": "✅ Domain Registration Successful!",
                "fr": "✅ Enregistrement de Domaine Réussi!",
            },
            "contact_creation_successful": {
                "en": "✅ Contact created successfully",
                "fr": "✅ Contact créé avec succès",
            },
            "email_collection_title": {
                "en": "📧 Technical Email Required\n\nPlease provide your technical contact email for domain registration compliance.",
                "fr": "📧 Email Technique Requis\n\nVeuillez fournir votre email de contact technique pour la conformité d'enregistrement de domaine.",
            },
            "email_format_invalid": {
                "en": "❌ Invalid email format. Please enter a valid email address.",
                "fr": "❌ Format d'email invalide. Veuillez entrer une adresse email valide.",
            },
            "email_saved_successfully": {
                "en": "✅ Email saved successfully! This email will be reused for all future domain registrations.",
                "fr": "✅ Email sauvegardé avec succès! Cet email sera réutilisé pour tous les futurs enregistrements de domaine.",
            },
            # Confirmation system translations
            "payment_confirmation_subject": {
                "en": "Payment Confirmed - Nomadly2 Offshore Services",
                "fr": "Paiement Confirmé - Services Offshore Nomadly2",
            },
            "payment_confirmation_title": {
                "en": "🏴‍☠️ PAYMENT CONFIRMATION\nNomadly2 Offshore Services",
                "fr": "🏴‍☠️ CONFIRMATION DE PAIEMENT\nServices Offshore Nomadly2",
            },
            "payment_details": {"en": "Payment Details", "fr": "Détails du Paiement"},
            "amount": {"en": "Amount", "fr": "Montant"},
            "payment_method": {"en": "Payment Method", "fr": "Méthode de Paiement"},
            "transaction_id": {"en": "Transaction ID", "fr": "ID de Transaction"},
            "order_id": {"en": "Order ID", "fr": "ID de Commande"},
            "date": {"en": "Date", "fr": "Date"},
            "service_details": {"en": "Service Details", "fr": "Détails du Service"},
            "service_processing": {
                "en": "Your service is being processed and will be activated shortly.",
                "fr": "Votre service est en cours de traitement et sera activé sous peu.",
            },
            "offshore_community_welcome": {
                "en": "🌊 Welcome to the Nomadly offshore community!\nResilience • Discretion • Independence",
                "fr": "🌊 Bienvenue dans la communauté offshore Nomadly!\nRésilience • Discrétion • Indépendance",
            },
            "support_contact": {
                "en": "📞 Support: @nomadlysupport\n💬 Community: @NomadlyHQ",
                "fr": "📞 Support: @nomadlysupport\n💬 Communauté: @NomadlyHQ",
            },
            "domain_registration_subject": {
                "en": "Domain Registration Successful - Nomadly2",
                "fr": "Enregistrement de Domaine Réussi - Nomadly2",
            },
            "domain_registration_title": {
                "en": "🌐 DOMAIN REGISTRATION SUCCESSFUL\nNomadly2 Offshore Services",
                "fr": "🌐 ENREGISTREMENT DE DOMAINE RÉUSSI\nServices Offshore Nomadly2",
            },
            "domain_details": {"en": "Domain Details", "fr": "Détails du Domaine"},
            "domain_name": {"en": "Domain Name", "fr": "Nom de Domaine"},
            "registration_status": {
                "en": "Registration Status",
                "fr": "Statut d'Enregistrement",
            },
            "active": {"en": "Active", "fr": "Actif"},
            "expiry_date": {"en": "Expiry Date", "fr": "Date d'Expiration"},
            "nameservers": {"en": "Nameservers", "fr": "Serveurs de Noms"},
            "dns_configuration": {"en": "DNS Configuration", "fr": "Configuration DNS"},
            "dns_configured": {
                "en": "DNS has been configured with Cloudflare for optimal performance.",
                "fr": "Le DNS a été configuré avec Cloudflare pour des performances optimales.",
            },
            "domain_management_instructions": {
                "en": "You can manage your domain through the bot using /start → My Domains",
                "fr": "Vous pouvez gérer votre domaine via le bot en utilisant /start → Mes Domaines",
            },
            "offshore_privacy_notice": {
                "en": "🔒 Privacy Notice: Anonymous contact information has been used for maximum discretion.",
                "fr": "🔒 Notice de Confidentialité: Des informations de contact anonymes ont été utilisées pour une discrétion maximale.",
            },
        }

        session = self.db.get_session()
        try:
            for key, translations in default_translations.items():
                for lang_code, text in translations.items():
                    # Check if translation already exists
                    existing = (
                        session.query(Translation)
                        .filter(
                            Translation.key == key,
                            Translation.language_code == lang_code,
                        )
                        .first()
                    )

                    if not existing:
                        translation = Translation(
                            key=key, language_code=lang_code, translation_text=text
                        )
                        session.add(translation)

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error loading translations: {e}")
        finally:
            session.close()


# Global translation service
translation_service = None


def get_translation_service() -> TranslationService:
    """Get global translation service instance"""
    global translation_service
    if translation_service is None:
        translation_service = TranslationService()
    return translation_service


def get_text(key: str, language_code: str = "en", **kwargs) -> str:
    """Convenience function to get translated text"""
    return get_translation_service().get_text(key, language_code, **kwargs)


def get_user_language(telegram_id: int) -> str:
    """Convenience function to get user language"""
    return get_translation_service().get_user_language(telegram_id)


def get_translations() -> TranslationService:
    """Get translations service (alias for compatibility)"""
    return get_translation_service()
