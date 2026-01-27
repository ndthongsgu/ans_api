from sqlalchemy.orm import Session
from repositories.customer.stall_repository import StallRepository
from schemas.customer.stall import StallCreate, StallUpdate

class StallService:
    def __init__(self, db: Session):
        self.repository = StallRepository(db)

    def get_stall(self, stall_id: str):
        return self.repository.get_stall(stall_id)

    def get_stalls(self, skip: int = 0, limit: int = 100):
        return self.repository.get_stalls(skip, limit)

    def create_stall(self, stall: StallCreate):
        return self.repository.create_stall(stall)

    def update_stall(self, stall_id: str, stall: StallUpdate):
        return self.repository.update_stall(stall_id, stall)

    def delete_stall(self, stall_id: str):
        return self.repository.delete_stall(stall_id)
