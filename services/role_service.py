from sqlalchemy.orm import Session
from repositories.role_repository import RoleRepository
from schemas.role import RoleCreate, RoleUpdate

class RoleService:
    def __init__(self, db: Session):
        self.repository = RoleRepository(db)

    def get_role(self, role_id: str):
        return self.repository.get_role(role_id)

    def get_roles(self, skip: int = 0, limit: int = 100):
        return self.repository.get_roles(skip, limit)

    def create_role(self, role: RoleCreate):
        return self.repository.create_role(role)

    def update_role(self, role_id: str, role: RoleUpdate):
        return self.repository.update_role(role_id, role)

    def delete_role(self, role_id: str):
        return self.repository.delete_role(role_id)
