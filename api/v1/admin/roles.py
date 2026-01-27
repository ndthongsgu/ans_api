from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.admin.role_service import RoleService
from schemas.admin.role import Role, RoleCreate, RoleUpdate

router = APIRouter()

@router.post("/roles/", response_model=Role)
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    service = RoleService(db)
    return service.create_role(role)

@router.get("/roles/", response_model=list[Role])
def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = RoleService(db)
    return service.get_roles(skip=skip, limit=limit)

@router.get("/roles/{role_id}", response_model=Role)
def get_role(role_id: str, db: Session = Depends(get_db)):
    service = RoleService(db)
    db_role = service.get_role(role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/roles/{role_id}", response_model=Role)
def update_role(role_id: str, role: RoleUpdate, db: Session = Depends(get_db)):
    service = RoleService(db)
    db_role = service.update_role(role_id, role)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.delete("/roles/{role_id}")
def delete_role(role_id: str, db: Session = Depends(get_db)):
    service = RoleService(db)
    db_role = service.delete_role(role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"detail": "Deleted"}
