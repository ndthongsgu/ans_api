from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.admin.user_role_service import UserRoleService
from schemas.admin.user_role import UserRole, UserRoleCreate, UserRoleUpdate

router = APIRouter()

@router.post("/user-roles/", response_model=UserRole)
def create_user_role(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    service = UserRoleService(db)
    return service.create_user_role(user_role)

@router.get("/user-roles/", response_model=list[UserRole])
def list_user_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = UserRoleService(db)
    return service.get_user_roles(skip=skip, limit=limit)

@router.get("/user-roles/{user_role_id}", response_model=UserRole)
def get_user_role(user_role_id: str, db: Session = Depends(get_db)):
    service = UserRoleService(db)
    db_user_role = service.get_user_role(user_role_id)
    if not db_user_role:
        raise HTTPException(status_code=404, detail="UserRole not found")
    return db_user_role

@router.put("/user-roles/{user_role_id}", response_model=UserRole)
def update_user_role(user_role_id: str, user_role: UserRoleUpdate, db: Session = Depends(get_db)):
    service = UserRoleService(db)
    db_user_role = service.update_user_role(user_role_id, user_role)
    if not db_user_role:
        raise HTTPException(status_code=404, detail="UserRole not found")
    return db_user_role

@router.delete("/user-roles/{user_role_id}")
def delete_user_role(user_role_id: str, db: Session = Depends(get_db)):
    service = UserRoleService(db)
    db_user_role = service.delete_user_role(user_role_id)
    if not db_user_role:
        raise HTTPException(status_code=404, detail="UserRole not found")
    return {"detail": "Deleted"}
