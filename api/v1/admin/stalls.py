from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.admin.stall_service import StallService
from schemas.admin.stall import Stall, StallCreate, StallUpdate

router = APIRouter()

@router.post("/stalls/", response_model=Stall)
def create_stall(stall: StallCreate, db: Session = Depends(get_db)):
    service = StallService(db)
    return service.create_stall(stall)

@router.get("/stalls/", response_model=list[Stall])
def list_stalls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = StallService(db)
    return service.get_stalls(skip=skip, limit=limit)

@router.get("/stalls/{stall_id}", response_model=Stall)
def get_stall(stall_id: str, db: Session = Depends(get_db)):
    service = StallService(db)
    db_stall = service.get_stall(stall_id)
    if not db_stall:
        raise HTTPException(status_code=404, detail="Stall not found")
    return db_stall

@router.put("/stalls/{stall_id}", response_model=Stall)
def update_stall(stall_id: str, stall: StallUpdate, db: Session = Depends(get_db)):
    service = StallService(db)
    db_stall = service.update_stall(stall_id, stall)
    if not db_stall:
        raise HTTPException(status_code=404, detail="Stall not found")
    return db_stall

@router.delete("/stalls/{stall_id}")
def delete_stall(stall_id: str, db: Session = Depends(get_db)):
    service = StallService(db)
    db_stall = service.delete_stall(stall_id)
    if not db_stall:
        raise HTTPException(status_code=404, detail="Stall not found")
    return {"detail": "Deleted"}
