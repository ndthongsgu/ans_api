from sqlalchemy.orm import Session
from models.area import Area
from schemas.admin.area import AreaCreate, AreaUpdate

class AreaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_area(self, area_id: str):
        return self.db.query(Area).filter(Area.id == area_id).first()

    def get_areas(self, skip: int = 0, limit: int = 100):
        return self.db.query(Area).offset(skip).limit(limit).all()

    def create_area(self, area: AreaCreate):
        db_area = Area(
            name=area.name,
            description=area.description,
            image_url=area.image_url,
            center_lat=area.center_lat,
            center_long=area.center_long,
            radius=area.radius,
        )
        self.db.add(db_area)
        self.db.commit()
        self.db.refresh(db_area)
        return db_area

    def update_area(self, area_id: str, area: AreaUpdate):
        db_area = self.get_area(area_id)
        if db_area:
            db_area.name = area.name
            db_area.description = area.description
            db_area.image_url = area.image_url
            db_area.center_lat = area.center_lat
            db_area.center_long = area.center_long
            db_area.radius = area.radius
            self.db.commit()
            self.db.refresh(db_area)
        return db_area

    def delete_area(self, area_id: str):
        db_area = self.get_area(area_id)
        if db_area:
            self.db.delete(db_area)
            self.db.commit()
        return db_area
