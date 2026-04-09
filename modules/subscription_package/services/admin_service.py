from sqlalchemy.orm import Session
from models.subscription_package import SubscriptionPackage


class SubscriptionPackageService:
    def __init__(self, db: Session):
        self.db = db

    def list_packages(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None):
        q = self.db.query(SubscriptionPackage).filter(SubscriptionPackage.is_deleted == False)

        if filters.get('name'):
            q = q.filter(SubscriptionPackage.name.ilike(f"%{filters['name']}%"))
        if filters.get('code'):
            q = q.filter(SubscriptionPackage.code.ilike(f"%{filters['code']}%"))
        if sortBy:
            column = getattr(SubscriptionPackage, sortBy, None)
            if column is not None:
                q = q.order_by(column.desc() if sortDirection and sortDirection.upper() == 'DESC' else column.asc())

        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_package(self, package_id: str):
        return self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == package_id, SubscriptionPackage.is_deleted == False).first()

    def create_package(self, data: dict):
        if self.db.query(SubscriptionPackage).filter(SubscriptionPackage.code == data['code'], SubscriptionPackage.is_deleted == False).first():
            raise RuntimeError('subscription_package_code_exists')

        pkg = SubscriptionPackage(
            name=data['name'],
            code=data['code'],
            price=data['price'],
            max_stalls=data['max_stalls'],
            description=data.get('description'),
        )

        self.db.add(pkg)
        self.db.commit()
        self.db.refresh(pkg)
        return pkg

    def update_package(self, package_id: str, data: dict):
        pkg = self.get_package(package_id)
        if not pkg:
            return None

        if data.get('name') is not None:
            pkg.name = data['name']
        if data.get('code') is not None and data['code'] != pkg.code:
            if self.db.query(SubscriptionPackage).filter(SubscriptionPackage.code == data['code'], SubscriptionPackage.id != package_id, SubscriptionPackage.is_deleted == False).first():
                raise RuntimeError('subscription_package_code_exists')
            pkg.code = data['code']
        if data.get('price') is not None:
            pkg.price = data['price']
        if data.get('max_stalls') is not None:
            pkg.max_stalls = data['max_stalls']
        if data.get('description') is not None:
            pkg.description = data['description']

        self.db.commit()
        self.db.refresh(pkg)
        return pkg

    def deactivate_package(self, package_id: str):
        pkg = self.get_package(package_id)
        if not pkg:
            return None
        pkg.is_deleted = True
        self.db.commit()
        return pkg

    def activate_package(self, package_id: str):
        pkg = self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == package_id).first()
        if not pkg:
            return None
        pkg.is_deleted = False
        self.db.commit()
        return pkg

    def soft_delete_package(self, package_id: str):
        pkg = self.get_package(package_id)
        if not pkg:
            return None
        pkg.is_deleted = True
        self.db.commit()
        return pkg

    def list_for_select(self):
        return self.db.query(SubscriptionPackage).filter(SubscriptionPackage.is_deleted == False).all()
