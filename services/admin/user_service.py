from sqlalchemy.orm import Session
from repositories.admin.user_repository import UserRepository
from schemas.admin.user import UserCreate, UserUpdate
from utils.security import verify_password

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user(self, user_id: str):
        return self.repository.get_user(user_id)

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.repository.get_users(skip, limit)

    def create_user(self, user: UserCreate):
        return self.repository.create_user(user)

    def update_user(self, user_id: str, user: UserUpdate):
        return self.repository.update_user(user_id, user)

    def delete_user(self, user_id: str):
        return self.repository.delete_user(user_id)

    def authenticate_user(self, username_or_email: str, password: str):
        user = self.repository.find_by_username_or_email(username_or_email)
        if not user or not user.password_hash:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
