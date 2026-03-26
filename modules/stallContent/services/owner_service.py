import time

from sqlalchemy.orm import Session

from common.enums.language import LanguageCode
from models.owner import Owner
from models.stall import Stall
from models.stallContent import StallContent
from modules.stallContent.dto.owner_dto import (
    OwnerStallContentCreateRequest,
    OwnerStallContentResponse,
)
from utils.translation_util import TranslationService


class ServiceError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class OwnerStallContentService:
    def __init__(self, db: Session):
        self.db = db
        self.translator = TranslationService()

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
            return "vi"
        return language_code.strip().lower()

    def _ensure_supported_language(self, language_code: str) -> str:
        normalized = self._normalize_language_code(language_code)
        if not LanguageCode.is_supported(normalized):
            raise ServiceError("invalid_language_code")
        return normalized

    def _resolve_target_languages(self, source_language: str, target_languages: list[str] | None) -> list[str]:
        if target_languages is None:
            return [code for code in LanguageCode.codes() if code != source_language]

        resolved: list[str] = []
        for code in target_languages:
            normalized = self._ensure_supported_language(code)
            if normalized != source_language and normalized not in resolved:
                resolved.append(normalized)
        return resolved

    def _upsert_content(
        self,
        stall_id: str,
        language_code: str,
        title: str,
        description: str | None,
        short_description: str | None,
        audio_url: str,
        audio_duration: int | None,
        audio_file_size: int | None,
        tts_script: str | None,
        version: int,
        is_deleted: bool,
        now: int,
    ) -> StallContent:
        content = (
            self.db.query(StallContent)
            .filter(
                StallContent.stall_id == stall_id,
                StallContent.language_code == language_code,
            )
            .first()
        )

        if not content:
            content = StallContent(
                stall_id=stall_id,
                language_code=language_code,
                title=title,
                description=description,
                short_description=short_description,
                audio_url=audio_url,
                audio_duration=audio_duration,
                audio_file_size=audio_file_size,
                tts_script=tts_script,
                version=version,
                is_deleted=is_deleted,
                created_at=now,
                updated_at=now,
            )
            self.db.add(content)
            return content

        content.title = title
        content.description = description
        content.short_description = short_description
        content.audio_url = audio_url
        content.audio_duration = audio_duration
        content.audio_file_size = audio_file_size
        content.tts_script = tts_script
        content.version = version
        content.is_deleted = is_deleted
        content.updated_at = now
        return content

    def _to_response(self, content: StallContent) -> OwnerStallContentResponse:
        return OwnerStallContentResponse(
            id=content.id,
            stallId=content.stall_id,
            languageCode=content.language_code,
            title=content.title,
            description=content.description,
            shortDescription=content.short_description,
            audioUrl=content.audio_url,
            audioDuration=content.audio_duration,
            audioFileSize=content.audio_file_size,
            ttsScript=content.tts_script,
            version=content.version,
            isActive=not content.is_deleted,
            createdAt=content.created_at,
            updatedAt=content.updated_at,
        )

    def _translate_for_language(
        self,
        source_language: str,
        target_language: str,
        title: str,
        description: str | None,
        short_description: str | None,
        tts_script: str | None,
    ) -> dict:
        return {
            "title": self.translator.translate_text(title, source_language, target_language) or title,
            "description": self.translator.translate_text(description, source_language, target_language),
            "short_description": self.translator.translate_text(short_description, source_language, target_language),
            "tts_script": self.translator.translate_text(tts_script, source_language, target_language),
        }

    def create_content(
        self,
        user_id: str,
        payload: OwnerStallContentCreateRequest,
    ) -> OwnerStallContentResponse:
        owner = self._ensure_owner(user_id)
        self._ensure_owner_stall(owner.id, payload.stallId)

        title = payload.title.strip()
        audio_url = payload.audioUrl.strip()
        if not title:
            raise ServiceError("invalid_stall_content_title")
        if not audio_url:
            raise ServiceError("invalid_audio_url")

        source_language = self._ensure_supported_language(payload.languageCode)
        now = int(time.time())

        source_content = self._upsert_content(
            stall_id=payload.stallId,
            language_code=source_language,
            title=title,
            description=payload.description,
            short_description=payload.shortDescription,
            audio_url=audio_url,
            audio_duration=payload.audioDuration,
            audio_file_size=payload.audioFileSize,
            tts_script=payload.ttsScript,
            version=payload.version,
            is_deleted=not payload.isActive,
            now=now,
        )

        if payload.autoTranslate:
            target_languages = self._resolve_target_languages(source_language, payload.targetLanguages)
            for language in target_languages:
                translated = self._translate_for_language(
                    source_language=source_language,
                    target_language=language,
                    title=title,
                    description=payload.description,
                    short_description=payload.shortDescription,
                    tts_script=payload.ttsScript,
                )
                self._upsert_content(
                    stall_id=payload.stallId,
                    language_code=language,
                    title=translated["title"],
                    description=translated["description"],
                    short_description=translated["short_description"],
                    audio_url=audio_url,
                    audio_duration=payload.audioDuration,
                    audio_file_size=payload.audioFileSize,
                    tts_script=translated["tts_script"],
                    version=payload.version,
                    is_deleted=not payload.isActive,
                    now=now,
                )

        self.db.commit()
        self.db.refresh(source_content)
        return self._to_response(source_content)
