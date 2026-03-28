from sqlalchemy.orm import Session
from models.user import User
from utils.security import verify_password, hash_password

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_admin(self, username: str, password: str):
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_admin:
            return None
        return user