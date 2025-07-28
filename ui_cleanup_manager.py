"""
UI Cleanup Manager for Nomadly3 Bot
Handles clean message management and prevents Telegram API errors
"""

import logging
from typing import Dict, Any, Optional, Union
from telegram import Update, Message, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class UICleanupManager:
    """Manages clean UI by handling message updates and preventing duplicates"""
    
    def __init__(self):
        self.message_cache: Dict[int, Dict[str, Any]] = {}  # user_id -> message_data
        self.last_message_ids: Dict[int, int] = {}  # user_id -> last_message_id
        
    async def safe_edit_message(self, query, new_text: str, reply_markup: Optional[InlineKeyboardMarkup] = None) -> bool:
        """Safely edit a message, avoiding Telegram API errors"""
        try:
            user_id = query.from_user.id if query.from_user else 0
            message_id = query.message.message_id if query.message else 0
            
            # Special handling for navigation callbacks - always allow them to proceed
            navigation_callbacks = [
                'main_menu', 'my_domains', 'search_domain', 'change_language',
                'show_languages', 'wallet', 'support_menu', 'dns_tools_menu',
                'back_to_main', 'back_to_domains', 'back_to_search'
            ]
            
            # Also handle callbacks that start with navigation patterns
            navigation_patterns = [
                'back_', 'return_', 'cancel_', 'menu_', 'nav_'
            ]
            
            is_navigation = False
            if hasattr(query, 'data') and query.data:
                # Direct navigation callbacks
                is_navigation = query.data in navigation_callbacks
                # Pattern-based navigation callbacks
                if not is_navigation:
                    is_navigation = any(query.data.startswith(pattern) for pattern in navigation_patterns)
            
            # Check if content is identical to avoid "Message is not modified" error (but skip for navigation)
            cached_content = self.message_cache.get(user_id, {}).get('text', '')
            if cached_content == new_text and not is_navigation:
                logger.info(f"Skipping identical message edit for user {user_id}")
                await query.answer("Already up to date")
                return True
            
            # Try to edit the message
            await query.edit_message_text(
                text=new_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            # Cache the successful edit
            self.message_cache[user_id] = {
                'text': new_text,
                'message_id': message_id,
                'markup': reply_markup
            }
            
            logger.info(f"Successfully edited message for user {user_id}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            
            if "Message is not modified" in error_msg:
                logger.info(f"Message content unchanged for user {query.from_user.id if query.from_user else 0}")
                await query.answer("Already up to date")
                return True
                
            elif "Query is too old" in error_msg:
                logger.warning(f"Query too old for user {query.from_user.id if query.from_user else 0}, sending new message")
                return await self.send_fresh_message(query, new_text, reply_markup)
                
            else:
                logger.error(f"Message edit error for user {query.from_user.id if query.from_user else 0}: {e}")
                return await self.send_fresh_message(query, new_text, reply_markup)
    
    async def send_fresh_message(self, query, text: str, reply_markup: Optional[InlineKeyboardMarkup] = None) -> bool:
        """Send a fresh message when editing fails"""
        try:
            user_id = query.from_user.id if query.from_user else 0
            
            # Answer the callback query first
            await query.answer()
            
            # Send new message
            new_message = await query.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            # Cache the new message
            self.message_cache[user_id] = {
                'text': text,
                'message_id': new_message.message_id,
                'markup': reply_markup
            }
            self.last_message_ids[user_id] = new_message.message_id
            
            logger.info(f"Sent fresh message to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send fresh message to user {query.from_user.id if query.from_user else 0}: {e}")
            return False
    
    async def clean_old_messages(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, keep_last: int = 3):
        """Clean up old messages to keep UI tidy (optional feature)"""
        try:
            # This would require message tracking - implement if needed
            # For now, we rely on Telegram's built-in message management
            pass
        except Exception as e:
            logger.error(f"Error cleaning messages for user {user_id}: {e}")
    
    def clear_user_cache(self, user_id: int):
        """Clear cached data for a user"""
        if user_id in self.message_cache:
            del self.message_cache[user_id]
        if user_id in self.last_message_ids:
            del self.last_message_ids[user_id]
        logger.info(f"Cleared cache for user {user_id}")
    
    async def handle_callback_error(self, query, error: Exception) -> bool:
        """Handle callback query errors gracefully"""
        try:
            error_msg = str(error)
            user_id = query.from_user.id if query.from_user else 0
            
            if "Query is too old" in error_msg:
                # Send fresh message for old queries
                await query.message.reply_text("🔄 Session refreshed - please try again.")
                self.clear_user_cache(user_id)
                return True
                
            elif "Message is not modified" in error_msg:
                # Just answer the query
                await query.answer("Already up to date")
                return True
                
            else:
                # Generic error handling
                await query.answer("⚠️ Please try again")
                await query.message.reply_text("🚧 Service temporarily unavailable. Please use /start to refresh.")
                return True
                
        except Exception as inner_e:
            logger.error(f"Error in callback error handler: {inner_e}")
            return False

# Global instance
ui_cleanup = UICleanupManager()