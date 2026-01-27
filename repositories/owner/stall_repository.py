from sqlalchemy.orm import Session
from models.stall import Stall
from schemas.owner.stall import StallCreate, StallUpdate

class StallRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_stall(self, stall_id: str):
        return self.db.query(Stall).filter(Stall.id == stall_id).first()

    def get_stalls(self, skip: int = 0, limit: int = 100):
        return self.db.query(Stall).offset(skip).limit(limit).all()

    def create_stall(self, stall: StallCreate):
        db_stall = Stall(
            area_id=stall.area_id,
            owner_id=stall.owner_id,
            name=stall.name,
            latitude=stall.latitude,
            longitude=stall.longitude,
            radius=stall.radius,
            cover_image=stall.cover_image,
            status=stall.status,
        )
        self.db.add(db_stall)
        self.db.commit()
        self.db.refresh(db_stall)
        return db_stall

    def update_stall(self, stall_id: str, stall: StallUpdate):
        db_stall = self.get_stall(stall_id)
        if db_stall:
            db_stall.area_id = stall.area_id
            db_stall.owner_id = stall.owner_id
            db_stall.name = stall.name
            db_stall.latitude = stall.latitude
            db_stall.longitude = stall.longitude
            db_stall.radius = stall.radius
            db_stall.cover_image = stall.cover_image
            db_stall.status = stall.status
            self.db.commit()
            self.db.refresh(db_stall)
        return db_stall

    def delete_stall(self, stall_id: str):
        db_stall = self.get_stall(stall_id)
        if db_stall:
            self.db.delete(db_stall)
            self.db.commit()
        return db_stall
