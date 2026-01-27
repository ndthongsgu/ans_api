from sqlalchemy.orm import Session
from repositories.admin.subscription_package_repository import SubscriptionPackageRepository
from schemas.admin.subscription_package import SubscriptionPackageCreate, SubscriptionPackageUpdate

class SubscriptionPackageService:
    def __init__(self, db: Session):
        self.repository = SubscriptionPackageRepository(db)

    def get_subscription_package(self, package_id: str):
        return self.repository.get_subscription_package(package_id)

    def get_subscription_packages(self, skip: int = 0, limit: int = 100):
        return self.repository.get_subscription_packages(skip, limit)

    def create_subscription_package(self, package: SubscriptionPackageCreate):
        return self.repository.create_subscription_package(package)

    def update_subscription_package(self, package_id: str, package: SubscriptionPackageUpdate):
        return self.repository.update_subscription_package(package_id, package)

    def delete_subscription_package(self, package_id: str):
        return self.repository.delete_subscription_package(package_id)
