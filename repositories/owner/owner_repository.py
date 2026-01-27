from sqlalchemy.orm import Session
from models.owner import Owner
from schemas.owner.owner import OwnerCreate, OwnerUpdate

class OwnerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_owner(self, owner_id: str):
        return self.db.query(Owner).filter(Owner.id == owner_id).first()

    def get_owners(self, skip: int = 0, limit: int = 100):
        return self.db.query(Owner).offset(skip).limit(limit).all()

    def create_owner(self, owner: OwnerCreate):
        db_owner = Owner(full_name=owner.full_name, phone=owner.phone, user_id=owner.user_id, subscription_package_id=owner.subscription_package_id)
        self.db.add(db_owner)
        self.db.commit()
        self.db.refresh(db_owner)
        return db_owner

    def update_owner(self, owner_id: str, owner: OwnerUpdate):
        db_owner = self.get_owner(owner_id)
        if db_owner:
            db_owner.full_name = owner.full_name
            db_owner.phone = owner.phone
            db_owner.user_id = owner.user_id
            db_owner.subscription_package_id = owner.subscription_package_id
            self.db.commit()
            self.db.refresh(db_owner)
        return db_owner

    def delete_owner(self, owner_id: str):
        db_owner = self.get_owner(owner_id)
        if db_owner:
            self.db.delete(db_owner)
            self.db.commit()
        return db_owner
