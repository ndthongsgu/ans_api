class LanguageCode:
    # Default language for fallback
    DEFAULT = "vi"
    
    # List of all supported languages
    LIST = [
        {
            "code": "vi",
            "label": "Tiếng Việt"
        },
        {
            "code": "en",
            "label": "English"
        },
        {
            "code": "zh",
            "label": "中文"
        },
        {
            "code": "ja",
            "label": "日本語"
        },
        {
            "code": "ko",
            "label": "한국어"
        }
    ]
    
    # Mapping for translation service (Google Translate)
    TRANSLATION_CODE_MAPPINGS = {
        "vi": "vi",
        "en": "en",
        "zh": "zh-CN",   
        "ja": "ja",
        "ko": "ko",
    }
    
    # Mapping for TTS service (Google Text-to-Speech)
    TTS_CODE_MAPPINGS = {
        "vi": "vi",
        "en": "en",
        "zh": "zh-CN",
        "ja": "ja",
        "ko": "ko",
    }
    
    @classmethod
    def get_codes(cls) -> list[str]:
        """Get list of all language codes"""
        return [lang["code"] for lang in cls.LIST]
    
    @classmethod
    def get_translation_code(cls, language_code: str) -> str:
        """Get translation service language code"""
        return cls.TRANSLATION_CODE_MAPPINGS.get(language_code.lower(), language_code)
    
    @classmethod
    def get_tts_code(cls, language_code: str) -> str:
        """Get TTS service language code"""
        return cls.TTS_CODE_MAPPINGS.get(language_code.lower(), language_code)
