from sqlalchemy.orm import Session
from models.listeningHistory import ListeningHistory
from schemas.customer.listening_history import ListeningHistoryCreate, ListeningHistoryUpdate

class ListeningHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_history(self, history_id: str):
        return self.db.query(ListeningHistory).filter(ListeningHistory.id == history_id).first()

    def get_histories(self, skip: int = 0, limit: int = 100):
        return self.db.query(ListeningHistory).offset(skip).limit(limit).all()

    def create_history(self, history: ListeningHistoryCreate):
        db_history = ListeningHistory(
            user_id=history.user_id,
            stall_id=history.stall_id,
            stall_content_id=history.stall_content_id,
            listened_at=history.listened_at,
            listen_duration=history.listen_duration,
        )
        self.db.add(db_history)
        self.db.commit()
        self.db.refresh(db_history)
        return db_history

    def update_history(self, history_id: str, history: ListeningHistoryUpdate):
        db_history = self.get_history(history_id)
        if db_history:
            db_history.user_id = history.user_id
            db_history.stall_id = history.stall_id
            db_history.stall_content_id = history.stall_content_id
            db_history.listened_at = history.listened_at
            db_history.listen_duration = history.listen_duration
            self.db.commit()
            self.db.refresh(db_history)
        return db_history

    def delete_history(self, history_id: str):
        db_history = self.get_history(history_id)
        if db_history:
            self.db.delete(db_history)
            self.db.commit()
        return db_history
