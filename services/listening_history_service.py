from sqlalchemy.orm import Session
from repositories.listening_history_repository import ListeningHistoryRepository
from schemas.listening_history import ListeningHistoryCreate, ListeningHistoryUpdate

class ListeningHistoryService:
    def __init__(self, db: Session):
        self.repository = ListeningHistoryRepository(db)

    def get_history(self, history_id: str):
        return self.repository.get_history(history_id)

    def get_histories(self, skip: int = 0, limit: int = 100):
        return self.repository.get_histories(skip, limit)

    def create_history(self, history: ListeningHistoryCreate):
        return self.repository.create_history(history)

    def update_history(self, history_id: str, history: ListeningHistoryUpdate):
        return self.repository.update_history(history_id, history)

    def delete_history(self, history_id: str):
        return self.repository.delete_history(history_id)
