import json
from sqlalchemy.orm import Session
from models.role import Role
from typing import Tuple, List
import time

class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def list_roles(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[Role]]:
        q = self.db.query(Role)
        
        if filters.get('code'):
            q = q.filter(Role.code.ilike(f"%{filters['code']}%"))
            
        if filters.get('name'):
            q = q.filter(Role.name.ilike(f"%{filters['name']}%"))
                
        # Ordering
        if sortBy:
            column = getattr(Role, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
                    
        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_role(self, role_id: str):
        return self.db.query(Role).filter(Role.id == role_id).first()

    def create_role(self, data: dict):
        # Check existing code
        if self.db.query(Role).filter(Role.code == data['code']).first():
            raise RuntimeError('code_exists')
        
        current_time = int(time.time())
        permissions = data.get('permissions')
        if isinstance(permissions, list):
            permissions = json.dumps(permissions, ensure_ascii=False)

        role = Role(
            code=data['code'],
            name=data['name'],
            permissions=permissions,
            created_at=current_time,
            updated_at=current_time,
            created_by=data.get('created_by'),
            is_deleted=False
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id: str, data: dict):
        role = self.get_role(role_id)
        if not role:
            return None
            
        # Check code uniqueness
        if data.get('code') and data['code'] != role.code:
            if self.db.query(Role).filter(Role.code == data['code']).first():
                raise RuntimeError('code_exists')
                
        role.code = data['code']
        role.name = data['name']
        permissions = data.get('permissions')
        if isinstance(permissions, list):
            permissions = json.dumps(permissions, ensure_ascii=False)
        role.permissions = permissions
        role.description = data.get('description')
        role.updated_at = int(time.time())
        role.updated_by = data.get('updated_by')
        
        self.db.commit()
        return role

    def deactivate_role(self, role_id: str):
        role = self.get_role(role_id)
        if role:
            role.is_deleted = True
            role.updated_at = int(time.time())
            self.db.commit()
        return role

    def activate_role(self, role_id: str):
        role = self.get_role(role_id)
        if role:
            role.is_deleted = False
            role.updated_at = int(time.time())
            self.db.commit()
        return self.get_role(role_id)

    def list_all_active(self):
        return self.db.query(Role).all()

    def list_for_select(self):
        """Return roles formatted for select dropdown"""
        roles = self.list_all_active()
        return [
            {
                "id": r.id,
                "code": r.code,
                "name": r.name
            }
            for r in roles
        ]