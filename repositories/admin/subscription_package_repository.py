from sqlalchemy.orm import Session
from models.subscription_package import SubscriptionPackage
from schemas.admin.subscription_package import SubscriptionPackageCreate, SubscriptionPackageUpdate

class SubscriptionPackageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_subscription_package(self, package_id: str):
        return self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == package_id).first()

    def get_subscription_packages(self, skip: int = 0, limit: int = 100):
        return self.db.query(SubscriptionPackage).offset(skip).limit(limit).all()

    def create_subscription_package(self, package: SubscriptionPackageCreate):
        db_package = SubscriptionPackage(
            name=package.name,
            description=package.description,
            price=package.price,
            duration=package.duration,
            max_stalls=package.max_stalls,
            features=package.features
        )
        self.db.add(db_package)
        self.db.commit()
        self.db.refresh(db_package)
        return db_package

    def update_subscription_package(self, package_id: str, package: SubscriptionPackageUpdate):
        db_package = self.get_subscription_package(package_id)
        if db_package:
            db_package.name = package.name
            db_package.description = package.description
            db_package.price = package.price
            db_package.duration = package.duration
            db_package.max_stalls = package.max_stalls
            db_package.features = package.features
            self.db.commit()
            self.db.refresh(db_package)
        return db_package

    def delete_subscription_package(self, package_id: str):
        db_package = self.get_subscription_package(package_id)
        if db_package:
            self.db.delete(db_package)
            self.db.commit()
        return db_package
