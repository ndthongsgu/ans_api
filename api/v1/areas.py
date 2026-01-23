from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.area_service import AreaService
from schemas.area import Area, AreaCreate, AreaUpdate

router = APIRouter()

@router.post("/areas/", response_model=Area)
def create_area(area: AreaCreate, db: Session = Depends(get_db)):
    service = AreaService(db)
    return service.create_area(area)

@router.get("/areas/", response_model=list[Area])
def list_areas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = AreaService(db)
    return service.get_areas(skip=skip, limit=limit)

@router.get("/areas/{area_id}", response_model=Area)
def get_area(area_id: str, db: Session = Depends(get_db)):
    service = AreaService(db)
    db_area = service.get_area(area_id)
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")
    return db_area

@router.put("/areas/{area_id}", response_model=Area)
def update_area(area_id: str, area: AreaUpdate, db: Session = Depends(get_db)):
    service = AreaService(db)
    db_area = service.update_area(area_id, area)
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")
    return db_area

@router.delete("/areas/{area_id}")
def delete_area(area_id: str, db: Session = Depends(get_db)):
    service = AreaService(db)
    db_area = service.delete_area(area_id)
    if not db_area:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"detail": "Deleted"}
