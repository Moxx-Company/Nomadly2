"""
Translation Helper for Nomadly2 Bot
Provides easy access to translation service throughout the application
"""

from translations import get_translation_service, TranslationService
from database import get_db_manager

# Global translation service
_translation_service = None


def get_t() -> TranslationService:
    """Get global translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = get_translation_service()
    return _translation_service


def t(key: str, telegram_id: int = None, language_code: str = "en", **kwargs) -> str:
    """
    Quick translation function for use throughout the application

    Args:
        key: Translation key
        telegram_id: User's Telegram ID (for language detection)
        language_code: Default language code if user not found
        **kwargs: Parameters for string formatting

    Returns:
        Translated text
    """
    service = get_t()

    # If telegram_id provided, get user's language preference
    if telegram_id:
        try:
            user_language = service.get_user_language(telegram_id)
            language_code = user_language or language_code
        except:
            pass

    return service.get_text(key, language_code, **kwargs)


def get_user_language(telegram_id: int) -> str:
    """Get user's preferred language"""
    service = get_t()
    return service.get_user_language(telegram_id)


# Convenience functions for common use cases
def t_en(key: str, **kwargs) -> str:
    """Get English translation"""
    return t(key, language_code="en", **kwargs)


def t_fr(key: str, **kwargs) -> str:
    """Get French translation"""
    return t(key, language_code="fr", **kwargs)


def t_user(key: str, telegram_id: int, **kwargs) -> str:
    """Get translation in user's preferred language"""
    return t(key, telegram_id=telegram_id, **kwargs)
