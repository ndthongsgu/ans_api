from pydantic import BaseModel, Field, model_validator


class SubscriptionPackageResponse(BaseModel):
    id: str
    code: str
    name: str
    price: float
    max_stalls: int
    duration_days: int
    description: str | None = None
    is_deleted: bool
    created_at: int
    updated_at: int | None = None


class SubscriptionPackageListResponse(BaseModel):
    data: list[SubscriptionPackageResponse]
    total: int


class SubscriptionRegisterRequest(BaseModel):
    subscription_package_id: str = Field(min_length=1)
    payment_method: str | None = Field(default=None)

class SubscriptionTransactionResponse(BaseModel):
    id: str
    transaction_code: str
    order_id: str
    request_id: str
    owner_id: str
    subscription_package_id: str
    package_code: str
    package_name: str
    amount: float
    currency: str
    payment_method: str
    payment_provider: str
    payment_status: str
    payment_url: str | None = None
    qr_code_url: str | None = None
    vnpay_trans_id: str | None = None
    vnpay_response_code: str | None = None
    subscription_start_at: int
    subscription_end_at: int
    paid_at: int | None = None
    note: str | None = None
    created_at: int
    updated_at: int | None = None


class SubscriptionTransactionListResponse(BaseModel):
    data: list[SubscriptionTransactionResponse]
    total: int


class SubscriptionRegisterResponse(BaseModel):
    package: SubscriptionPackageResponse
    transaction: SubscriptionTransactionResponse
