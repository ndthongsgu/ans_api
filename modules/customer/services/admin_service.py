from sqlalchemy.orm import Session
from models.customer import Customer
from models.user import User
from models.role import Role
from models.userRole import UserRole
from utils.security import hash_password
import time
from typing import Tuple, List

class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def list_customers(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[Customer]]:
        q = self.db.query(Customer).join(User)
        
            
        if filters.get('name'):
            q = q.filter(Customer.full_name.ilike(f"%{filters['name']}%"))
            
        if filters.get('email'):
            q = q.filter(User.email.ilike(f"%{filters['email']}%"))
            
        if filters.get('phone'):
            q = q.filter(Customer.phone.ilike(f"%{filters['phone']}%"))
            
        if filters.get('isDeleted') is not None:
            if filters['isDeleted']:
                q = q.filter(User.is_active == False)
            else:
                q = q.filter(User.is_active == True)
                
        if filters.get('customerTypeId'):
            # Adjust based on your Customer model relationship
            pass
            
        # Ordering
        if sortBy:
            column = getattr(Customer, sortBy, None) or getattr(User, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
                    
        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_customer(self, customer_id: str):
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def create_customer(self, data: dict):
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
        
        # Assign CUSTOMER role
        customer_role = self.db.query(Role).filter(Role.code == "CUSTOMER").first()
        if customer_role:
            ur = UserRole(user_id=user.id, role_id=customer_role.id, code=customer_role.code)
            self.db.add(ur)
        
        # Create customer profile
        customer = Customer(
            user_id=user.id,
            full_name=data['name'],
            phone=data.get('phone'),
            notification_enabled=True,
            created_at=int(time.time())
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update_customer(self, customer_id: str, data: dict):
        customer = self.get_customer(customer_id)
        if not customer:
            return None
            
        user = customer.user
        
        # Update user email/username
        if data.get('email') and data['email'] != user.email:
            if self.db.query(User).filter(User.email == data['email']).first():
                raise RuntimeError('email_exists')
            user.email = data['email']
            user.username = data['email']
            
        # Update customer fields
        customer.full_name = data['name']
        customer.phone = data.get('phone')
        
        self.db.commit()
        return customer

    def deactivate_customer(self, customer_id: str):
        customer = self.get_customer(customer_id)
        if customer and customer.user:
            customer.user.is_active = False
            self.db.commit()
        return customer

    def activate_customer(self, customer_id: str):
        customer = self.get_customer(customer_id)
        if customer and customer.user:
            customer.user.is_active = True
            self.db.commit()
        return customer

    def delete_customer(self, customer_id: str):
        """Hard delete customer and associated user"""
        customer = self.get_customer(customer_id)
        if not customer:
            return None
            
        user = customer.user
        
        # Delete customer record
        self.db.delete(customer)
        
        # Delete associated user roles
        if user:
            self.db.query(UserRole).filter(UserRole.user_id == user.id).delete()
            # Delete user
            self.db.delete(user)
            
        self.db.commit()
        return True

    def list_all_active(self):
        return self.db.query(Customer).join(User).filter(User.is_active == True).all()

    def list_for_select(self):
        """Return customers formatted for select dropdown"""
        customers = self.list_all_active()
        return [
            {
                "id": c.id,
                "name": c.full_name,
                "phone": c.phone or "",
                "userId": c.user_id
            }
            for c in customers
        ]