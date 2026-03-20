from sqlalchemy.orm import Session
from models.subscription_package import SubscriptionPackage
from typing import Tuple, List

class SubscriptionPackageService:
    def __init__(self, db: Session):
        self.db = db

    def list_subscription_packages(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[SubscriptionPackage]]:
        q = self.db.query(SubscriptionPackage)
        
        if filters.get('name'):
            q = q.filter(SubscriptionPackage.name.ilike(f"%{filters['name']}%"))
            
        if filters.get('is_active') is not None:
            q = q.filter(SubscriptionPackage.is_deleted == (not filters['is_active']))
                
        # Ordering
        if sortBy:
            column = getattr(SubscriptionPackage, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
                    
        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_subscription_package(self, package_id: str):
        return self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == package_id).first()

    def create_subscription_package(self, data: dict):
        package = SubscriptionPackage(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            duration=data['duration'],
            max_stalls=data.get('max_stalls', 1),
            max_audio_storage=data.get('max_audio_storage', 100),
            features=data.get('features'),
        )
        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)
        return package

    def update_subscription_package(self, package_id: str, data: dict):
        package = self.get_subscription_package(package_id)
        if not package:
            return None
            
        package.name = data['name']
        package.description = data.get('description')
        package.price = data['price']
        package.duration = data['duration']
        package.max_stalls = data.get('max_stalls', 1)
        package.max_audio_storage = data.get('max_audio_storage', 100)
        package.features = data.get('features')
        
        self.db.commit()
        return package

    def deactivate_subscription_package(self, package_id: str):
        package = self.get_subscription_package(package_id)
        if package:
            package.is_deleted = True
            self.db.commit()
        return package

    def activate_subscription_package(self, package_id: str):
        package = self.get_subscription_package(package_id)
        if package:
            package.is_deleted = False
            self.db.commit()
        return package

    def list_all_active(self):
        return self.db.query(SubscriptionPackage).filter(SubscriptionPackage.is_deleted == False).all()

    def list_for_select(self):
        """Return subscription packages formatted for select dropdown"""
        packages = self.list_all_active()
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price
            }
            for p in packages
        ]