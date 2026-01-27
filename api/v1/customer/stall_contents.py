from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.customer.stall_content_service import StallContentService
from schemas.customer.stall_content import StallContent, StallContentCreate, StallContentUpdate

router = APIRouter()

@router.post("/stall-contents/", response_model=StallContent)
def create_content(content: StallContentCreate, db: Session = Depends(get_db)):
    service = StallContentService(db)
    return service.create_content(content)

@router.get("/stall-contents/", response_model=list[StallContent])
def list_contents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = StallContentService(db)
    return service.get_contents(skip=skip, limit=limit)

@router.get("/stall-contents/{content_id}", response_model=StallContent)
def get_content(content_id: str, db: Session = Depends(get_db)):
    service = StallContentService(db)
    db_content = service.get_content(content_id)
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    return db_content

@router.put("/stall-contents/{content_id}", response_model=StallContent)
def update_content(content_id: str, content: StallContentUpdate, db: Session = Depends(get_db)):
    service = StallContentService(db)
    db_content = service.update_content(content_id, content)
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    return db_content

@router.delete("/stall-contents/{content_id}")
def delete_content(content_id: str, db: Session = Depends(get_db)):
    service = StallContentService(db)
    db_content = service.delete_content(content_id)
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"detail": "Deleted"}
