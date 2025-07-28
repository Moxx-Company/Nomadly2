"""
Type stub file for Nomadly2 Bot - Helps LSP understand our types
"""

from typing import Optional, Dict, Any, List, Union
from sqlalchemy.orm import DeclarativeBase
from telegram import Update, Message, CallbackQuery, User as TelegramUser
from telegram.ext import ContextTypes

# Database Types
class DatabaseManager:
    def get_user(self, telegram_id: int) -> Optional["User"]: ...
    def get_user_domains(self, telegram_id: int) -> List["RegisteredDomain"]: ...
    def create_user(self, telegram_id: int, **kwargs) -> "User": ...
    def get_or_create_user(self, telegram_id: int, **kwargs) -> "User": ...

class User:
    id: int
    telegram_id: int
    language_code: str
    balance_usd: float
    technical_email: Optional[str]
    created_at: Any
    updated_at: Any

class RegisteredDomain:
    id: int
    user_id: int
    domain_name: str
    openprovider_domain_id: Optional[str]
    cloudflare_zone_id: Optional[str]
    registration_status: str
    dns_status: str

# Bot Types
class Nomadly2Bot:
    application: Any
    def show_main_menu_simple(self, message: Message, user: Optional[User]) -> None: ...

# DNS System Types  
class CompleteDNSSystem:
    def show_dns_hub(self, query: CallbackQuery, domain_name: str) -> None: ...
    def show_dns_management_hub(self, query: CallbackQuery) -> None: ...
