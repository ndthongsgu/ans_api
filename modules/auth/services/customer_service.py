from sqlalchemy.orm import Session
from models.customer import Customer
from models.user import User
from modules.auth.dto.customer_dto import RegisterRequest, UserCreate
from utils.security import hash_password, verify_password
import time

class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_customer(self, email: str, password: str):
        user = self.db.query(User).filter(
            (User.username == email) | (User.email == email)
        ).first()
        if user and verify_password(password, user.password_hash):
            return user
        return None

    def find_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def find_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create_customer(self, register_request: RegisterRequest):
        # Check if user already exists
        if register_request.username and self.find_by_username(register_request.username):
            raise ValueError("Username already exists")
        if self.find_by_email(register_request.email):
            raise ValueError("Email already exists")

        # Create user
        user_create = UserCreate(
            username=register_request.username or register_request.email,
            email=register_request.email,
            password=register_request.password
        )
        hashed = hash_password(user_create.password)
        user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed,
            created_at=int(time.time())
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create customer profile
        customer = Customer(
            user_id=user.id,
            full_name=register_request.full_name
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        return user, customer

    def get_customer_profile(self, user_id: str):
        customer = self.db.query(Customer).filter(Customer.user_id == user_id).first()
        return customer
