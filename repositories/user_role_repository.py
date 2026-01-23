from sqlalchemy.orm import Session
from models.userRole import UserRole
from schemas.user_role import UserRoleCreate, UserRoleUpdate

class UserRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_role(self, user_role_id: str):
        return self.db.query(UserRole).filter(UserRole.id == user_role_id).first()

    def get_user_roles(self, skip: int = 0, limit: int = 100):
        return self.db.query(UserRole).offset(skip).limit(limit).all()

    def create_user_role(self, user_role: UserRoleCreate):
        db_user_role = UserRole(user_id=user_role.user_id, role_id=user_role.role_id)
        self.db.add(db_user_role)
        self.db.commit()
        self.db.refresh(db_user_role)
        return db_user_role

    def update_user_role(self, user_role_id: str, user_role: UserRoleUpdate):
        db_user_role = self.get_user_role(user_role_id)
        if db_user_role:
            db_user_role.user_id = user_role.user_id
            db_user_role.role_id = user_role.role_id
            self.db.commit()
            self.db.refresh(db_user_role)
        return db_user_role

    def delete_user_role(self, user_role_id: str):
        db_user_role = self.get_user_role(user_role_id)
        if db_user_role:
            self.db.delete(db_user_role)
            self.db.commit()
        return db_user_role
