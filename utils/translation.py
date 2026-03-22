"""
Translation utility for multilingual content
Supports translating text from Vietnamese to other languages
"""

from typing import Dict
from deep_translator import GoogleTranslator
import logging
import time
from functools import lru_cache
from common.enums.language import LanguageCode

logger = logging.getLogger(__name__)


def _normalize_lang_code(lang_code: str) -> str:
    return LanguageCode.get_translation_code(lang_code)


def get_translation_language_code(language_code: str) -> str:
    return LanguageCode.get_translation_code(language_code)


def get_tts_language_code(language_code: str) -> str:
    return LanguageCode.get_tts_code(language_code)


# ==============================
# CORE TRANSLATION
# ==============================

@lru_cache(maxsize=1000)
def _cached_translate(text: str, source: str, target: str) -> str:
    """
    Cache layer to reduce duplicate API calls
    """
    translator = GoogleTranslator(source=source, target=target)
    return translator.translate(text)


def translate_text(
    text: str,
    source_lang: str = "vi",
    target_lang: str = "en",
    retries: int = 3
) -> str:
    """
    Translate text with retry + cache
    """

    if not text or not text.strip():
        return text

    if source_lang.lower() == target_lang.lower():
        return text

    source = _normalize_lang_code(source_lang)
    target = _normalize_lang_code(target_lang)

    logger.info(f"[TRANSLATE] {source} → {target}: {text[:50]}...")

    for attempt in range(retries):
        try:
            time.sleep(0.1)  # tránh rate limit

            translated = _cached_translate(text, source, target)

            if translated:
                return translated

        except Exception as e:
            logger.warning(
                f"[Retry {attempt+1}/{retries}] Failed {target}: {e}"
            )
            time.sleep(0.3)

    logger.error(f"[FAILED] Translation failed for {target}")
    return text  # fallback


# ==============================
# MULTI LANGUAGE
# ==============================

def translate_to_multiple_languages(
    text: str,
    target_languages: list[str],
    source_lang: str = "vi"
) -> Dict[str, str]:
    """
    Translate text to multiple languages
    """

    logger.info(f"[MULTI] {source_lang} → {target_languages}")

    result = {source_lang: text}

    for lang in target_languages:
        lang = lang.lower()

        if lang == source_lang.lower():
            result[lang] = text
            continue

        translated = translate_text(text, source_lang, lang)

        if translated == text:
            logger.warning(f"[FALLBACK] {lang} returned original text")

        result[lang] = translated

    logger.info(f"[DONE] Languages: {list(result.keys())}")
    return result