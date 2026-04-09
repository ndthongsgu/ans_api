from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.subscription_package.services.admin_service import SubscriptionPackageService
from modules.subscription_package.dto.admin_dto import (
    SubscriptionPackagePageRequest,
    SubscriptionPackageCreate,
    SubscriptionPackageUpdate,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from common.dto.response import success_response

router = APIRouter(prefix="/subscription-packages")


def ensure_admin(user: User, locale: str | None = None):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")


@router.post("/pagination")
def paginate(req: SubscriptionPackagePageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    total, items = service.list_packages(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)

    results = []
    for p in items:
        results.append({
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "price": float(p.price),
            "max_stalls": p.max_stalls,
            "description": p.description,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "is_deleted": p.is_deleted,
        })

    return success_response(
        message="Lấy dữ liệu thành công",
        data={"content": results, "totalElements": total}
    )


@router.get("")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    packages = service.list_for_select()
    data = [
        {"id": p.id, "name": p.name, "code": p.code, "max_stalls": p.max_stalls}
        for p in packages
    ]
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )


@router.post("")
def create_package(package: SubscriptionPackageCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    try:
        pkg = service.create_package(package.dict())
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Tạo gói đăng ký thành công",
        status_code=201,
        data={
            "id": pkg.id,
            "name": pkg.name,
            "code": pkg.code,
            "price": float(pkg.price),
            "max_stalls": pkg.max_stalls,
            "description": pkg.description,
            "created_at": pkg.created_at,
            "updated_at": pkg.updated_at,
        }
    )


@router.put("/{package_id}")
def update_package(package_id: str, package: SubscriptionPackageUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    try:
        pkg = service.update_package(package_id, package.dict(exclude_unset=True))
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói đăng ký")
    return success_response(message="Cập nhật gói đăng ký thành công")


@router.get("/{package_id}")
def detail_package(package_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    pkg = service.get_package(package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói đăng ký")
    return success_response(
        message="Lấy dữ liệu thành công",
        data={
            "id": pkg.id,
            "name": pkg.name,
            "code": pkg.code,
            "price": float(pkg.price),
            "max_stalls": pkg.max_stalls,
            "description": pkg.description,
            "created_at": pkg.created_at,
            "updated_at": pkg.updated_at,
        }
    )


@router.post("/deactivate/{package_id}")
def deactivate_package(package_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    pkg = service.deactivate_package(package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói đăng ký")
    return success_response(message="Ngưng hoạt động gói đăng ký thành công")


@router.post("/activate/{package_id}")
def activate_package(package_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    pkg = service.activate_package(package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy gói đăng ký")
    return success_response(message="Kích hoạt gói đăng ký thành công")


@router.get("/select")
def select_package(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = SubscriptionPackageService(db)
    packages = service.list_for_select()
    data = [{"id": p.id, "name": p.name} for p in packages]
    return success_response(message="Lấy dữ liệu thành công", data=data)
