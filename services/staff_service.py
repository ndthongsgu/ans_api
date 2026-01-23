from sqlalchemy.orm import Session
from repositories.staff_repository import StaffRepository
from schemas.staff import StaffCreate, StaffUpdate

class StaffService:
    def __init__(self, db: Session):
        self.repository = StaffRepository(db)

    def get_staff(self, staff_id: str):
        return self.repository.get_staff(staff_id)

    def get_staffs(self, skip: int = 0, limit: int = 100):
        return self.repository.get_staffs(skip, limit)

    def create_staff(self, staff: StaffCreate):
        return self.repository.create_staff(staff)

    def update_staff(self, staff_id: str, staff: StaffUpdate):
        return self.repository.update_staff(staff_id, staff)

    def delete_staff(self, staff_id: str):
        return self.repository.delete_staff(staff_id)
