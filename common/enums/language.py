class LanguageCode:
    LIST = [
        {
            "code": "vi",
            "label": "Tiếng Việt"
        },
        {
            "code": "en",
            "label": "Tiếng Anh"
        },
        {
            "code": "zh",
            "label": "Tiếng Trung"
        },
        {
            "code": "ja",
            "label": "Tiếng Nhật"
        },
        {
            "code": "ko",
            "label": "Tiếng Hàn"
        }
    ]

    @classmethod
    def codes(cls) -> list[str]:
        return [item["code"] for item in cls.LIST]

    @classmethod
    def is_supported(cls, code: str | None) -> bool:
        if not code:
            return False
        return code.strip().lower() in cls.codes()
