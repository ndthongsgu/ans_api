from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user(self, user_id: int):
        return self.repository.get_user(user_id)

    def get_users(self, skip: int = 0, limit: int = 100):
        return self.repository.get_users(skip, limit)

    def create_user(self, user: UserCreate):
        return self.repository.create_user(user)

    def update_user(self, user_id: int, user: UserUpdate):
        return self.repository.update_user(user_id, user)

    def delete_user(self, user_id: int):
        return self.repository.delete_user(user_id)
