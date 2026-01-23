from sqlalchemy.orm import Session
from repositories.area_repository import AreaRepository
from schemas.area import AreaCreate, AreaUpdate

class AreaService:
    def __init__(self, db: Session):
        self.repository = AreaRepository(db)

    def get_area(self, area_id: str):
        return self.repository.get_area(area_id)

    def get_areas(self, skip: int = 0, limit: int = 100):
        return self.repository.get_areas(skip, limit)

    def create_area(self, area: AreaCreate):
        return self.repository.create_area(area)

    def update_area(self, area_id: str, area: AreaUpdate):
        return self.repository.update_area(area_id, area)

    def delete_area(self, area_id: str):
        return self.repository.delete_area(area_id)
