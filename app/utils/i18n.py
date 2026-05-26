"""
Internationalization utilities for bilingual support.
"""
import json
from pathlib import Path
from typing import Any, Optional

# Supported languages
SUPPORTED_LANGUAGES = ["pt", "en"]
DEFAULT_LANGUAGE = "pt"

# Cache for translation files
_translations_cache = {}


def load_translations(lang: str) -> dict:
    """
    Load translation JSON file for the given language.
    Results are cached to avoid repeated file reads.
    
    Args:
        lang: Language code ('pt' or 'en')
    
    Returns:
        Dictionary of translation keys and values
    """
    if lang not in _translations_cache:
        translations_dir = Path(__file__).parent.parent / "translations"
        file_path = translations_dir / f"{lang}.json"
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                _translations_cache[lang] = json.load(f)
        else:
            _translations_cache[lang] = {}
    
    return _translations_cache[lang]


def get_translation(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Get translated string for a given key and language.
    
    Args:
        key: Translation key (e.g., 'nav.home')
        lang: Language code ('pt' or 'en')
    
    Returns:
        Translated string, or the key itself if not found
    """
    translations = load_translations(lang)
    
    # Support nested keys like 'nav.home'
    keys = key.split(".")
    value = translations
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return key  # Return key if translation not found
    
    return value if isinstance(value, str) else key


def get_translated_field(obj: Any, field_base: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Get translated database field value with fallback logic.
    
    Fallback order:
    1. Requested language (e.g., field_pt or field_en)
    2. Portuguese (field_pt)
    3. English (field_en)
    4. Empty string
    
    Args:
        obj: Database model instance
        field_base: Base field name without language suffix (e.g., 'name', 'description')
        lang: Requested language code ('pt' or 'en')
    
    Returns:
        Translated field value with fallback
    """
    # Try requested language
    field_name = f"{field_base}_{lang}"
    value = getattr(obj, field_name, None)
    if value:
        return value
    
    # Fallback to Portuguese
    if lang != "pt":
        field_name = f"{field_base}_pt"
        value = getattr(obj, field_name, None)
        if value:
            return value
    
    # Fallback to English
    if lang != "en":
        field_name = f"{field_base}_en"
        value = getattr(obj, field_name, None)
        if value:
            return value
    
    # Return empty string if nothing found
    return ""


def validate_language(lang: Optional[str]) -> str:
    """
    Validate and return a supported language code.
    
    Args:
        lang: Language code to validate
    
    Returns:
        Valid language code, defaults to DEFAULT_LANGUAGE if invalid
    """
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang
    return DEFAULT_LANGUAGE
