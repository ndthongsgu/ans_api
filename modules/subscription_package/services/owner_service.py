import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus, urlencode

from sqlalchemy.orm import Session

from core.config import (
    VNPAY_ENDPOINT,
    VNPAY_HASH_SECRET,
    VNPAY_LOCALE,
    VNPAY_ORDER_TYPE,
    VNPAY_RETURN_URL,
    VNPAY_TMN_CODE,
)
from models.owner import Owner
from models.subscription_package import SubscriptionPackage
from models.subscription_transaction import SubscriptionTransaction
from modules.subscription_package.dto.owner_dto import SubscriptionRegisterRequest


class ServiceError(Exception):
    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code)


class OwnerSubscriptionPackageService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_owner(self, user_id: str) -> Owner:
        owner = self.db.query(Owner).filter(Owner.user_id == user_id).first()
        if not owner:
            raise ServiceError("profile_not_found")
        return owner

    def _get_package(self, package_id: str) -> SubscriptionPackage:
        package = (
            self.db.query(SubscriptionPackage)
            .filter(SubscriptionPackage.id == package_id, SubscriptionPackage.is_deleted == False)
            .first()
        )
        if not package:
            raise ServiceError("package_not_found")
        return package

    def _package_to_dict(self, package: SubscriptionPackage) -> dict:
        return {
            "id": package.id,
            "code": package.code,
            "name": package.name,
            "price": float(package.price or 0),
            "max_stalls": package.max_stalls,
            "duration_days": package.duration_days,
            "description": package.description,
            "is_deleted": package.is_deleted,
            "created_at": package.created_at,
            "updated_at": package.updated_at,
        }

    def get_my_subscription(self, user_id: str) -> dict:
        owner = self._ensure_owner(user_id)
        package = None
        if owner.subscription_package_id:
            package = (
                self.db.query(SubscriptionPackage)
                .filter(
                    SubscriptionPackage.id == owner.subscription_package_id,
                    SubscriptionPackage.is_deleted == False,
                )
                .first()
            )

        now = int(time.time())
        expires_at = owner.subscription_expires_at
        is_active = bool(expires_at and expires_at > now)

        latest_completed_transaction = (
            self.db.query(SubscriptionTransaction)
            .filter(
                SubscriptionTransaction.owner_id == owner.id,
                SubscriptionTransaction.payment_status == "completed",
            )
            .order_by(SubscriptionTransaction.created_at.desc())
            .first()
        )

        return {
            "owner_id": owner.id,
            "subscription_package_id": owner.subscription_package_id,
            "is_active": is_active,
            "subscription_start_at": latest_completed_transaction.subscription_start_at if latest_completed_transaction else None,
            "subscription_expires_at": expires_at,
            "remaining_seconds": max((expires_at or 0) - now, 0) if expires_at else 0,
            "package": self._package_to_dict(package) if package else None,
        }

    def _transaction_to_dict(self, transaction: SubscriptionTransaction, package: SubscriptionPackage) -> dict:
        return {
            "id": transaction.id,
            "transaction_code": transaction.transaction_code,
            "order_id": transaction.order_id,
            "request_id": transaction.request_id,
            "owner_id": transaction.owner_id,
            "subscription_package_id": transaction.subscription_package_id,
            "package_code": package.code,
            "package_name": package.name,
            "amount": float(transaction.amount or 0),
            "currency": transaction.currency,
            "payment_method": transaction.payment_method,
            "payment_provider": transaction.payment_provider,
            "payment_status": transaction.payment_status,
            "payment_url": transaction.payment_url,
            "qr_code_url": transaction.qr_code_url,
            "vnpay_trans_id": transaction.vnpay_trans_id,
            "vnpay_response_code": transaction.vnpay_response_code,
            "subscription_start_at": transaction.subscription_start_at,
            "subscription_end_at": transaction.subscription_end_at,
            "paid_at": transaction.paid_at,
            "note": transaction.note,
            "created_at": transaction.created_at,
            "updated_at": transaction.updated_at,
        }

    def list_packages(self) -> list[dict]:
        packages = (
            self.db.query(SubscriptionPackage)
            .filter(SubscriptionPackage.is_deleted == False)
            .order_by(SubscriptionPackage.price.asc(), SubscriptionPackage.max_stalls.asc())
            .all()
        )
        return [self._package_to_dict(package) for package in packages]

    def list_transactions(self, user_id: str, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        owner = self._ensure_owner(user_id)
        query = (
            self.db.query(SubscriptionTransaction)
            .filter(SubscriptionTransaction.owner_id == owner.id)
            .order_by(SubscriptionTransaction.created_at.desc())
        )

        total = query.count()
        rows = query.offset(skip).limit(limit).all()
        data: list[dict] = []
        for row in rows:
            package = self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == row.subscription_package_id).first()
            if package:
                data.append(self._transaction_to_dict(row, package))
        return data, total

    def _build_vnpay_hash_data(self, params: dict) -> str:
        filtered_params = {
            str(key): str(value)
            for key, value in params.items()
            if value is not None and str(value) != ""
        }
        sorted_items = sorted(filtered_params.items())
        return "&".join(f"{key}={quote_plus(value, safe='')}" for key, value in sorted_items)

    def _build_vnpay_secure_hash(self, params: dict) -> str:
        hash_data = self._build_vnpay_hash_data(params)
        return hmac.new(
            VNPAY_HASH_SECRET.encode("utf-8"),
            hash_data.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

    def _create_vnpay_payment(self, transaction: SubscriptionTransaction, owner: Owner, package: SubscriptionPackage) -> dict:
        if not VNPAY_TMN_CODE.strip() or not VNPAY_HASH_SECRET.strip() or not VNPAY_ENDPOINT.strip():
            raise ServiceError("subscription_failed", "Missing VNPay credentials")

        utc7 = timezone(timedelta(hours=7))
        create_date = datetime.now(utc7).strftime("%Y%m%d%H%M%S")
        expire_date = (datetime.now(utc7) + timedelta(minutes=15)).strftime("%Y%m%d%H%M%S")

        request_data = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": VNPAY_TMN_CODE.strip(),
            "vnp_Amount": str(int(round(float(transaction.amount) * 100))),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": transaction.order_id,
            "vnp_OrderInfo": f"Subscription package {package.code} for owner {owner.id}",
            "vnp_OrderType": VNPAY_ORDER_TYPE,
            "vnp_Locale": VNPAY_LOCALE,
            "vnp_ReturnUrl": VNPAY_RETURN_URL,
            "vnp_IpAddr": "127.0.0.1",
            "vnp_CreateDate": create_date,
            "vnp_ExpireDate": expire_date,
        }

        secure_hash = self._build_vnpay_secure_hash(request_data)
        query_string = urlencode(sorted(request_data.items()))
        payment_url = f"{VNPAY_ENDPOINT}?{query_string}&vnp_SecureHash={secure_hash}"
        return {"payUrl": payment_url, "qrCodeUrl": payment_url}

    def register_package(self, user_id: str, payload: SubscriptionRegisterRequest) -> dict:
        owner = self._ensure_owner(user_id)
        package = self._get_package(payload.subscription_package_id)
        now = int(time.time())
        subscription_start_at = now
        subscription_end_at = now + int(package.duration_days or 0) * 24 * 60 * 60

        transaction = SubscriptionTransaction(
            owner_id=owner.id,
            subscription_package_id=package.id,
            transaction_code=f"SUB-{uuid.uuid4().hex[:18].upper()}",
            order_id=f"VNPAY-{uuid.uuid4().hex[:20].upper()}",
            request_id=f"REQ-{uuid.uuid4().hex[:20].upper()}",
            amount=package.price,
            currency="VND",
            payment_method="vnpay",
            payment_provider="vnpay",
            payment_status="pending",
            subscription_start_at=subscription_start_at,
            subscription_end_at=subscription_end_at,
            note=payload.note,
            raw_payload=json.dumps(payload.model_dump(), ensure_ascii=False),
            created_at=now,
            updated_at=now,
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        try:
            vnpay_response = self._create_vnpay_payment(transaction, owner, package)
        except ServiceError as exc:
            transaction.payment_status = "failed"
            transaction.vnpay_raw_response = json.dumps({"error": getattr(exc, "detail", None) or exc.code}, ensure_ascii=False)
            transaction.updated_at = int(time.time())
            self.db.commit()
            raise

        transaction.payment_url = vnpay_response.get("payUrl")
        transaction.qr_code_url = vnpay_response.get("qrCodeUrl") or vnpay_response.get("payUrl")
        transaction.vnpay_raw_response = json.dumps(vnpay_response, ensure_ascii=False)
        if not transaction.payment_url:
            transaction.payment_status = "failed"
            transaction.updated_at = int(time.time())
            self.db.commit()
            raise ServiceError("subscription_failed", "VNPay did not return payUrl")
        transaction.updated_at = int(time.time())
        self.db.commit()
        self.db.refresh(transaction)

        return {
            "package": self._package_to_dict(package),
            "transaction": self._transaction_to_dict(transaction, package),
            "payment_url": transaction.payment_url,
            "qr_code_url": transaction.qr_code_url,
        }

    def handle_vnpay_ipn(self, payload: dict) -> dict:
        if not VNPAY_HASH_SECRET.strip():
            raise ServiceError("subscription_failed", "Missing VNPay hash secret")

        secure_hash = payload.get("vnp_SecureHash")
        if not secure_hash:
            raise ServiceError("subscription_failed", "Missing VNPay secure hash")

        signed_payload = {
            key: value
            for key, value in payload.items()
            if key not in {"vnp_SecureHash", "vnp_SecureHashType"}
        }
        expected_secure_hash = self._build_vnpay_secure_hash(signed_payload)
        if secure_hash.lower() != expected_secure_hash.lower():
            raise ServiceError("subscription_failed", "Invalid VNPay secure hash")

        order_id = payload.get("vnp_TxnRef")
        if not order_id:
            raise ServiceError("subscription_failed", "Missing vnp_TxnRef")

        transaction = (
            self.db.query(SubscriptionTransaction)
            .filter(SubscriptionTransaction.order_id == order_id)
            .first()
        )
        if not transaction:
            raise ServiceError("subscription_failed", "Transaction not found")

        if transaction.payment_status == "completed":
            return {"RspCode": "00", "Message": "Confirm Success"}

        response_code = str(payload.get("vnp_ResponseCode") or "")
        transaction_status = str(payload.get("vnp_TransactionStatus") or "")
        amount_raw = payload.get("vnp_Amount")

        try:
            amount_value = int(str(amount_raw))
        except (TypeError, ValueError):
            amount_value = -1

        expected_amount = int(round(float(transaction.amount) * 100))
        transaction.vnpay_response_code = response_code or None
        transaction.vnpay_trans_id = str(payload.get("vnp_TransactionNo")) if payload.get("vnp_TransactionNo") is not None else None
        transaction.vnpay_raw_response = json.dumps(payload, ensure_ascii=False)
        transaction.updated_at = int(time.time())

        owner = self.db.query(Owner).filter(Owner.id == transaction.owner_id).first()
        package = self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == transaction.subscription_package_id).first()
        if not owner or not package:
            raise ServiceError("subscription_failed", "Owner/package not found")

        if response_code == "00" and transaction_status == "00" and amount_value == expected_amount:
            now = int(time.time())
            owner.subscription_package_id = package.id
            owner.subscription_expires_at = transaction.subscription_end_at
            owner.updated_at = now
            transaction.payment_status = "completed"
            transaction.paid_at = now
        else:
            transaction.payment_status = "failed"

        self.db.commit()
        return {"RspCode": "00", "Message": "Confirm Success"}
