#!/usr/bin/env python3
"""
User-Friendly Messaging System
Enhanced messaging with welcoming language and clear guidance
"""

class UserFriendlyMessages:
    """Friendly, helpful messages for the bot"""
    
    @staticmethod
    def welcome_message(first_name: str = "") -> str:
        """Warm welcome message"""
        name_part = f" {first_name}" if first_name else ""
        return f"""🌊 Welcome to Nomadly2{name_part}!

Your secure offshore domain registration partner. We're here to help you establish your digital presence with complete privacy and discretion.

🏴‍☠️ What we offer:
• Anonymous domain registration
• Cryptocurrency payments only
• Complete DNS management
• 24/7 offshore hosting support

How would you like to begin your journey?"""

    @staticmethod
    def help_message() -> str:
        """Comprehensive help message"""
        return """🛟 **How can we help you?**

**🔍 Domain Registration:**
• Search and register domains anonymously
• Privacy-focused contact generation
• Cryptocurrency payments (ETH, BTC, USDT)
• Instant DNS setup

**🌐 DNS Management:**
• Complete DNS record management
• Custom nameserver support
• Cloudflare integration
• Real-time propagation

**💰 Wallet & Payments:**
• Secure cryptocurrency wallet
• Multiple payment options
• Loyalty rewards program
• Transaction history

**⚙️ Settings & Support:**
• Bilingual support (English/French)
• 24/7 customer support
• Account management
• Domain portfolio

**Need immediate assistance?** Just type your question or use the menu buttons below. We're here to help every step of the way!"""

    @staticmethod
    def domain_search_guide() -> str:
        """Domain search guidance"""
        return """🔍 **Domain Search Guide**

Please enter the domain name you'd like to register:

**Examples:**
• mycompany.com
• secure-site.org  
• offshore-business.net

**Tips for better results:**
• Use only letters, numbers, and hyphens
• Domain must end with a valid extension (.com, .org, etc.)
• We'll show you available alternatives if your first choice isn't available

**What happens next?**
1. We'll check availability instantly
2. Show you pricing and options
3. Guide you through secure registration
4. Set up DNS automatically

Ready to find your perfect domain?"""

    @staticmethod
    def payment_explanation() -> str:
        """Payment process explanation"""
        return """💰 **Secure Payment Process**

We only accept cryptocurrency payments for maximum privacy:

**Supported Currencies:**
• Ethereum (ETH) - Recommended
• Bitcoin (BTC) - Most secure  
• USDT - Stable value
• Litecoin (LTC)
• Dogecoin (DOGE)
• Tron (TRX)

**How it works:**
1. We generate a unique payment address
2. Send exact amount within 30 minutes
3. Payment confirms automatically
4. Domain registers immediately

**Why cryptocurrency only?**
• Complete anonymity
• No chargebacks or reversals
• Offshore compliance
• Instant global payments

Your payment is 100% secure and anonymous."""

    @staticmethod
    def dns_management_intro() -> str:
        """DNS management introduction"""  
        return """🌐 **DNS Management Made Simple**

Take full control of your domain's DNS settings:

**What you can do:**
• Create A, CNAME, MX, TXT records
• Set up email forwarding
• Configure subdomains
• Manage nameservers

**Getting Started:**
1. Select your domain from the list
2. Choose the DNS record type
3. Enter the required information
4. Changes propagate within minutes

**Need help?**
Each record type includes helpful examples and guidance. Our system validates your entries and suggests corrections for common mistakes.

**Pro tip:** Changes may take up to 48 hours to propagate globally, but most resolve within minutes."""

    @staticmethod
    def nameserver_switch_guide() -> str:
        """Nameserver switching guidance"""
        return """🔄 **Nameserver Management**

Choose how you want to manage your domain's DNS:

**🌟 Cloudflare DNS (Recommended)**
• Fast global network
• Advanced security features
• Easy DNS record management
• Free SSL certificates

**🏢 Default Nameservers**
• Basic DNS functionality
• Stable and reliable
• Limited customization

**🛠️ Custom Nameservers**
• Use your own DNS provider
• Full control and flexibility
• Requires technical knowledge

**Important:** Nameserver changes can take 24-48 hours to propagate globally. During this time, your website may be intermittently unavailable.

Which option would you prefer?"""

    @staticmethod
    def error_recovery_message(action: str) -> str:
        """User-friendly error recovery"""
        return f"""🔧 **Oops! Something went wrong**

We encountered an issue while {action}. Don't worry - this happens sometimes!

**What you can try:**
• Wait a moment and try again
• Check your internet connection  
• Refresh and restart the action
• Contact our support team

**Your data is safe:**
• No payments have been lost
• Your domains are secure
• All settings are preserved

**Need immediate help?**
Our support team is standing by 24/7 to assist you. Just click the Support button below.

We apologize for any inconvenience and appreciate your patience!"""

    @staticmethod
    def success_celebration(action: str, details: str = "") -> str:
        """Celebrate successful actions"""
        celebrations = {
            'domain_registration': '🎉 **Domain Registration Successful!**',
            'payment_received': '💰 **Payment Received Successfully!**',
            'dns_updated': '🌐 **DNS Updated Successfully!**',
            'nameservers_changed': '🔄 **Nameservers Updated!**'
        }
        
        title = celebrations.get(action, f'✅ **{action.replace("_", " ").title()} Completed!**')
        
        message = f"""{title}

{details}

**What's next?**
• Your changes are processing
• You'll receive confirmation shortly
• Need to make more changes? Just ask!

Thank you for choosing Nomadly2 for your offshore hosting needs!"""
        
        return message

    @staticmethod
    def progress_update(step: str, total_steps: int, current_step: int) -> str:
        """Progress update with encouragement"""
        progress_bar = "█" * current_step + "░" * (total_steps - current_step)
        percentage = int((current_step / total_steps) * 100)
        
        return f"""⚡ **Processing Your Request**

Step {current_step}/{total_steps}: {step}

[{progress_bar}] {percentage}%

**Almost there!** We're working hard to complete your request. This usually takes just a few moments.

Thank you for your patience!"""

    @staticmethod
    def confirmation_request(action: str, details: str, warning: str = "") -> str:
        """Request confirmation with clear details"""
        message = f"""🤔 **Please Confirm Your Action**

**Action:** {action.replace('_', ' ').title()}

**Details:**
{details}"""
        
        if warning:
            message += f"""

⚠️ **Important Notice:**
{warning}"""
        
        message += """

**Are you sure you want to proceed?**
This action will be processed immediately after confirmation."""
        
        return message

    @staticmethod
    def get_friendly_error_message(error_type: str) -> str:
        """Get user-friendly error messages"""
        friendly_errors = {
            'domain_unavailable': "😔 Unfortunately, that domain is already taken. But don't worry! We'll show you some great alternatives.",
            'payment_timeout': "⏰ Payment time expired, but no worries! You can create a new payment anytime. Your domain reservation is still secure.",
            'dns_error': "🔧 DNS update encountered a temporary issue. These usually resolve quickly - please try again in a moment.",
            'validation_failed': "📝 We noticed a small issue with the information provided. Let's fix that together!",
            'api_timeout': "🌐 Our servers are taking a bit longer than usual. Thank you for your patience while we process your request.",
            'insufficient_balance': "💳 Your wallet needs a bit more funds for this purchase. You can easily add more cryptocurrency anytime!",
            'invalid_nameserver': "🌐 The nameserver format looks unusual. Let us help you correct it!",
        }
        
        return friendly_errors.get(error_type, "🤔 Something unexpected happened, but we're here to help you resolve it!")

    @staticmethod
    def get_supportive_suggestions(context: str) -> list:
        """Get supportive suggestions based on context"""
        suggestions = {
            'domain_search': [
                "💡 Try different extensions like .org, .net, or .info",
                "💡 Add numbers or hyphens to your preferred name",
                "💡 Consider abbreviations or alternative spellings",
                "💡 Browse our suggested alternatives below"
            ],
            'payment_issues': [
                "💡 Check if you sent the exact amount shown",
                "💡 Verify the payment address is correct", 
                "💡 Contact support if payment was sent correctly",
                "💡 Create a new payment if the old one expired"
            ],
            'dns_problems': [
                "💡 Check your record format matches the examples",
                "💡 Verify IP addresses are valid",
                "💡 Wait a few minutes for changes to process",
                "💡 Contact support for complex DNS setups"
            ],
            'general_help': [
                "💡 Use the menu buttons for quick navigation",
                "💡 Type 'help' anytime for assistance",
                "💡 Check our FAQ for common questions",
                "💡 Contact support for personal assistance"
            ]
        }
        
        return suggestions.get(context, suggestions['general_help'])

if __name__ == "__main__":
    # Test the messaging system
    msg = UserFriendlyMessages()
    print("Welcome Message:")
    print(msg.welcome_message("John"))
    print("\nHelp Message:")  
    print(msg.help_message())
    print("\nError Message:")
    print(msg.get_friendly_error_message("domain_unavailable"))