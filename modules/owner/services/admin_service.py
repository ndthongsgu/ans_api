from sqlalchemy.orm import Session
from models.owner import Owner
from models.user import User
from models.role import Role
from models.userRole import UserRole
from utils.security import hash_password
import time
from typing import Tuple, List

class OwnerService:
    def __init__(self, db: Session):
        self.db = db

    def list_owners(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[Owner]]:
        q = self.db.query(Owner).join(User)
        
        if filters.get('full_name'):
            q = q.filter(Owner.full_name.ilike(f"%{filters['full_name']}%"))
            
        if filters.get('email'):
            q = q.filter(User.email.ilike(f"%{filters['email']}%"))
            
        if filters.get('phone'):
            q = q.filter(Owner.phone.ilike(f"%{filters['phone']}%"))
            
        if filters.get('isDeleted') is not None:
            q = q.filter(User.is_deleted == filters['isDeleted'])
                
        # Ordering
        if sortBy:
            column = getattr(Owner, sortBy, None) or getattr(User, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
                    
        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_owner(self, owner_id: str):
        return self.db.query(Owner).filter(Owner.id == owner_id).first()

    def create_owner(self, data: dict):
        # Check existing user/email
        if self.db.query(User).filter(User.email == data['email']).first():
            raise RuntimeError('email_exists')
            
        # Create user
        user = User(
            username=data['email'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            created_at=int(time.time())
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Assign OWNER role
        owner_role = self.db.query(Role).filter(Role.code == "OWNER").first()
        if owner_role:
            ur = UserRole(user_id=user.id, role_id=owner_role.id, code=owner_role.code)
            self.db.add(ur)
        
        # Create owner profile
        owner = Owner(
            user_id=user.id,
            full_name=data['full_name'],
            phone=data.get('phone'),
            business_name=data.get('business_name'),
            business_address=data.get('business_address'),
            created_at=int(time.time())
        )
        self.db.add(owner)
        self.db.commit()
        self.db.refresh(owner)
        return owner

    def update_owner(self, owner_id: str, data: dict):
        owner = self.get_owner(owner_id)
        if not owner:
            return None
            
        user = owner.user
        
        # Update user email/username
        if data.get('email') and data['email'] != user.email:
            if self.db.query(User).filter(User.email == data['email']).first():
                raise RuntimeError('email_exists')
            user.email = data['email']
            user.username = data['email']
            
        # Update owner fields
        owner.full_name = data['full_name']
        owner.phone = data.get('phone')
        owner.business_name = data.get('business_name')
        owner.business_address = data.get('business_address')
        
        self.db.commit()
        return owner

    def deactivate_owner(self, owner_id: str):
        owner = self.get_owner(owner_id)
        if owner and owner.user:
            owner.user.is_deleted = True
            self.db.commit()
        return owner

    def activate_owner(self, owner_id: str):
        owner = self.get_owner(owner_id)
        if owner and owner.user:
            owner.user.is_deleted = False
            self.db.commit()
        return owner

    def list_all_active(self):
        return self.db.query(Owner).join(User).filter(User.is_deleted == False).all()

    def list_for_select(self):
        """Return owners formatted for select dropdown"""
        owners = self.list_all_active()
        return [
            {
                "id": o.id,
                "full_name": o.full_name,
                "phone": o.phone or "",
                "userId": o.user_id
            }
            for o in owners
        ]