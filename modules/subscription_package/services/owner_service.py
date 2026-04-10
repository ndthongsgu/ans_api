import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus, urlencode

from sqlalchemy.orm import Session
from sqlalchemy import func

from core.config import (
    VNPAY_ENDPOINT,
    VNPAY_HASH_SECRET,
    VNPAY_LOCALE,
    VNPAY_ORDER_TYPE,
    VNPAY_RETURN_URL,
    VNPAY_TMN_CODE,
)
from models.owner import Owner
from models.stall import Stall
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
            "description": package.description,
            "is_deleted": package.is_deleted,
            "created_at": package.created_at,
            "updated_at": package.updated_at,
        }

    def get_my_subscription(self, user_id: str) -> dict:
        owner = self._ensure_owner(user_id)

        latest_completed_transaction = (
            self.db.query(SubscriptionTransaction)
            .filter(
                SubscriptionTransaction.owner_id == owner.id,
                SubscriptionTransaction.payment_status == "success",
            )
            .order_by(SubscriptionTransaction.created_at.desc())
            .first()
        )

        if latest_completed_transaction and (
            owner.subscription_package_id != latest_completed_transaction.subscription_package_id
        ):
            owner.subscription_package_id = latest_completed_transaction.subscription_package_id
            owner.updated_at = int(time.time())
            self.db.commit()
            self.db.refresh(owner)

        package = None
        if latest_completed_transaction:
            package = (
                self.db.query(SubscriptionPackage)
                .filter(
                    SubscriptionPackage.id == latest_completed_transaction.subscription_package_id,
                    SubscriptionPackage.is_deleted == False,
                )
                .first()
            )

        if not package and owner.subscription_package_id:
            package = (
                self.db.query(SubscriptionPackage)
                .filter(
                    SubscriptionPackage.id == owner.subscription_package_id,
                    SubscriptionPackage.is_deleted == False,
                )
                .first()
            )

        now = int(time.time())
        is_active = False
        return {
            "owner_id": owner.id,
            "subscription_package_id": latest_completed_transaction.subscription_package_id if latest_completed_transaction else owner.subscription_package_id,
            "is_active": is_active,
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

    def get_my_purchases(self, user_id: str) -> list[dict]:
        """Trả về tất cả các gói đã từng mua (dựa vào subscription_transaction có owner_id), kèm transaction_id thành công gần nhất."""
        owner = self._ensure_owner(user_id)

        # Lấy tất cả transaction của owner, mọi trạng thái
        rows = (
            self.db.query(SubscriptionTransaction)
            .filter(SubscriptionTransaction.owner_id == owner.id)
            .order_by(SubscriptionTransaction.created_at.desc())
            .all()
        )

        # Gom các package_id đã mua (duy nhất), giữ thứ tự lần mua gần nhất
        seen_package_ids: set[str] = set()
        result: list[dict] = []
        for row in rows:
            pid = row.subscription_package_id
            if pid in seen_package_ids:
                continue
            seen_package_ids.add(pid)
            package = self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == pid).first()
            if package:
                # Tìm transaction thành công gần nhất cho package này
                success_tx = (
                    self.db.query(SubscriptionTransaction)
                    .filter(
                        SubscriptionTransaction.owner_id == owner.id,
                        SubscriptionTransaction.subscription_package_id == pid,
                        SubscriptionTransaction.payment_status == "success"
                    )
                    .order_by(SubscriptionTransaction.created_at.desc())
                    .first()
                )
                package_dict = self._package_to_dict(package)
                package_dict["transaction_id"] = success_tx.id if success_tx else None
                result.append(package_dict)
        return result

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
        sorted_params = dict(sorted(filtered_params.items()))
        return "&".join(
            f"{key}={quote_plus(str(value))}"
            for key, value in sorted_params.items()
)

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

        query_string = self._build_vnpay_hash_data(request_data)
        secure_hash = self._build_vnpay_secure_hash(request_data)
        payment_url = (
            f"{VNPAY_ENDPOINT}?{query_string}"
            f"&vnp_SecureHash={secure_hash}"
        )
        return {"payUrl": payment_url}


    def register_package(self, user_id: str, payload: SubscriptionRegisterRequest) -> dict:
        owner = self._ensure_owner(user_id)
        package = self._get_package(payload.subscription_package_id)

        # Kiểm tra: số lượng quán hiện tại phải <= max_stalls của gói mới
        current_stall_count = (
            self.db.query(func.count(Stall.id))
            .filter(Stall.owner_id == owner.id)
            .scalar()
        ) or 0
        if current_stall_count > package.max_stalls:
            raise ServiceError(
                "stall_count_not_met",
                f"Số lượng quán hiện tại ({current_stall_count}) vượt quá giới hạn của gói mới ({package.max_stalls}). Vui lòng xóa bớt quán trước khi chuyển gói.",
            )

        # Không cho đăng ký lại gói đã có transaction thành công
        existed = self.db.query(SubscriptionTransaction).filter(
            SubscriptionTransaction.owner_id == owner.id,
            SubscriptionTransaction.subscription_package_id == package.id,
            SubscriptionTransaction.payment_status == "success"
        ).first()
        if existed:
            raise ServiceError(
                "package_already_purchased",
                "Bạn đã đăng ký gói này thành công trước đó. Không thể đăng ký lại cùng một gói.",
            )

        now = int(time.time())
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
            payment_status="success",  
            raw_payload=json.dumps(payload.model_dump(), ensure_ascii=False),
            created_at=now,
            updated_at=now,
        )

        try:
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)

            vnpay_response = self._create_vnpay_payment(transaction, owner, package)
        except ServiceError as exc:
            transaction.payment_status = "failed"
            transaction.vnpay_raw_response = json.dumps({"error": getattr(exc, "detail", None) or exc.code}, ensure_ascii=False)
            transaction.updated_at = int(time.time())
            self.db.commit()
            raise

        transaction.payment_url = vnpay_response.get("payUrl")
        transaction.qr_code_url = vnpay_response.get("qrCodeUrl")
        transaction.vnpay_raw_response = json.dumps(vnpay_response, ensure_ascii=False)
        if not transaction.payment_url:
            transaction.payment_status = "failed"
            transaction.updated_at = int(time.time())
            self.db.commit()
            raise ServiceError("subscription_failed", "VNPay did not return payUrl")
        transaction.updated_at = int(time.time())

        # Nếu thanh toán thành công (mặc định luôn success), cập nhật owner.subscription_package_id
        if transaction.payment_status == "success":
            owner.subscription_package_id = package.id
            owner.updated_at = int(time.time())
            self.db.commit()
            self.db.refresh(owner)

        self.db.commit()
        self.db.refresh(transaction)

        return {
            "package": self._package_to_dict(package),
            "transaction": self._transaction_to_dict(transaction, package),
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

        if transaction.payment_status == "success":
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
            owner.updated_at = now
            transaction.payment_status = "success"
            transaction.paid_at = now
            self.db.commit()
            self.db.refresh(owner)
        else:
            transaction.payment_status = "failed"
            self.db.commit()
        return {"RspCode": "00", "Message": "Confirm Success"}

    def activate_purchase(self, user_id: str, transaction_id: str) -> dict:
        owner = self._ensure_owner(user_id)
        transaction = self.db.query(SubscriptionTransaction).filter(
            SubscriptionTransaction.id == transaction_id,
            SubscriptionTransaction.owner_id == owner.id,
            SubscriptionTransaction.payment_status == "success"
        ).first()
        if not transaction:
            raise ServiceError("transaction_not_found")
        package = self.db.query(SubscriptionPackage).filter(
            SubscriptionPackage.id == transaction.subscription_package_id,
            SubscriptionPackage.is_deleted == False
        ).first()
        if not package:
            raise ServiceError("package_not_found")
        # Cập nhật owner sử dụng gói này
        owner.subscription_package_id = package.id
        owner.updated_at = int(time.time())
        self.db.commit()
        self.db.refresh(owner)
        return {
            "owner_id": owner.id,
            "subscription_package_id": package.id,
            "package": self._package_to_dict(package)
        }
