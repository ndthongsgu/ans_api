from sqlalchemy.orm import Session
from models.stallContent import StallContent
import time
from typing import Tuple, List
from utils.tts_generator import generate_audio_from_text, delete_audio_file

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

    def create_stall_content(self, data: dict):
        # Auto-generate audio if tts_script is provided and audio_url is not
        audio_url = data.get('audio_url')
        audio_duration = data.get('audio_duration')
        audio_file_size = data.get('audio_file_size')
        
        if data.get('tts_script') and not audio_url:
            # Generate audio from tts_script
            language_code = data.get('language_code', 'vi')
            audio_data = generate_audio_from_text(data['tts_script'], language_code)
            audio_url = audio_data['audio_url']
            audio_duration = audio_data['audio_duration']
            audio_file_size = audio_data['audio_file_size']
        
        if not audio_url:
            raise RuntimeError("audio_url is required or tts_script must be provided for auto-generation")
        
        content = StallContent(
            stall_id=data['stall_id'],
            language_code=data.get('language_code', 'vi'),
            audio_url=audio_url,
            audio_duration=audio_duration,
            audio_file_size=audio_file_size,
            tts_script=data.get('tts_script'),
            version=data.get('version', 1),
            created_at=int(time.time())
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    def update_stall_content(self, content_id: str, data: dict):
        content = self.get_stall_content(content_id)
        if not content:
            return None
        
        # Auto-generate audio if tts_script is provided and audio_url is updated
        audio_url = data.get('audio_url', content.audio_url)
        audio_duration = data.get('audio_duration', content.audio_duration)
        audio_file_size = data.get('audio_file_size', content.audio_file_size)
        
        # If tts_script is provided and different, regenerate audio
        new_tts_script = data.get('tts_script', content.tts_script)
        if new_tts_script and new_tts_script != content.tts_script and not (data.get('audio_url') and data['audio_url'] != content.audio_url):
            # Regenerate audio only if tts_script changed and no explicit audio_url provided
            language_code = data.get('language_code', content.language_code)
            audio_data = generate_audio_from_text(new_tts_script, language_code)
            audio_url = audio_data['audio_url']
            audio_duration = audio_data['audio_duration']
            audio_file_size = audio_data['audio_file_size']
            
            # Delete old audio file if exists
            if content.audio_url:
                delete_audio_file(content.audio_url)
        
        content.stall_id = data['stall_id']
        content.language_code = data.get('language_code', content.language_code)
        content.audio_url = audio_url
        content.audio_duration = audio_duration
        content.audio_file_size = audio_file_size
        content.tts_script = new_tts_script
        content.version = data.get('version', content.version)
        content.updated_at = int(time.time())
        
        self.db.commit()
        return content

    def deactivate_stall_content(self, content_id: str):
        content = self.get_stall_content(content_id)
        if content:
            content.is_deleted = True
            self.db.commit()
        return content

    def activate_stall_content(self, content_id: str):
        content = self.get_stall_content(content_id)
        if content:
            content.is_deleted = False
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