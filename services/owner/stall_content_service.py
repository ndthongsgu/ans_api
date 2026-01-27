from sqlalchemy.orm import Session
from repositories.owner.stall_content_repository import StallContentRepository
from schemas.owner.stall_content import StallContentCreate, StallContentUpdate

class StallContentService:
    def __init__(self, db: Session):
        self.repository = StallContentRepository(db)

    def get_content(self, content_id: str):
        return self.repository.get_content(content_id)

    def get_contents(self, skip: int = 0, limit: int = 100):
        return self.repository.get_contents(skip, limit)

    def create_content(self, content: StallContentCreate):
        return self.repository.create_content(content)

    def update_content(self, content_id: str, content: StallContentUpdate):
        return self.repository.update_content(content_id, content)

    def delete_content(self, content_id: str):
        return self.repository.delete_content(content_id)
