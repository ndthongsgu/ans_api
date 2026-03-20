from sqlalchemy.orm import Session
from models.customer_subscription_package import CustomerSubscriptionPackage
from models.customer import Customer
import time

class ServiceError(Exception):
    """Service-level error with a machine-readable code."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def list_packages(self, active_only: bool = True):
        q = self.db.query(CustomerSubscriptionPackage)
        if active_only:
            q = q.filter(CustomerSubscriptionPackage.is_deleted == False)
        return q.all()

    def get_package(self, package_id: str):
        return self.db.query(CustomerSubscriptionPackage).filter(CustomerSubscriptionPackage.id == package_id).first()

    def purchase_package(self, user_id: str, package_id: str):
        pkg = self.get_package(package_id)
        if not pkg or pkg.is_deleted:
            raise ServiceError('package_not_found')

        customer = self.db.query(Customer).filter(Customer.user_id == user_id).first()
        if not customer:
            raise ServiceError('customer_not_found')

        now = int(time.time())
        expires = now + int(pkg.duration) * 24 * 3600

        customer.subscription_package_id = pkg.id
        customer.subscription_expires_at = expires

        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_customer_subscription(self, user_id: str):
        customer = self.db.query(Customer).filter(Customer.user_id == user_id).first()
        if not customer:
            return None
        pkg = None
        if customer.subscription_package_id:
            pkg = self.get_package(customer.subscription_package_id)
        active = False
        if customer.subscription_expires_at:
            try:
                exp = int(customer.subscription_expires_at)
                active = exp > int(time.time())
            except Exception:
                active = False
        return {
            'customer': customer,
            'package': pkg,
            'expires_at': customer.subscription_expires_at,
            'active': active
        }