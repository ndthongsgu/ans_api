from sqlalchemy.orm import Session
from models.user import User
from schemas.admin.user import UserCreate, UserUpdate
import time
from utils.security import hash_password

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.db.query(User).offset(skip).limit(limit).all()

    def find_by_username_or_email(self, username_or_email: str):
        return self.db.query(User).filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

    def create_user(self, user: UserCreate):
        password_hash = hash_password(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=password_hash,
            created_at=int(time.time()),
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: str, user: UserUpdate):
        db_user = self.get_user(user_id)
        if db_user:
            if user.password:
                db_user.password_hash = hash_password(user.password)
            db_user.username = user.username
            db_user.email = user.email
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: str):
        db_user = self.get_user(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
        return db_user
