from sqlalchemy.orm import Session
from common.enums.language import LanguageCode
from models.stallContent import StallContent
from models.stallContentTranslation import StallContentTranslation
from typing import List
import logging

logger = logging.getLogger(__name__)


class StallContentMobileService:
    """Service for mobile API - read-only operations for stall content with multilingual support"""
    
    def __init__(self, db: Session):
        self.db = db

    def _get_content_translation(self, content_id: str, language_code: str) -> StallContentTranslation | None:
        """Get translation for specific language, fallback to default language if not found"""
        trans = self.db.query(StallContentTranslation).filter(
            StallContentTranslation.stall_content_id == content_id,
            StallContentTranslation.language_code == language_code
        ).first()
        
        if not trans and language_code != LanguageCode.DEFAULT:
            # Fallback to default language
            trans = self.db.query(StallContentTranslation).filter(
                StallContentTranslation.stall_content_id == content_id,
                StallContentTranslation.language_code == LanguageCode.DEFAULT
            ).first()
        
        return trans

    def get_stall_contents(self, stall_id: str, language_code: str = "vi") -> List[dict]:
        """Get all content items for a stall with translations in requested language only"""
        contents = self.db.query(StallContent).filter(
            StallContent.stall_id == stall_id,
            StallContent.is_deleted == False
        ).all()
        
        results = []
        for c in contents:
            trans = self._get_content_translation(c.id, language_code)
            
            # Use translation if available, otherwise fall back to content's direct fields
            audio_url = trans.audio_url if trans else None
            tts_script = trans.tts_script if trans else c.tts_script
            audio_duration = trans.audio_duration if trans else None
            audio_file_size = trans.audio_file_size if trans else None
            
            result_item = {
                "id": c.id,
                "audio_url": audio_url,
                "tts_script": tts_script,
                "audio_duration": audio_duration,
                "audio_file_size": audio_file_size,
                "language_code": language_code,
            }
            
            results.append(result_item)
        
        logger.info(f"Retrieved {len(results)} content items for stall {stall_id} in language {language_code}")
        return results

    def get_content_by_language(self, stall_id: str, content_id: str, language_code: str = "vi") -> dict | None:
        """Get specific content item for a stall with specific language translation"""
        content = self.db.query(StallContent).filter(
            StallContent.id == content_id,
            StallContent.stall_id == stall_id,
            StallContent.is_deleted == False
        ).first()
        
        if not content:
            logger.warning(f"Content {content_id} not found for stall {stall_id}")
            return None
        
        trans = self._get_content_translation(content.id, language_code)
        
        result = {
            "id": content.id,
            "stall_id": content.stall_id,
            "audio_duration": trans.audio_duration if trans else None,
            "audio_file_size": trans.audio_file_size if trans else None,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
        }
        
        # Add translation-specific fields if translation exists
        if trans:
            result["audio_url"] = trans.audio_url
            result["tts_script"] = trans.tts_script
            result["language_code"] = trans.language_code
        else:
            # Fallback to content-level script
            result["audio_url"] = None
            result["tts_script"] = content.tts_script
            result["language_code"] = language_code
        
        logger.info(f"Retrieved content {content_id} for stall {stall_id} in language {language_code}")
        return result

    def get_available_languages(self, stall_id: str) -> List[str]:
        """Get all available languages for a stall's content"""
        # Get distinct languages from all content translations for this stall
        stall_contents = self.db.query(StallContent.id).filter(
            StallContent.stall_id == stall_id,
            StallContent.is_deleted == False
        ).all()
        
        if not stall_contents:
            logger.info(f"No content found for stall {stall_id}")
            return []
        
        content_ids = [c[0] for c in stall_contents]
        
        languages = self.db.query(StallContentTranslation.language_code).filter(
            StallContentTranslation.stall_content_id.in_(content_ids)
        ).distinct().all()
        
        lang_list = [lang[0] for lang in languages]
        logger.info(f"Retrieved {len(lang_list)} available languages for stall {stall_id} content")
        return lang_list

    def search_by_tts_script(self, stall_id: str, search_text: str, language_code: str = "vi") -> List[dict]:
        """Search stall content by TTS script text"""
        # Get content IDs that have translations matching the search
        matching_translations = self.db.query(StallContentTranslation).filter(
            StallContentTranslation.language_code == language_code,
            StallContentTranslation.tts_script.contains(search_text)
        ).all()
        
        matching_content_ids = [t.stall_content_id for t in matching_translations]
        
        if not matching_content_ids:
            logger.info(f"No matching content found for stall {stall_id} with text '{search_text}'")
            return []
        
        # Get the actual content items and ensure they belong to this stall
        results = []
        for trans in matching_translations:
            content = self.db.query(StallContent).filter(
                StallContent.id == trans.stall_content_id,
                StallContent.stall_id == stall_id,
                StallContent.is_deleted == False
            ).first()
            
            if content:
                results.append({
                    "id": content.id,
                    "stall_id": content.stall_id,
                    "audio_url": trans.audio_url,
                    "tts_script": trans.tts_script,
                    "language_code": trans.language_code,
                })
        
        logger.info(f"Found {len(results)} matching content items in stall {stall_id}")
        return results
