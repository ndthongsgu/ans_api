from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.owner.owner_service import OwnerService
from schemas.owner.owner import Owner, OwnerCreate, OwnerUpdate

router = APIRouter()

@router.post("/owners/", response_model=Owner)
def create_owner(owner: OwnerCreate, db: Session = Depends(get_db)):
    service = OwnerService(db)
    return service.create_owner(owner)

@router.get("/owners/", response_model=list[Owner])
def list_owners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = OwnerService(db)
    return service.get_owners(skip=skip, limit=limit)

@router.get("/owners/{owner_id}", response_model=Owner)
def get_owner(owner_id: str, db: Session = Depends(get_db)):
    service = OwnerService(db)
    db_owner = service.get_owner(owner_id)
    if not db_owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    return db_owner

@router.put("/owners/{owner_id}", response_model=Owner)
def update_owner(owner_id: str, owner: OwnerUpdate, db: Session = Depends(get_db)):
    service = OwnerService(db)
    db_owner = service.update_owner(owner_id, owner)
    if not db_owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    return db_owner

@router.delete("/owners/{owner_id}")
def delete_owner(owner_id: str, db: Session = Depends(get_db)):
    service = OwnerService(db)
    db_owner = service.delete_owner(owner_id)
    if not db_owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    return {"detail": "Deleted"}
