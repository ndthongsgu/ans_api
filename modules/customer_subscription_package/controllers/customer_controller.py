from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List
from sqlalchemy.orm import Session
from core.database import get_db
from modules.customer_subscription_package.services.customer_service import SubscriptionService, ServiceError
from modules.customer_subscription_package.dto.customer_dto import PackageOut, SubscriptionOut
from modules.auth.controllers.customer_controller import get_current_user
from utils.i18n import t

router = APIRouter(prefix="/subscription-packages")

@router.get("/", response_model=List[PackageOut])
def list_packages(db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    service = CustomerService(db)
    pkgs = service.list_packages(active_only=True)
    return [PackageOut(id=p.id, name=p.name, description=p.description, price=float(p.price), duration=p.duration, features=p.features) for p in pkgs]

@router.get("/{pkg_id}", response_model=PackageOut)
def get_package(pkg_id: str, db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    service = CustomerService(db)
    p = service.get_package(pkg_id)
    if not p:
        raise HTTPException(status_code=404, detail=t('package_not_found', accept_language))
    return PackageOut(id=p.id, name=p.name, description=p.description, price=float(p.price), duration=p.duration, features=p.features)

# Customer endpoints
@router.post("/{pkg_id}/purchase")
def purchase_package(pkg_id: str, current_user: object = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    # current_user is a User model instance from auth
    service = CustomerService(db)
    try:
        customer = service.purchase_package(current_user.id, pkg_id)
        return {"message": t('purchase_success', accept_language), "expires_at": customer.subscription_expires_at}
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=t(e.code, accept_language))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=t(str(e), accept_language))

@router.get("/my-subscription", response_model=SubscriptionOut)
def my_subscription(current_user: object = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    service = CustomerService(db)
    s = service.get_customer_subscription(current_user.id)
    if s is None:
        raise HTTPException(status_code=404, detail=t('profile_not_found', accept_language))
    pkg = s['package']
    return SubscriptionOut(package_id=(pkg.id if pkg else None), package_name=(pkg.name if pkg else None), expires_at=s['expires_at'], active=s['active'])
