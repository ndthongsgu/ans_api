from sqlalchemy.orm import Session
from models.role import Role
from schemas.role import RoleCreate, RoleUpdate

class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_role(self, role_id: str):
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_roles(self, skip: int = 0, limit: int = 100):
        return self.db.query(Role).offset(skip).limit(limit).all()

    def create_role(self, role: RoleCreate):
        db_role = Role(code=role.code, name=role.name, permissions=role.permissions)
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role

    def update_role(self, role_id: str, role: RoleUpdate):
        db_role = self.get_role(role_id)
        if db_role:
            db_role.code = role.code
            db_role.name = role.name
            db_role.permissions = role.permissions
            self.db.commit()
            self.db.refresh(db_role)
        return db_role

    def delete_role(self, role_id: str):
        db_role = self.get_role(role_id)
        if db_role:
            self.db.delete(db_role)
            self.db.commit()
        return db_role
