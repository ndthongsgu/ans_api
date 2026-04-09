import time
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from common.enums.language import LanguageCode
from models.listeningHistory import ListeningHistory
from models.owner import Owner
from models.stall import Stall
from models.stallContent import StallContent
from models.stallContentTranslation import StallContentTranslation
from modules.stall_content.dto.owner_dto import (
    StallContentCreateRequest,
    StallContentResponse,
    StallContentUpdateRequest,
)
from utils.tts_generator import generate_audio_from_text
from utils.translation import translate_to_multiple_languages, get_tts_language_code


class ServiceError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class OwnerStallContentService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_owner(self, user_id: str) -> Owner:
        owner = self.db.query(Owner).filter(Owner.user_id == user_id).first()
        if not owner:
            raise ServiceError("profile_not_found")
        return owner

    def _ensure_owner_stall(self, owner_id: str, stall_id: str) -> Stall:
        stall = (
            self.db.query(Stall)
            .filter(Stall.id == stall_id, Stall.owner_id == owner_id)
            .first()
        )
        if not stall:
            raise ServiceError("stall_not_found")
        return stall

    def _normalize_language_code(self, language_code: str | None) -> str:
        if language_code is None:
            return LanguageCode.DEFAULT
        return language_code.strip().lower()

    def _ensure_supported_language(self, language_code: str) -> str:
        normalized = self._normalize_language_code(language_code)
        if normalized not in LanguageCode.get_codes():
            raise ServiceError("invalid_language_code")
        return normalized

    def _resolve_target_languages(self, source_language: str) -> list[str]:
        return [code for code in LanguageCode.get_codes() if code != source_language]

    def _get_all_language_codes(self) -> list[str]:
        return [lang["code"] for lang in LanguageCode.LIST]

    def _get_translation(
        self,
        content_id: str,
        language_code: str,
    ) -> StallContentTranslation | None:
        trans = (
            self.db.query(StallContentTranslation)
            .filter(
                StallContentTranslation.stall_content_id == content_id,
                StallContentTranslation.language_code == language_code,
            )
            .first()
        )
        if trans:
            return trans

        # fallback to default language
        if language_code != LanguageCode.DEFAULT:
            return (
                self.db.query(StallContentTranslation)
                .filter(
                    StallContentTranslation.stall_content_id == content_id,
                    StallContentTranslation.language_code == LanguageCode.DEFAULT,
                )
                .first()
            )
        return None

    def _upsert_translation(
        self,
        content_id: str,
        language_code: str,
        audio_url: str,
        audio_duration: int | None,
        audio_file_size: int | None,
        tts_script: str | None,
        now: int,
    ) -> StallContentTranslation:
        trans = (
            self.db.query(StallContentTranslation)
            .filter(
                StallContentTranslation.stall_content_id == content_id,
                StallContentTranslation.language_code == language_code,
            )
            .first()
        )
        if not trans:
            trans = StallContentTranslation(
                stall_content_id=content_id,
                language_code=language_code,
                audio_url=audio_url,
                audio_duration=audio_duration,
                audio_file_size=audio_file_size,
                tts_script=tts_script,
                created_at=now,
                updated_at=now,
            )
            self.db.add(trans)
            return trans

        trans.audio_url = audio_url
        trans.audio_duration = audio_duration
        trans.audio_file_size = audio_file_size
        trans.tts_script = tts_script
        trans.updated_at = now
        return trans

    def _to_response(
        self,
        content: StallContent,
        language_code: str,
    ) -> StallContentResponse:
        trans = self._get_translation(content.id, language_code)
        return StallContentResponse(
            id=content.id,
            stall_id=content.stall_id,
            stall_name=content.stall.name if content.stall else None,
            language_code=trans.language_code if trans else language_code,
            audio_url=trans.audio_url if trans else "",
            audio_duration=trans.audio_duration if trans else None,
            audio_file_size=trans.audio_file_size if trans else None,
            tts_script=trans.tts_script if trans else content.tts_script,
            is_deleted=content.is_deleted,
            created_at=content.created_at,
            updated_at=content.updated_at,
        )

    def _translate_for_language(
        self,
        source_language: str,
        target_language: str,
        tts_script: str | None,
    ) -> dict:
        if tts_script is None:
            return {"tts_script": None}
        translated_map = translate_to_multiple_languages(
            tts_script,
            [target_language],
            source_lang=source_language,
        )
        return {
            "tts_script": translated_map.get(target_language, tts_script),
        }

    def _generate_audio_from_tts(
        self,
        language_code: str,
        tts_script: str,
    ) -> dict:
        script = tts_script.strip()
        if not script:
            raise ServiceError("invalid_tts_script")

        try:
            tts_lang_code = get_tts_language_code(language_code)
            return generate_audio_from_text(script, language_code=tts_lang_code)
        except Exception as exc:
            raise ServiceError(f"tts_generation_failed: {str(exc)}")

    def create_content(
        self,
        user_id: str,
        payload: StallContentCreateRequest,
    ) -> StallContentResponse:
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, payload.stall_id)

        source_language = LanguageCode.DEFAULT
        now = int(time.time())
        source_audio = self._generate_audio_from_tts(source_language, payload.tts_script)

        # One stall must have only one narration content record.
        source_content = (
            self.db.query(StallContent)
            .filter(StallContent.stall_id == payload.stall_id)
            .order_by(StallContent.created_at.desc())
            .first()
        )

        if source_content:
            source_content.tts_script = payload.tts_script
            source_content.is_deleted = False
            source_content.updated_at = now
        else:
            source_content = StallContent(
                stall_id=payload.stall_id,
                tts_script=payload.tts_script,
            )
            self.db.add(source_content)
            self.db.flush()

        self._upsert_translation(
            content_id=source_content.id,
            language_code=source_language,
            audio_url=source_audio["audio_url"],
            audio_duration=source_audio.get("audio_duration"),
            audio_file_size=source_audio.get("audio_file_size"),
            tts_script=payload.tts_script,
            now=now,
        )

        all_languages = self._get_all_language_codes()
        translated_scripts = translate_to_multiple_languages(
            payload.tts_script,
            all_languages,
            source_lang=source_language,
        )

        target_languages = self._resolve_target_languages(source_language)
        for language in target_languages:
            try:
                translated_script = translated_scripts.get(language, payload.tts_script)
                translated_audio = self._generate_audio_from_tts(language, translated_script)
                self._upsert_translation(
                    content_id=source_content.id,
                    language_code=language,
                    audio_url=translated_audio["audio_url"],
                    audio_duration=translated_audio.get("audio_duration"),
                    audio_file_size=translated_audio.get("audio_file_size"),
                    tts_script=translated_script,
                    now=now,
                )
            except ServiceError:
                continue

        self.db.commit()
        self.db.refresh(source_content)
        return self._to_response(source_content, source_language)

    def list_stalls_without_content(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[dict], int]:
        owner = self._ensure_owner(user_id)

        has_any_content = (
            self.db.query(StallContent.id)
            .filter(StallContent.stall_id == Stall.id)
            .exists()
        )

        query = (
            self.db.query(Stall)
            .filter(
                Stall.owner_id == owner.id,
                Stall.is_deleted == False,
                ~has_any_content,
            )
        )

        stalls = query.order_by(Stall.created_at.desc()).offset(skip).limit(limit).all()
        data = [{"id": stall.id, "stall_name": stall.name} for stall in stalls]
        return data

    def list_stall_contents(
        self,
        user_id: str,
        stall_id: str,
        language_code: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[StallContentResponse], int]:
        """List all contents for a stall owned by the user"""
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, stall_id)

        requested_lang = self._ensure_supported_language(language_code) if language_code else LanguageCode.DEFAULT

        query = self.db.query(StallContent).filter(
            StallContent.stall_id == stall_id,
            StallContent.is_deleted == False,
        )

        total = query.count()
        contents = query.order_by(StallContent.created_at.desc()).offset(skip).limit(limit).all()

        return [self._to_response(c, requested_lang) for c in contents], total

    def list_owner_contents(
        self,
        user_id: str,
        language_code: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[StallContentResponse], int]:
        owner = self._ensure_owner(user_id)
        requested_lang = self._ensure_supported_language(language_code) if language_code else LanguageCode.DEFAULT

        query = (
            self.db.query(StallContent)
            .join(Stall, Stall.id == StallContent.stall_id)
            .filter(
                Stall.owner_id == owner.id,
                StallContent.is_deleted == False,
            )
        )

        total = query.count()
        data = query.order_by(StallContent.created_at.desc()).offset(skip).limit(limit).all()
        return [self._to_response(c, requested_lang) for c in data], total

    def get_available_languages(
        self,
        user_id: str,
        stall_id: str,
    ) -> list[str]:
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, stall_id)

        content_ids = [
            c.id
            for c in self.db.query(StallContent.id)
            .filter(
                StallContent.stall_id == stall_id,
                StallContent.is_deleted == False,
            )
            .all()
        ]

        if not content_ids:
            return []

        rows = (
            self.db.query(StallContentTranslation.language_code)
            .filter(StallContentTranslation.stall_content_id.in_(content_ids))
            .distinct()
            .all()
        )
        return [r[0] for r in rows]

    def get_content(
        self,
        user_id: str,
        stall_id: str,
        content_id: str,
        language_code: str | None = None,
    ) -> StallContentResponse:
        """Get a specific content by ID"""
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, stall_id)

        content = (
            self.db.query(StallContent)
            .filter(
                StallContent.id == content_id,
                StallContent.stall_id == stall_id,
                StallContent.is_deleted == False,
            )
            .first()
        )

        if not content:
            raise ServiceError("content_not_found")

        requested_lang = self._ensure_supported_language(language_code) if language_code else LanguageCode.DEFAULT
        return self._to_response(content, requested_lang)

    def update_content(
        self,
        user_id: str,
        stall_id: str,
        content_id: str,
        payload: StallContentUpdateRequest,
    ) -> StallContentResponse:
        """Update a content item"""
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, stall_id)

        content = (
            self.db.query(StallContent)
            .filter(
                StallContent.id == content_id,
                StallContent.stall_id == stall_id,
                StallContent.is_deleted == False,
            )
            .first()
        )

        if not content:
            raise ServiceError("content_not_found")

        now = int(time.time())

        update_lang = self._ensure_supported_language(payload.language_code) if payload.language_code else LanguageCode.DEFAULT

        if payload.tts_script is not None:
            translated_scripts = translate_to_multiple_languages(
                payload.tts_script,
                self._get_all_language_codes(),
                source_lang=update_lang,
            )

            source_script = translated_scripts.get(update_lang, payload.tts_script)
            audio_data = self._generate_audio_from_tts(update_lang, source_script)

            content.tts_script = source_script

        content.updated_at = now

        if payload.tts_script is not None:
            self._upsert_translation(
                content_id=content.id,
                language_code=update_lang,
                audio_url=audio_data["audio_url"],
                audio_duration=audio_data.get("audio_duration"),
                audio_file_size=audio_data.get("audio_file_size"),
                tts_script=content.tts_script,
                now=now,
            )

            for language in self._resolve_target_languages(update_lang):
                try:
                    translated_script = translated_scripts.get(language, payload.tts_script)
                    translated_audio = self._generate_audio_from_tts(language, translated_script)
                    self._upsert_translation(
                        content_id=content.id,
                        language_code=language,
                        audio_url=translated_audio["audio_url"],
                        audio_duration=translated_audio.get("audio_duration"),
                        audio_file_size=translated_audio.get("audio_file_size"),
                        tts_script=translated_script,
                        now=now,
                    )
                except ServiceError:
                    continue

        self.db.commit()
        self.db.refresh(content)
        return self._to_response(content, update_lang)

    def delete_content(
        self,
        user_id: str,
        stall_id: str,
        content_id: str,
    ) -> None:
        """Delete a content item permanently from database"""
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, stall_id)

        content = (
            self.db.query(StallContent)
            .filter(
                StallContent.id == content_id,
                StallContent.stall_id == stall_id,
            )
            .first()
        )

        if not content:
            raise ServiceError("content_not_found")

        # Ensure foreign key constraints are satisfied before deleting content.
        self.db.query(ListeningHistory).filter(
            ListeningHistory.stall_content_id == content.id
        ).delete(synchronize_session=False)

        self.db.delete(content)

        self.db.commit()

    def set_content_deleted_status(
        self,
        user_id: str,
        stall_id: str,
        content_id: str,
        is_deleted: bool,
    ) -> StallContentResponse:
        """Toggle content active status using is_deleted flag"""
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, stall_id)

        content = (
            self.db.query(StallContent)
            .filter(
                StallContent.id == content_id,
                StallContent.stall_id == stall_id,
            )
            .first()
        )

        if not content:
            raise ServiceError("content_not_found")

        content.is_deleted = is_deleted
        content.updated_at = int(time.time())

        self.db.commit()
        self.db.refresh(content)
        return self._to_response(content, LanguageCode.DEFAULT)

