from sqlalchemy.orm import Session
from models.stallContent import StallContent
from schemas.admin.stall_content import StallContentCreate, StallContentUpdate

class StallContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_content(self, content_id: str):
        return self.db.query(StallContent).filter(StallContent.id == content_id).first()

    def get_contents(self, skip: int = 0, limit: int = 100):
        return self.db.query(StallContent).offset(skip).limit(limit).all()

    def create_content(self, content: StallContentCreate):
        db_content = StallContent(
            stall_id=content.stall_id,
            language_code=content.language_code,
            title=content.title,
            description=content.description,
            audio_url=content.audio_url,
        )
        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)
        return db_content

    def update_content(self, content_id: str, content: StallContentUpdate):
        db_content = self.get_content(content_id)
        if db_content:
            db_content.stall_id = content.stall_id
            db_content.language_code = content.language_code
            db_content.title = content.title
            db_content.description = content.description
            db_content.audio_url = content.audio_url
            self.db.commit()
            self.db.refresh(db_content)
        return db_content

    def delete_content(self, content_id: str):
        db_content = self.get_content(content_id)
        if db_content:
            self.db.delete(db_content)
            self.db.commit()
        return db_content
