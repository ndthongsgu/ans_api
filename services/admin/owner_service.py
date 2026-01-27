from sqlalchemy.orm import Session
from repositories.admin.owner_repository import OwnerRepository
from schemas.admin.owner import OwnerCreate, OwnerUpdate

class OwnerService:
    def __init__(self, db: Session):
        self.repository = OwnerRepository(db)

    def get_owner(self, owner_id: str):
        return self.repository.get_owner(owner_id)

    def get_owners(self, skip: int = 0, limit: int = 100):
        return self.repository.get_owners(skip, limit)

    def create_owner(self, owner: OwnerCreate):
        return self.repository.create_owner(owner)

    def update_owner(self, owner_id: str, owner: OwnerUpdate):
        return self.repository.update_owner(owner_id, owner)

    def delete_owner(self, owner_id: str):
        return self.repository.delete_owner(owner_id)
