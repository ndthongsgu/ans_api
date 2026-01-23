from sqlalchemy.orm import Session
from models.staff import Staff
from schemas.staff import StaffCreate, StaffUpdate

class StaffRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_staff(self, staff_id: str):
        return self.db.query(Staff).filter(Staff.id == staff_id).first()

    def get_staffs(self, skip: int = 0, limit: int = 100):
        return self.db.query(Staff).offset(skip).limit(limit).all()

    def create_staff(self, staff: StaffCreate):
        db_staff = Staff(full_name=staff.full_name, phone=staff.phone, user_id=staff.user_id)
        self.db.add(db_staff)
        self.db.commit()
        self.db.refresh(db_staff)
        return db_staff

    def update_staff(self, staff_id: str, staff: StaffUpdate):
        db_staff = self.get_staff(staff_id)
        if db_staff:
            db_staff.full_name = staff.full_name
            db_staff.phone = staff.phone
            db_staff.user_id = staff.user_id
            self.db.commit()
            self.db.refresh(db_staff)
        return db_staff

    def delete_staff(self, staff_id: str):
        db_staff = self.get_staff(staff_id)
        if db_staff:
            self.db.delete(db_staff)
            self.db.commit()
        return db_staff
