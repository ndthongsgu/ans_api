from sqlalchemy.orm import Session
from repositories.user_role_repository import UserRoleRepository
from schemas.user_role import UserRoleCreate, UserRoleUpdate

class UserRoleService:
    def __init__(self, db: Session):
        self.repository = UserRoleRepository(db)

    def get_user_role(self, user_role_id: str):
        return self.repository.get_user_role(user_role_id)

    def get_user_roles(self, skip: int = 0, limit: int = 100):
        return self.repository.get_user_roles(skip, limit)

    def create_user_role(self, user_role: UserRoleCreate):
        return self.repository.create_user_role(user_role)

    def update_user_role(self, user_role_id: str, user_role: UserRoleUpdate):
        return self.repository.update_user_role(user_role_id, user_role)

    def delete_user_role(self, user_role_id: str):
        return self.repository.delete_user_role(user_role_id)
