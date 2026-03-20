from sqlalchemy.orm import Session
from models.stallContent import StallContent
import time
from typing import Tuple, List

class StallContentService:
    def __init__(self, db: Session):
        self.db = db

    def list_stall_contents(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[StallContent]]:
        q = self.db.query(StallContent)
        
        if filters.get('title'):
            q = q.filter(StallContent.title.ilike(f"%{filters['title']}%"))
            
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
        content = StallContent(
            stall_id=data['stall_id'],
            language_code=data.get('language_code', 'vi'),
            title=data['title'],
            description=data.get('description'),
            short_description=data.get('short_description'),
            audio_url=data['audio_url'],
            audio_duration=data.get('audio_duration'),
            audio_file_size=data.get('audio_file_size'),
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
            
        content.stall_id = data['stall_id']
        content.language_code = data.get('language_code', 'vi')
        content.title = data['title']
        content.description = data.get('description')
        content.short_description = data.get('short_description')
        content.audio_url = data['audio_url']
        content.audio_duration = data.get('audio_duration')
        content.audio_file_size = data.get('audio_file_size')
        content.tts_script = data.get('tts_script')
        content.version = data.get('version', 1)
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
                "title": c.title,
                "stall_id": c.stall_id
            }
            for c in contents
        ]