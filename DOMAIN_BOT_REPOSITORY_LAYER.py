"""
Repository Layer for Telegram Domain Bot
Data Access Layer with Business Logic Abstraction
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc, func, text
from datetime import datetime, timedelta
from decimal import Decimal
import logging
import json

from DOMAIN_BOT_DATABASE_MODELS import (
    User,
    UserState,
    RegisteredDomain,
    DNSRecord,
    WalletTransaction,
    OpenProviderContact,
    AdminNotification,
    Translation,
    SystemSetting,
    APIUsageLog,
)

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository with common database operations"""

    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        """Commit current transaction"""
        try:
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database commit error: {e}")
            raise

    def rollback(self):
        """Rollback current transaction"""
        self.session.rollback()


class UserRepository(BaseRepository):
    """User data access layer"""

    def create_user(
        self,
        telegram_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        language_code: str = "en",
    ) -> User:
        """Create new user"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
        self.session.add(user)
        self.commit()
        return user

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        return self.session.query(User).filter(User.telegram_id == telegram_id).first()

    def get_or_create_user(self, telegram_id: int, **kwargs) -> Tuple[User, bool]:
        """Get existing user or create new one"""
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            # Update last activity
            user.last_activity = datetime.utcnow()
            self.commit()
            return user, False
        else:
            user = self.create_user(telegram_id, **kwargs)
            return user, True

    def update_user_language(self, telegram_id: int, language_code: str) -> bool:
        """Update user's language preference"""
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            user.language_code = language_code
            user.updated_at = datetime.utcnow()
            self.commit()
            return True
        return False

    def update_user_balance(self, telegram_id: int, new_balance: Decimal) -> bool:
        """Update user's wallet balance"""
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            user.wallet_balance = float(new_balance)
            user.updated_at = datetime.utcnow()
            self.commit()
            return True
        return False

    def get_user_balance(self, telegram_id: int) -> Decimal:
        """Get user's current balance"""
        user = self.get_user_by_telegram_id(telegram_id)
        return user.get_balance() if user else Decimal("0.00")

    def get_users_by_language(self, language_code: str) -> List[User]:
        """Get all users with specific language"""
        return (
            self.session.query(User)
            .filter(and_(User.language_code == language_code, User.is_active == True))
            .all()
        )

    def get_active_users_count(self) -> int:
        """Get count of active users"""
        return self.session.query(User).filter(User.is_active == True).count()

    def deactivate_user(self, telegram_id: int) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_telegram_id(telegram_id)
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
            self.commit()
            return True
        return False


class UserStateRepository(BaseRepository):
    """User state management for conversations"""

    def set_user_state(
        self,
        telegram_id: int,
        state_name: str,
        state_data: Dict[str, Any] = None,
        expires_in_minutes: int = 60,
    ) -> UserState:
        """Set user state with optional expiration"""
        # Clear existing state
        self.clear_user_state(telegram_id)

        expiry_date = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        user_state = UserState(
            telegram_id=telegram_id,
            state_name=state_name,
            state_data=state_data or {},
            expiry_date=expiry_date,
        )
        self.session.add(user_state)
        self.commit()
        return user_state

    def get_user_state(self, telegram_id: int) -> Optional[UserState]:
        """Get current user state"""
        state = (
            self.session.query(UserState)
            .filter(UserState.telegram_id == telegram_id)
            .first()
        )

        if state and state.is_expired():
            self.clear_user_state(telegram_id)
            return None

        return state

    def update_state_data(self, telegram_id: int, key: str, value: Any) -> bool:
        """Update specific state data"""
        state = self.get_user_state(telegram_id)
        if state:
            state.set_data(key, value)
            self.commit()
            return True
        return False

    def clear_user_state(self, telegram_id: int) -> bool:
        """Clear user state"""
        deleted = (
            self.session.query(UserState)
            .filter(UserState.telegram_id == telegram_id)
            .delete()
        )
        self.commit()
        return deleted > 0

    def cleanup_expired_states(self) -> int:
        """Cleanup expired states"""
        deleted = (
            self.session.query(UserState)
            .filter(UserState.expiry_date < datetime.utcnow())
            .delete()
        )
        self.commit()
        return deleted


class DomainRepository(BaseRepository):
    """Domain registration and management"""

    def create_domain(
        self,
        telegram_id: int,
        domain_name: str,
        tld: str,
        price_paid: Decimal,
        payment_method: str,
        openprovider_domain_id: str = None,
        cloudflare_zone_id: str = None,
        nameserver_mode: str = "cloudflare",
        nameservers: List[str] = None,
    ) -> RegisteredDomain:
        """Create new domain registration"""
        domain = RegisteredDomain(
            telegram_id=telegram_id,
            domain_name=domain_name,
            tld=tld,
            price_paid=float(price_paid),
            payment_method=payment_method,
            openprovider_domain_id=openprovider_domain_id,
            cloudflare_zone_id=cloudflare_zone_id,
            nameserver_mode=nameserver_mode,
            nameservers=nameservers or [],
            expiry_date=datetime.utcnow() + timedelta(days=365),  # 1 year
        )
        self.session.add(domain)
        self.commit()
        return domain

    def get_user_domains(
        self, telegram_id: int, active_only: bool = True
    ) -> List[RegisteredDomain]:
        """Get user's domains"""
        query = self.session.query(RegisteredDomain).filter(
            RegisteredDomain.telegram_id == telegram_id
        )

        if active_only:
            query = query.filter(RegisteredDomain.status == "active")

        return query.order_by(desc(RegisteredDomain.created_at)).all()

    def get_domain_by_id(self, domain_id: int) -> Optional[RegisteredDomain]:
        """Get domain by ID"""
        return (
            self.session.query(RegisteredDomain)
            .filter(RegisteredDomain.id == domain_id)
            .first()
        )

    def get_domain_by_name(
        self, domain_name: str, tld: str
    ) -> Optional[RegisteredDomain]:
        """Get domain by name and TLD"""
        return (
            self.session.query(RegisteredDomain)
            .filter(
                and_(
                    RegisteredDomain.domain_name == domain_name,
                    RegisteredDomain.tld == tld,
                )
            )
            .first()
        )

    def update_domain_nameservers(
        self, domain_id: int, nameservers: List[str], nameserver_mode: str = None
    ) -> bool:
        """Update domain nameservers"""
        domain = self.get_domain_by_id(domain_id)
        if domain:
            domain.set_nameservers(nameservers)
            if nameserver_mode:
                domain.nameserver_mode = nameserver_mode
            self.commit()
            return True
        return False

    def update_domain_status(self, domain_id: int, status: str) -> bool:
        """Update domain status"""
        domain = self.get_domain_by_id(domain_id)
        if domain:
            domain.status = status
            domain.updated_at = datetime.utcnow()
            self.commit()
            return True
        return False

    def get_expiring_domains(self, days_ahead: int = 30) -> List[RegisteredDomain]:
        """Get domains expiring within specified days"""
        expiry_threshold = datetime.utcnow() + timedelta(days=days_ahead)
        return (
            self.session.query(RegisteredDomain)
            .filter(
                and_(
                    RegisteredDomain.expires_at <= expiry_threshold,
                    RegisteredDomain.status == "active",
                )
            )
            .all()
        )

    def get_domain_statistics(self) -> Dict[str, Any]:
        """Get domain registration statistics"""
        total_domains = self.session.query(RegisteredDomain).count()
        active_domains = (
            self.session.query(RegisteredDomain)
            .filter(RegisteredDomain.status == "active")
            .count()
        )

        # Top TLDs
        tld_stats = (
            self.session.query(
                RegisteredDomain.tld, func.count(RegisteredDomain.id).label("count")
            )
            .group_by(RegisteredDomain.tld)
            .order_by(desc("count"))
            .limit(10)
            .all()
        )

        return {
            "total_domains": total_domains,
            "active_domains": active_domains,
            "top_tlds": [{"tld": tld, "count": count} for tld, count in tld_stats],
        }


class DNSRepository(BaseRepository):
    """DNS record management"""

    def create_dns_record(
        self,
        domain_id: int,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 3600,
        priority: int = None,
        proxied: bool = False,
        cloudflare_record_id: str = None,
    ) -> DNSRecord:
        """Create DNS record"""
        record = DNSRecord(
            domain_id=domain_id,
            record_type=record_type.upper(),
            name=name,
            content=content,
            ttl=ttl,
            priority=priority,
            proxied=proxied,
            cloudflare_record_id=cloudflare_record_id,
        )
        self.session.add(record)
        self.commit()
        return record

    def get_domain_dns_records(
        self, domain_id: int, record_type: str = None
    ) -> List[DNSRecord]:
        """Get DNS records for domain"""
        query = self.session.query(DNSRecord).filter(DNSRecord.domain_id == domain_id)

        if record_type:
            query = query.filter(DNSRecord.record_type == record_type.upper())

        return query.order_by(DNSRecord.record_type, DNSRecord.name).all()

    def get_dns_record_by_id(self, record_id: int) -> Optional[DNSRecord]:
        """Get DNS record by ID"""
        return self.session.query(DNSRecord).filter(DNSRecord.id == record_id).first()

    def update_dns_record(
        self,
        record_id: int,
        content: str = None,
        ttl: int = None,
        priority: int = None,
        proxied: bool = None,
    ) -> bool:
        """Update DNS record"""
        record = self.get_dns_record_by_id(record_id)
        if record:
            if content is not None:
                record.content = content
            if ttl is not None:
                record.ttl = ttl
            if priority is not None:
                record.priority = priority
            if proxied is not None:
                record.proxied = proxied

            record.updated_at = datetime.utcnow()
            self.commit()
            return True
        return False

    def delete_dns_record(self, record_id: int) -> bool:
        """Delete DNS record"""
        deleted = (
            self.session.query(DNSRecord).filter(DNSRecord.id == record_id).delete()
        )
        self.commit()
        return deleted > 0

    def get_dns_records_by_cloudflare_id(
        self, cloudflare_record_id: str
    ) -> Optional[DNSRecord]:
        """Get DNS record by Cloudflare record ID"""
        return (
            self.session.query(DNSRecord)
            .filter(DNSRecord.cloudflare_record_id == cloudflare_record_id)
            .first()
        )


class WalletRepository(BaseRepository):
    """Wallet and transaction management"""

    def create_transaction(
        self,
        telegram_id: int,
        transaction_type: str,
        amount: Decimal,
        description: str = None,
        crypto_currency: str = None,
        crypto_amount: Decimal = None,
        payment_address: str = None,
        blockbee_payment_id: str = None,
    ) -> WalletTransaction:
        """Create wallet transaction"""
        transaction = WalletTransaction(
            telegram_id=telegram_id,
            transaction_type=transaction_type,
            amount=float(amount),
            description=description,
            crypto_currency=crypto_currency,
            crypto_amount=float(crypto_amount) if crypto_amount else None,
            payment_address=payment_address,
            blockbee_payment_id=blockbee_payment_id,
        )
        self.session.add(transaction)
        self.commit()
        return transaction

    def get_user_transactions(
        self, telegram_id: int, transaction_type: str = None, limit: int = 50
    ) -> List[WalletTransaction]:
        """Get user's transaction history"""
        query = self.session.query(WalletTransaction).filter(
            WalletTransaction.telegram_id == telegram_id
        )

        if transaction_type:
            query = query.filter(WalletTransaction.transaction_type == transaction_type)

        return query.order_by(desc(WalletTransaction.created_at)).limit(limit).all()

    def get_transaction_by_id(self, transaction_id: int) -> Optional[WalletTransaction]:
        """Get transaction by ID"""
        return (
            self.session.query(WalletTransaction)
            .filter(WalletTransaction.id == transaction_id)
            .first()
        )

    def get_transaction_by_blockbee_id(
        self, blockbee_payment_id: str
    ) -> Optional[WalletTransaction]:
        """Get transaction by BlockBee payment ID"""
        return (
            self.session.query(WalletTransaction)
            .filter(WalletTransaction.blockbee_payment_id == blockbee_payment_id)
            .first()
        )

    def update_transaction_status(
        self, transaction_id: int, status: str, transaction_hash: str = None
    ) -> bool:
        """Update transaction status"""
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            transaction.status = status
            if transaction_hash:
                transaction.transaction_hash = transaction_hash
            if status == "confirmed":
                transaction.confirmed_at = datetime.utcnow()
            self.commit()
            return True
        return False

    def get_pending_transactions(
        self, older_than_hours: int = 24
    ) -> List[WalletTransaction]:
        """Get pending transactions older than specified hours"""
        threshold = datetime.utcnow() - timedelta(hours=older_than_hours)
        return (
            self.session.query(WalletTransaction)
            .filter(
                and_(
                    WalletTransaction.status == "pending",
                    WalletTransaction.created_at < threshold,
                )
            )
            .all()
        )

    def get_wallet_statistics(self) -> Dict[str, Any]:
        """Get wallet and transaction statistics"""
        total_deposits = (
            self.session.query(func.sum(WalletTransaction.amount))
            .filter(
                and_(
                    WalletTransaction.transaction_type == "deposit",
                    WalletTransaction.status == "confirmed",
                )
            )
            .scalar()
            or 0
        )

        total_payments = (
            self.session.query(func.sum(WalletTransaction.amount))
            .filter(
                and_(
                    WalletTransaction.transaction_type == "payment",
                    WalletTransaction.status == "confirmed",
                )
            )
            .scalar()
            or 0
        )

        # Crypto currency breakdown
        crypto_stats = (
            self.session.query(
                WalletTransaction.crypto_currency,
                func.count(WalletTransaction.id).label("count"),
                func.sum(WalletTransaction.amount).label("total_usd"),
            )
            .filter(
                and_(
                    WalletTransaction.crypto_currency.isnot(None),
                    WalletTransaction.status == "confirmed",
                )
            )
            .group_by(WalletTransaction.crypto_currency)
            .all()
        )

        return {
            "total_deposits": float(total_deposits),
            "total_payments": float(total_payments),
            "crypto_breakdown": [
                {
                    "currency": currency,
                    "transaction_count": count,
                    "total_usd": float(total_usd or 0),
                }
                for currency, count, total_usd in crypto_stats
            ],
        }


class ContactRepository(BaseRepository):
    """OpenProvider contact management"""

    def create_contact(
        self, telegram_id: int, contact_handle: str, contact_data: Dict[str, Any]
    ) -> OpenProviderContact:
        """Create OpenProvider contact"""
        contact = OpenProviderContact(
            telegram_id=telegram_id,
            contact_handle=contact_handle,
            generated_identity=contact_data,
            first_name=contact_data.get("first_name"),
            last_name=contact_data.get("last_name"),
            address_line1=contact_data.get("address_line1"),
            city=contact_data.get("city"),
            state=contact_data.get("state"),
            postal_code=contact_data.get("postal_code"),
            country_code=contact_data.get("country_code", "US"),
            phone=contact_data.get("phone"),
            email=contact_data.get("email"),
            date_of_birth=contact_data.get("date_of_birth"),
            passport_number=contact_data.get("passport_number"),
        )
        self.session.add(contact)
        self.commit()
        return contact

    def get_user_contact(self, telegram_id: int) -> Optional[OpenProviderContact]:
        """Get user's OpenProvider contact"""
        return (
            self.session.query(OpenProviderContact)
            .filter(
                and_(
                    OpenProviderContact.telegram_id == telegram_id,
                    OpenProviderContact.is_active == True,
                )
            )
            .first()
        )

    def get_contact_by_handle(
        self, contact_handle: str
    ) -> Optional[OpenProviderContact]:
        """Get contact by handle"""
        return (
            self.session.query(OpenProviderContact)
            .filter(OpenProviderContact.contact_handle == contact_handle)
            .first()
        )


class TranslationRepository(BaseRepository):
    """Translation and localization management"""

    def get_translation(self, key: str, language_code: str) -> Optional[str]:
        """Get translation for key and language"""
        translation = (
            self.session.query(Translation)
            .filter(
                and_(Translation.key == key, Translation.language_code == language_code)
            )
            .first()
        )
        return translation.translation_text if translation else None

    def add_translation(
        self, key: str, language_code: str, text: str, context: str = None
    ) -> Translation:
        """Add or update translation"""
        translation = (
            self.session.query(Translation)
            .filter(
                and_(Translation.key == key, Translation.language_code == language_code)
            )
            .first()
        )

        if translation:
            translation.translation_text = text
            if context:
                translation.context = context
            translation.updated_at = datetime.utcnow()
        else:
            translation = Translation(
                key=key,
                language_code=language_code,
                translation_text=text,
                context=context,
            )
            self.session.add(translation)

        self.commit()
        return translation

    def get_all_translations(self, language_code: str) -> Dict[str, str]:
        """Get all translations for language"""
        translations = (
            self.session.query(Translation)
            .filter(Translation.language_code == language_code)
            .all()
        )
        return {t.key: t.translation_text for t in translations}


class AdminRepository(BaseRepository):
    """Admin notifications and system management"""

    def create_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        telegram_id: int = None,
        metadata: Dict[str, Any] = None,
        severity: str = "info",
    ) -> AdminNotification:
        """Create admin notification"""
        notification = AdminNotification(
            telegram_id=telegram_id,
            notification_type=notification_type,
            title=title,
            message=message,
            metadata=metadata,
            severity=severity,
        )
        self.session.add(notification)
        self.commit()
        return notification

    def get_recent_notifications(
        self, hours: int = 24, limit: int = 100
    ) -> List[AdminNotification]:
        """Get recent admin notifications"""
        threshold = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.session.query(AdminNotification)
            .filter(AdminNotification.created_at >= threshold)
            .order_by(desc(AdminNotification.created_at))
            .limit(limit)
            .all()
        )

    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        notification = (
            self.session.query(AdminNotification)
            .filter(AdminNotification.id == notification_id)
            .first()
        )
        if notification:
            notification.is_read = True
            self.commit()
            return True
        return False
