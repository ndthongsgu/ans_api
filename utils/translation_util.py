import json
from urllib.parse import quote
from urllib.request import urlopen


class TranslationService:
    """Simple online translator with safe fallback to original text."""

    def __init__(self):
        self._cache: dict[tuple[str, str, str], str] = {}

    def translate_text(self, text: str | None, source_lang: str, target_lang: str) -> str | None:
        if text is None:
            return None

        value = text.strip()
        if not value:
            return text

        src = source_lang.strip().lower()
        dst = target_lang.strip().lower()
        if src == dst:
            return text

        key = (value, src, dst)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        translated = self._translate_with_mymemory(value, src, dst)
        if not translated:
            translated = text

        self._cache[key] = translated
        return translated

    def _translate_with_mymemory(self, text: str, source_lang: str, target_lang: str) -> str | None:
        url = (
            "https://api.mymemory.translated.net/get"
            f"?q={quote(text)}&langpair={quote(source_lang)}|{quote(target_lang)}"
        )

        try:
            with urlopen(url, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return None

        response_data = payload.get("responseData") or {}
        translated = response_data.get("translatedText")
        if isinstance(translated, str) and translated.strip():
            return translated
        return None
