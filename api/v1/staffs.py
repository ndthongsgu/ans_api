from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.staff_service import StaffService
from schemas.staff import Staff, StaffCreate, StaffUpdate

router = APIRouter()

@router.post("/staffs/", response_model=Staff)
def create_staff(staff: StaffCreate, db: Session = Depends(get_db)):
    service = StaffService(db)
    return service.create_staff(staff)

@router.get("/staffs/", response_model=list[Staff])
def list_staffs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = StaffService(db)
    return service.get_staffs(skip=skip, limit=limit)

@router.get("/staffs/{staff_id}", response_model=Staff)
def get_staff(staff_id: str, db: Session = Depends(get_db)):
    service = StaffService(db)
    db_staff = service.get_staff(staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return db_staff

@router.put("/staffs/{staff_id}", response_model=Staff)
def update_staff(staff_id: str, staff: StaffUpdate, db: Session = Depends(get_db)):
    service = StaffService(db)
    db_staff = service.update_staff(staff_id, staff)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return db_staff

@router.delete("/staffs/{staff_id}")
def delete_staff(staff_id: str, db: Session = Depends(get_db)):
    service = StaffService(db)
    db_staff = service.delete_staff(staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"detail": "Deleted"}
