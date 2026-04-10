from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from common.dto.response import success_response
from core.database import get_db
from models.user import User
from core.dependencies import ensure_owner
from modules.auth.controllers.owner_controller import get_current_user
from modules.subscription_package.dto.owner_dto import SubscriptionRegisterRequest
from modules.subscription_package.services.owner_service import OwnerSubscriptionPackageService, ServiceError
from utils.i18n import t

router = APIRouter(prefix="/subscription-packages")


@router.get("")
def list_packages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_owner(current_user, db)
    service = OwnerSubscriptionPackageService(db)
    data = service.list_packages()
    return success_response(message="Lấy danh sách gói thành công", data=data)


@router.get("/my-subscription")
def my_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    ensure_owner(current_user, db)
    service = OwnerSubscriptionPackageService(db)
    try:
        data = service.get_my_subscription(current_user.id)
        return success_response(message="Lấy gói đăng ký hiện tại thành công", data=data)
    except ServiceError as exc:
        if exc.code == "profile_not_found":
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=getattr(exc, "detail", None) or t(exc.code, locale))


@router.get("/my-purchases")
def my_purchases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    ensure_owner(current_user, db)
    service = OwnerSubscriptionPackageService(db)
    try:
        data = service.get_my_purchases(current_user.id)
        return success_response(message="Lấy danh sách gói đã mua thành công", data=data)
    except ServiceError as exc:
        if exc.code == "profile_not_found":
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=getattr(exc, "detail", None) or t(exc.code, locale))


@router.post("/register")
def register_package(
    payload: SubscriptionRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    ensure_owner(current_user, db)
    service = OwnerSubscriptionPackageService(db)
    try:
        data = service.register_package(current_user.id, payload)
        return success_response(message="Tạo giao dịch thành công, vui lòng thanh toán", data=data, status_code=201)
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "package_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        if exc.code == "stall_count_not_met":
            raise HTTPException(status_code=422, detail=getattr(exc, "detail", None) or t(exc.code, locale))
        raise HTTPException(status_code=400, detail=getattr(exc, "detail", None) or t(exc.code, locale))


@router.post("/register/redirect")
def register_package_redirect(
    payload: SubscriptionRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    ensure_owner(current_user, db)
    service = OwnerSubscriptionPackageService(db)
    try:
        data = service.register_package(current_user.id, payload)
        payment_url = data.get("payment_url")
        if not payment_url:
            raise HTTPException(status_code=400, detail="payment_url_not_found")
        return RedirectResponse(url=payment_url, status_code=303)
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "package_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        if exc.code == "stall_count_not_met":
            raise HTTPException(status_code=422, detail=getattr(exc, "detail", None) or t(exc.code, locale))
        raise HTTPException(status_code=400, detail=getattr(exc, "detail", None) or t(exc.code, locale))




@router.post("/activate-purchase")
def activate_purchase(
    transaction_id: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    ensure_owner(current_user, db)
    service = OwnerSubscriptionPackageService(db)
    try:
        data = service.activate_purchase(current_user.id, transaction_id)
        print(f"[DEBUG] activate_purchase transaction_id: {transaction_id}")
        return success_response(message="Kích hoạt gói thành công", data=data)
    except ServiceError as exc:
        if exc.code == "profile_not_found":
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        if exc.code == "transaction_not_found":
            raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")
        if exc.code == "package_not_found":
            raise HTTPException(status_code=404, detail="Không tìm thấy gói")
        raise HTTPException(status_code=400, detail=getattr(exc, "detail", None) or t(exc.code, locale))


@router.api_route("/vnpay/ipn", methods=["GET", "POST"])
async def vnpay_ipn(request: Request, payload: dict | None = Body(default=None), db: Session = Depends(get_db)):
    service = OwnerSubscriptionPackageService(db)
    params = dict(request.query_params) if request.query_params else dict(payload or {})

    try:
        result = service.handle_vnpay_ipn(params)
        return result
    except ServiceError as exc:
        return {"RspCode": "99", "Message": getattr(exc, "detail", None) or exc.code}


@router.api_route("/vnpay/return", methods=["GET", "POST"])
async def vnpay_return(request: Request, payload: dict | None = Body(default=None), db: Session = Depends(get_db)):
    service = OwnerSubscriptionPackageService(db)
    params = dict(request.query_params) if request.query_params else dict(payload or {})

    try:
        service.handle_vnpay_ipn(params)
        return success_response(
            message="Xác nhận thanh toán thành công",
            data={
                "order_id": params.get("vnp_TxnRef"),
                "response_code": params.get("vnp_ResponseCode"),
                "transaction_status": params.get("vnp_TransactionStatus"),
            },
        )
    except ServiceError as exc:
        raise HTTPException(status_code=400, detail=getattr(exc, "detail", None) or exc.code)
