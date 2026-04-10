from sqlalchemy.orm import Session
from models.listeningHistory import ListeningHistory
from models.stallTranslation import StallTranslation
from common.enums.language import LanguageCode


class ListeningHistoryMobileService:
    def __init__(self, db: Session):
        self.db = db

    def _normalize_language_code(self, language_code: str | None) -> str:
        if language_code is None:
            return LanguageCode.DEFAULT
        return language_code.strip().lower()

    def _get_stall_translation(self, stall_id: str, language_code: str) -> str | None:
        trans = (
            self.db.query(StallTranslation)
            .filter(
                StallTranslation.stall_id == stall_id,
                StallTranslation.language_code == language_code,
            )
            .first()
        )
        if trans:
            return trans.name

        # fallback to default language
        if language_code != LanguageCode.DEFAULT:
            default_trans = (
                self.db.query(StallTranslation)
                .filter(
                    StallTranslation.stall_id == stall_id,
                    StallTranslation.language_code == LanguageCode.DEFAULT,
                )
                .first()
            )
            if default_trans:
                return default_trans.name
        return None

    def get_user_listening_history(
        self,
        user_id: str,
        page: int = 1,
        size: int = 20,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        language_code: str | None = None,
    ) -> dict:
        if page < 1:
            page = 1
        if size < 1:
            size = 20

        requested_lang = self._normalize_language_code(language_code)

        query = self.db.query(ListeningHistory).filter(ListeningHistory.user_id == user_id)

        if from_timestamp is not None:
            query = query.filter(ListeningHistory.listened_at >= from_timestamp)
        if to_timestamp is not None:
            query = query.filter(ListeningHistory.listened_at <= to_timestamp)

        total = query.count() or 0

        offset = (page - 1) * size
        records = (
            query.order_by(ListeningHistory.listened_at.desc())
            .offset(offset)
            .limit(size)
            .all()
        )

        items = []
        for rec in records:
            audio_url = None
            if rec.content is not None and rec.content.translations:
                audio_url = rec.content.translations[0].audio_url

            stall_name = None
            if rec.stall is not None:
                stall_name = self._get_stall_translation(rec.stall.id, requested_lang) or rec.stall.name

            items.append({
                "id": rec.id,
                "user_id": rec.user_id,
                "stall_id": rec.stall_id,
                "stall_content_id": rec.stall_content_id,
                "listened_at": rec.listened_at,
                "listen_duration": rec.listen_duration,
                "stall_name": stall_name,
                "audio_url": audio_url,
            })

        return {
            "page": page,
            "size": size,
            "total": total,
            "items": items,
        }

    def add_listening_history(
        self,
        user_id: str,
        stall_id: str,
        stall_content_id: str,
        listened_at: int,
        listen_duration: int | None = None,
    ) -> dict:
        new_record = ListeningHistory(
            user_id=user_id,
            stall_id=stall_id,
            stall_content_id=stall_content_id,
            listened_at=listened_at,
            listen_duration=listen_duration,
        )
        self.db.add(new_record)
        self.db.commit()
        self.db.refresh(new_record)

        return {
            "id": new_record.id,
            "user_id": new_record.user_id,
            "stall_id": new_record.stall_id,
            "stall_content_id": new_record.stall_content_id,
            "listened_at": new_record.listened_at,
            "listen_duration": new_record.listen_duration,
        }
