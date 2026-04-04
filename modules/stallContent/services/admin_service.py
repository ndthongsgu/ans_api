from sqlalchemy.orm import Session
from models.stallContent import StallContent
from models.stallContentTranslation import StallContentTranslation
import time
from typing import Tuple, List
from utils.tts_generator import generate_audio_from_text, delete_audio_file
from utils.translation import translate_to_multiple_languages, get_tts_language_code
from common.enums.language import LanguageCode
import logging

logger = logging.getLogger(__name__)

class StallContentService:
    def __init__(self, db: Session):
        self.db = db

    def list_stall_contents(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[StallContent]]:
        q = self.db.query(StallContent)
            
        if filters.get('stall_id'):
            q = q.filter(StallContent.stall_id == filters['stall_id'])
            
        if filters.get('is_deleted') is not None:
            q = q.filter(StallContent.is_deleted == filters['is_deleted'])
                
        # Ordering
        if sortBy:
            column = getattr(StallContent, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
                    
        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_stall_content(self, content_id: str):
        return self.db.query(StallContent).filter(StallContent.id == content_id).first()

    def _get_all_language_codes(self) -> List[str]:
        """Get all available language codes from LanguageCode enum"""
        return [lang["code"] for lang in LanguageCode.LIST]

    def _create_stall_content_for_language(self, stall_content_id: str, language_code: str, tts_script: str) -> StallContentTranslation:
        """Create a single StallContentTranslation record for a specific language"""
        if not tts_script or not tts_script.strip():
            raise RuntimeError(f"TTS script cannot be empty for language {language_code}")
        
        # Generate audio from tts_script
        tts_lang_code = get_tts_language_code(language_code)
        audio_data = generate_audio_from_text(tts_script, tts_lang_code)
        
        trans = StallContentTranslation(
            stall_content_id=stall_content_id,
            language_code=language_code,
            audio_url=audio_data['audio_url'],
            audio_duration=audio_data.get('audio_duration'),
            audio_file_size=audio_data.get('audio_file_size'),
            tts_script=tts_script,
        )
        
        self.db.add(trans)
        return trans

    def create_stall_content(self, data: dict):
        """
        Create multilingual StallContent
        
        Input: Vietnamese TTS script
        Output: 1 StallContent record + multiple StallContentTranslation records (one for each language)
        """
        stall_id = data.get('stall_id')
        tts_script_vi = data.get('tts_script')
        
        if not stall_id or not stall_id.strip():
            raise RuntimeError("stall_id is required")
        
        if not tts_script_vi or not tts_script_vi.strip():
            raise RuntimeError("tts_script is required and must be in Vietnamese")
        
        # Create base StallContent record (without language-specific data)
        content = StallContent(
            stall_id=stall_id,
            tts_script=tts_script_vi,  # Store Vietnamese script in base record
            created_at=int(time.time())
        )
        self.db.add(content)
        self.db.flush()  # Get content ID without committing
        
        # Get all language codes
        language_codes = self._get_all_language_codes()
        logger.info(f"Creating stall content for stall_id={stall_id} with languages: {language_codes}")
        
        # Translate to all languages
        translated_scripts = translate_to_multiple_languages(
            tts_script_vi,
            language_codes,
            source_lang="vi"
        )
        
        logger.info(f"Translated scripts received: {list(translated_scripts.keys())}")
        for lang, script in translated_scripts.items():
            logger.info(f"  {lang}: {script[:50]}..." if len(script) > 50 else f"  {lang}: {script}")
        
        created_translations = []
        try:
            # Create translation records for all languages
            for lang_code in language_codes:
                tts_script = translated_scripts.get(lang_code, tts_script_vi)
                logger.info(f"Creating StallContentTranslation for {lang_code}")
                trans = self._create_stall_content_for_language(content.id, lang_code, tts_script)
                created_translations.append(trans)
            
            # Commit all records at once
            self.db.commit()
            logger.info(f"Successfully committed 1 StallContent + {len(created_translations)} translation records")
            
            self.db.refresh(content)
            return [content] + created_translations  # Return for API response
        except Exception as e:
            logger.error(f"Failed to create multilingual content: {str(e)}")
            self.db.rollback()
            # Clean up created audio files on error
            for trans in created_translations:
                if trans.audio_url:
                    try:
                        delete_audio_file(trans.audio_url)
                    except:
                        pass
            raise RuntimeError(f"Failed to create multilingual content: {str(e)}")

    def update_stall_content(self, content_id: str, data: dict):
        """
        Update multilingual StallContent
        
        If tts_script is provided, updates all language translation records for this content id
        with translated scripts and regenerated audio files.
        """
        # Find content by content_id
        content = self.get_stall_content(content_id)
        if not content:
            return None
        
        logger.info(f"Updating stall content for stall_id={content.stall_id}, content_id={content.id}")
        
        tts_script_vi = data.get('tts_script')
        
        # If tts_script is provided, regenerate all language versions
        if tts_script_vi and tts_script_vi.strip():
            language_codes = self._get_all_language_codes()
            logger.info(f"Translating to {language_codes}")
            
            # Translate to all languages
            translated_scripts = translate_to_multiple_languages(
                tts_script_vi,
                language_codes,
                source_lang="vi"
            )
            
            logger.info(f"Translated scripts: {list(translated_scripts.keys())}")
            
            try:
                # Get or create translation records for each language
                for lang_code in language_codes:
                    tts_script = translated_scripts.get(lang_code, tts_script_vi)
                    logger.info(f"Updating {lang_code}: {tts_script[:50]}..." if len(tts_script) > 50 else f"Updating {lang_code}: {tts_script}")
                    
                    # Find existing translation
                    trans = self.db.query(StallContentTranslation).filter(
                        StallContentTranslation.stall_content_id == content.id,
                        StallContentTranslation.language_code == lang_code
                    ).first()
                    
                    # Generate new audio
                    tts_lang_code = get_tts_language_code(lang_code)
                    audio_data = generate_audio_from_text(tts_script, tts_lang_code)
                    
                    if trans:
                        # Delete old audio file
                        if trans.audio_url:
                            try:
                                delete_audio_file(trans.audio_url)
                            except:
                                pass
                        
                        # Update existing translation
                        trans.audio_url = audio_data['audio_url']
                        trans.audio_duration = audio_data.get('audio_duration')
                        trans.audio_file_size = audio_data.get('audio_file_size')
                        trans.tts_script = tts_script
                        trans.updated_at = int(time.time())
                    else:
                        # Create new translation if it doesn't exist
                        trans = StallContentTranslation(
                            stall_content_id=content.id,
                            language_code=lang_code,
                            audio_url=audio_data['audio_url'],
                            audio_duration=audio_data.get('audio_duration'),
                            audio_file_size=audio_data.get('audio_file_size'),
                            tts_script=tts_script,
                        )
                        self.db.add(trans)
                
                # Update base record with Vietnamese script
                content.tts_script = tts_script_vi
                content.updated_at = int(time.time())
                
                self.db.commit()
                logger.info(f"Successfully updated translations for content_id={content.id}")
                return [content]
            except Exception as e:
                logger.error(f"Failed to update multilingual content: {str(e)}")
                self.db.rollback()
                raise RuntimeError(f"Failed to update multilingual content: {str(e)}")
        else:
            # If no tts_script provided, just update other fields if needed
            content.updated_at = int(time.time())
            self.db.commit()
            return [content]

    def deactivate_stall_content(self, content_id: str):
        """Deactivate a single stall content by content_id"""
        content = self.db.query(StallContent).filter(
            StallContent.id == content_id
        ).first()
        if not content:
            return None

        content.is_deleted = True
        content.updated_at = int(time.time())
        self.db.commit()
        return content

    def activate_stall_content(self, content_id: str):
        """Activate a single stall content by content_id"""
        content = self.db.query(StallContent).filter(
            StallContent.id == content_id
        ).first()
        if not content:
            return None

        content.is_deleted = False
        content.updated_at = int(time.time())
        self.db.commit()
        return content

    def list_all_active(self):
        return self.db.query(StallContent).filter(StallContent.is_deleted == False).all()

    def list_for_select(self):
        """Return stall contents formatted for select dropdown"""
        contents = self.list_all_active()
        return [
            {
                "id": c.id,
                "stall_id": c.stall_id
            }
            for c in contents
        ]