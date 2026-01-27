from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from services.owner.subscription_package_service import SubscriptionPackageService
from schemas.owner.subscription_package import SubscriptionPackage, SubscriptionPackageCreate, SubscriptionPackageUpdate

router = APIRouter()

@router.post("/subscription_packages/", response_model=SubscriptionPackage)
def create_subscription_package(package: SubscriptionPackageCreate, db: Session = Depends(get_db)):
    service = SubscriptionPackageService(db)
    return service.create_subscription_package(package)

@router.get("/subscription_packages/", response_model=list[SubscriptionPackage])
def list_subscription_packages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = SubscriptionPackageService(db)
    return service.get_subscription_packages(skip=skip, limit=limit)

@router.get("/subscription_packages/{package_id}", response_model=SubscriptionPackage)
def get_subscription_package(package_id: str, db: Session = Depends(get_db)):
    service = SubscriptionPackageService(db)
    db_package = service.get_subscription_package(package_id)
    if not db_package:
        raise HTTPException(status_code=404, detail="Subscription package not found")
    return db_package

@router.put("/subscription_packages/{package_id}", response_model=SubscriptionPackage)
def update_subscription_package(package_id: str, package: SubscriptionPackageUpdate, db: Session = Depends(get_db)):
    service = SubscriptionPackageService(db)
    db_package = service.update_subscription_package(package_id, package)
    if not db_package:
        raise HTTPException(status_code=404, detail="Subscription package not found")
    return db_package

@router.delete("/subscription_packages/{package_id}")
def delete_subscription_package(package_id: str, db: Session = Depends(get_db)):
    service = SubscriptionPackageService(db)
    db_package = service.delete_subscription_package(package_id)
    if not db_package:
        raise HTTPException(status_code=404, detail="Subscription package not found")
    return {"detail": "Deleted"}
