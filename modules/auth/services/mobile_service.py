from sqlalchemy.orm import Session
from models.customer import Customer
from models.user import User
from modules.auth.dto.mobile_dto import RegisterRequest, UserCreate
from utils.security import hash_password, verify_password
import time
from google.auth.transport import requests
from google.oauth2 import id_token
import logging


logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """Service-level error with a machine-readable code."""
    def __init__(self, code: str, message: str | None = None):
        self.code = code
        self.message = message  # Store detailed error message
        super().__init__(message or code)


class MobileService:
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
            raise ServiceError('username_exists')
        if self.find_by_email(register_request.email):
            raise ServiceError('email_exists')

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

    def create_customer_with_hashed_password(self, username: str | None, email: str, password_hash: str, full_name: str):
        # Check if user already exists
        if username and self.find_by_username(username):
            raise ServiceError('username_exists')
        if self.find_by_email(email):
            raise ServiceError('email_exists')

        user = User(
            username=username or email,
            email=email,
            password_hash=password_hash,
            created_at=int(time.time())
        )
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
        except Exception as exc:
            self.db.rollback()
            # map common duplicate key errors
            if 'Duplicate entry' in str(exc) and 'users.username' in str(exc):
                raise ServiceError('username_exists')
            if 'Duplicate entry' in str(exc) and 'users.email' in str(exc):
                raise ServiceError('email_exists')
            raise ServiceError('create_user_failed')

        customer = Customer(
            user_id=user.id,
            full_name=full_name
        )
        self.db.add(customer)
        try:
            self.db.commit()
            self.db.refresh(customer)
        except Exception as exc:
            self.db.rollback()
            raise ServiceError('create_customer_failed')

        return user, customer

    def change_password_by_email(self, email: str, password_hash: str):
        user = self.find_by_email(email)
        if not user:
            raise ServiceError('user_not_found')
        user.password_hash = password_hash
        self.db.commit()
        return user

    def change_password(self, user_id: str, current_password: str, new_password: str):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ServiceError('user_not_found')

        if not user.password_hash:
            raise ServiceError('invalid_credentials')

        if not verify_password(current_password, user.password_hash):
            raise ServiceError('invalid_credentials')

        user.password_hash = hash_password(new_password)
        self.db.commit()
        return user

    def get_customer_profile(self, user_id: str):
        customer = self.db.query(Customer).filter(Customer.user_id == user_id).first()
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if customer:
            customer.email = user.email
        return customer

    def update_profile(self, user_id: str, full_name: str | None = None, email: str | None = None, phone: str | None = None, avatar_url: str | None = None):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ServiceError('user_not_found')

        if email and email != user.email:
            if self.find_by_email(email):
                raise ServiceError('email_exists')
            if self.find_by_username(email) and self.find_by_username(email).id != user_id:
                raise ServiceError('username_exists')
            user.email = email
            user.username = email

        customer = self.db.query(Customer).filter(Customer.user_id == user_id).first()
        if full_name:
            if customer:
                customer.full_name = full_name
            else:
                customer = Customer(user_id=user_id, full_name=full_name)
                self.db.add(customer)
        if phone is not None:
            if customer:
                customer.phone = phone
        if avatar_url is not None:
            if customer:
                customer.avatar_url = avatar_url

        self.db.add(user)
        if customer:
            self.db.add(customer)

        try:
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            if 'Duplicate entry' in str(exc) and 'users.email' in str(exc):
                raise ServiceError('email_exists')
            if 'Duplicate entry' in str(exc) and 'users.username' in str(exc):
                raise ServiceError('username_exists')
            raise ServiceError('update_profile_failed')

        return {'email': user.email, 'full_name': customer.full_name if customer else None, 'phone': customer.phone if customer else None, 'avatar_url': customer.avatar_url if customer else None}

    def verify_google_token(self, id_token_str: str) -> dict:
        """Verify Google ID token and return user info"""
        try:
            # Verify token without strict audience check (accepts any valid Google token)
            # Added clock_skew_in_seconds to handle minor time differences between client and server
            idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), clock_skew_in_seconds=10)
            # Optionally verify it's a Google token
            if idinfo.get('iss') not in ['https://accounts.google.com', 'accounts.google.com']:
                raise ValueError('Not a Google token')
            return idinfo
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"Invalid token: {error_msg}")
            raise ServiceError('invalid_google_token', message=error_msg)

    def authenticate_with_google(self, id_token_str: str) -> User:
        """Authenticate user with Google ID token, create if not exists"""
        # Verify the token
        idinfo = self.verify_google_token(id_token_str)

        email = idinfo.get("email")
        full_name = idinfo.get("name", "")
        google_id = idinfo.get("sub")

        if not email:
            raise ServiceError('google_email_not_provided')

        # Find or create customer user
        user = self.find_by_email(email)

        if not user:
            # Create new user and customer profile
            user = User(email=email, username=email.split("@")[0], created_at=int(time.time()))
            self.db.add(user)
            self.db.flush()

            customer = Customer(user_id=user.id, full_name=full_name)
            self.db.add(customer)
            self.db.commit()
        else:
            # Update customer profile if needed
            customer = self.get_customer_profile(user.id)
            if customer and not customer.full_name and full_name:
                customer.full_name = full_name
                self.db.commit()
            elif not customer and full_name:
                # Create customer profile if missing
                customer = Customer(user_id=user.id, full_name=full_name)
                self.db.add(customer)
                self.db.commit()

        return user

    def login_or_create_by_device(self, device_id: str):
        user = self.db.query(User).filter(User.device_id == device_id).first()
        if not user:
            user = User(
                username=f"user_{device_id[:8]}",
                device_id=device_id,
                password_hash=hash_password(device_id),
                is_admin=False,
                created_at=int(time.time())
            )
            self.db.add(user)
            self.db.flush()

            customer = Customer(user_id=user.id, full_name=f"Device User {device_id[:8]}")
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(user)
            return user
        
        customer = self.db.query(Customer).filter(Customer.user_id == user.id).first()
        if not customer:
            customer = Customer(user_id=user.id, full_name=user.username)
            self.db.add(customer)
            self.db.commit()
        
        return user
