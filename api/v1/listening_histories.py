from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.listening_history_service import ListeningHistoryService
from schemas.listening_history import ListeningHistory, ListeningHistoryCreate, ListeningHistoryUpdate

router = APIRouter()

@router.post("/listening-histories/", response_model=ListeningHistory)
def create_history(history: ListeningHistoryCreate, db: Session = Depends(get_db)):
    service = ListeningHistoryService(db)
    return service.create_history(history)

@router.get("/listening-histories/", response_model=list[ListeningHistory])
def list_histories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ListeningHistoryService(db)
    return service.get_histories(skip=skip, limit=limit)

@router.get("/listening-histories/{history_id}", response_model=ListeningHistory)
def get_history(history_id: str, db: Session = Depends(get_db)):
    service = ListeningHistoryService(db)
    db_history = service.get_history(history_id)
    if not db_history:
        raise HTTPException(status_code=404, detail="History not found")
    return db_history

@router.put("/listening-histories/{history_id}", response_model=ListeningHistory)
def update_history(history_id: str, history: ListeningHistoryUpdate, db: Session = Depends(get_db)):
    service = ListeningHistoryService(db)
    db_history = service.update_history(history_id, history)
    if not db_history:
        raise HTTPException(status_code=404, detail="History not found")
    return db_history

@router.delete("/listening-histories/{history_id}")
def delete_history(history_id: str, db: Session = Depends(get_db)):
    service = ListeningHistoryService(db)
    db_history = service.delete_history(history_id)
    if not db_history:
        raise HTTPException(status_code=404, detail="History not found")
    return {"detail": "Deleted"}
