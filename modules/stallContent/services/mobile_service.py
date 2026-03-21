from sqlalchemy.orm import Session
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
        """Get translation for specific language, fallback to 'vi' if not found"""
        trans = self.db.query(StallContentTranslation).filter(
            StallContentTranslation.stall_content_id == content_id,
            StallContentTranslation.language_code == language_code
        ).first()
        
        if not trans and language_code != "vi":
            # Fallback to Vietnamese
            trans = self.db.query(StallContentTranslation).filter(
                StallContentTranslation.stall_content_id == content_id,
                StallContentTranslation.language_code == "vi"
            ).first()
        
        return trans

    def get_stall_contents(self, stall_id: str, language_code: str = "vi") -> List[dict]:
        """Get all content items for a stall with multilingual translations"""
        contents = self.db.query(StallContent).filter(
            StallContent.stall_id == stall_id,
            StallContent.is_deleted == False
        ).all()
        
        results = []
        for c in contents:
            trans = self._get_content_translation(c.id, language_code)
            
            result_item = {
                "id": c.id,
                "stall_id": c.stall_id,
                "type": c.type,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "is_deleted": c.is_deleted,
            }
            
            # Add translation-specific fields
            if trans:
                result_item["audio_url"] = trans.audio_url
                result_item["tts_script"] = trans.tts_script
                result_item["language_code"] = trans.language_code
            else:
                result_item["audio_url"] = None
                result_item["tts_script"] = None
                result_item["language_code"] = language_code
            
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
            "type": content.type,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
            "is_deleted": content.is_deleted,
        }
        
        # Add translation-specific fields
        if trans:
            result["audio_url"] = trans.audio_url
            result["tts_script"] = trans.tts_script
            result["language_code"] = trans.language_code
        else:
            result["audio_url"] = None
            result["tts_script"] = None
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
                    "type": content.type,
                    "audio_url": trans.audio_url,
                    "tts_script": trans.tts_script,
                    "language_code": trans.language_code,
                })
        
        logger.info(f"Found {len(results)} matching content items in stall {stall_id}")
        return results
