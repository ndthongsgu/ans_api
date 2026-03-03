from sqlalchemy.orm import Session
from models.user import User
from utils.security import verify_password

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_admin(self, username: str, password: str):
        # username parameter may be actual username or email address
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        # check role membership
        # user.roles is a list of UserRole objects with code attribute
        if not any(r.code == "ADMIN" for r in user.roles):
            return None
        return user
