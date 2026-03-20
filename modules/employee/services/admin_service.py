from sqlalchemy.orm import Session
from models.employee import Employee
from models.user import User
from models.role import Role
from models.userRole import UserRole
from utils.security import hash_password
import time
from typing import Tuple, List

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def list_employees(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[Employee]]:
        q = self.db.query(Employee).join(User)
        # apply basic filters
        if filters.get('code'):
            q = q.filter(Employee.code.ilike(f"%{filters['code']}%"))
        if filters.get('name'):
            q = q.filter(Employee.full_name.ilike(f"%{filters['name']}%"))
        if filters.get('email'):
            q = q.filter(User.email.ilike(f"%{filters['email']}%"))
        if filters.get('phone'):
            q = q.filter(Employee.phone.ilike(f"%{filters['phone']}%"))
        if filters.get('isDeleted') is not None:
            if filters['isDeleted']:
                q = q.filter(Employee.is_deleted == True)
            else:
                q = q.filter(Employee.is_deleted == False)
        # role filtering
        role_ids = filters.get('roleIds')
        if role_ids:
            # join roles and filter
            q = q.join(UserRole).filter(UserRole.role_id.in_(role_ids))
        # ordering
        if sortBy:
            column = getattr(Employee, sortBy, None) or getattr(User, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_employee(self, emp_id: str):
        return self.db.query(Employee).filter(Employee.id == emp_id).first()

    def create_employee(self, data: dict):
        # check existing user/email or employee code
        if self.db.query(User).filter(User.email == data['email']).first():
            raise RuntimeError('email_exists')
        if self.db.query(Employee).filter(Employee.code == data['code']).first():
            raise RuntimeError('code_exists')
        # create user with default password if not provided
        password = data.get('password', 'Temp@123456')  # default temporary password
        user = User(
            username=data['email'],
            email=data['email'],
            password_hash=hash_password(password),
            created_at=int(time.time())
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        # create employee profile
        emp = Employee(
            user_id=user.id,
            code=data['code'],
            full_name=data['name'],
            phone=data.get('phone'),
            description=data.get('description'),
            created_at=int(time.time())
        )
        self.db.add(emp)
        # add roles
        for rid in data.get('roleIds', []):
            role = self.db.query(Role).filter(Role.id == rid).first()
            if role:
                ur = UserRole(user_id=user.id, role_id=rid, code=role.code)
                self.db.add(ur)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def update_employee(self, emp_id: str, data: dict):
        emp = self.get_employee(emp_id)
        if not emp:
            return None
        user = emp.user
        # update user email/username
        if data.get('email') and data['email'] != user.email:
            if self.db.query(User).filter(User.email == data['email']).first():
                raise RuntimeError('email_exists')
            user.email = data['email']
            user.username = data['email']
        # update employee fields
        emp.code = data['code']
        emp.full_name = data['name']
        emp.phone = data.get('phone')
        emp.description = data.get('description')
        # update roles: remove all then add
        self.db.query(UserRole).filter(UserRole.user_id == user.id).delete()
        for rid in data.get('roleIds', []):
            role = self.db.query(Role).filter(Role.id == rid).first()
            if role:
                ur = UserRole(user_id=user.id, role_id=rid, code=role.code)
                self.db.add(ur)
        self.db.commit()
        return emp

    def deactivate_employee(self, emp_id: str):
        emp = self.get_employee(emp_id)
        if emp:
            emp.is_deleted = True
            if emp.user:
                emp.user.is_deleted = True
            self.db.commit()
        return emp

    def activate_employee(self, emp_id: str):
        emp = self.get_employee(emp_id)
        if emp:
            emp.is_deleted = False
            if emp.user:
                emp.user.is_deleted = False
            self.db.commit()
        return emp

    def list_all_active(self):
        return self.db.query(Employee).filter(Employee.is_deleted == False).all()
