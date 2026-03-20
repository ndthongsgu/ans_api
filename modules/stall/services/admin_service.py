from sqlalchemy.orm import Session
from models.stall import Stall
import time
from typing import Tuple, List

class StallService:
    def __init__(self, db: Session):
        self.db = db

    def list_stalls(self, filters: dict, page: int, size: int, sortBy: str | None = None, sortDirection: str | None = None) -> Tuple[int, List[Stall]]:
        q = self.db.query(Stall)
        
        if filters.get('name'):
            q = q.filter(Stall.name.ilike(f"%{filters['name']}%"))
            
        if filters.get('owner_id'):
            q = q.filter(Stall.owner_id == filters['owner_id'])
            
        if filters.get('is_deleted') is not None:
            q = q.filter(Stall.is_deleted == filters['is_deleted'])
            
        if filters.get('category'):
            q = q.filter(Stall.category.ilike(f"%{filters['category']}%"))
                
        # Ordering
        if sortBy:
            column = getattr(Stall, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == 'DESC':
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
                    
        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def get_stall(self, stall_id: str):
        return self.db.query(Stall).filter(Stall.id == stall_id).first()

    def create_stall(self, data: dict):
        # Validate coordinates
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
        except (ValueError, TypeError):
            raise RuntimeError("Vĩ độ và kinh độ phải là số")
        
        stall = Stall(
            owner_id=data['owner_id'],
            name=data['name'],
            latitude=latitude,
            longitude=longitude,
            radius=int(data.get('radius', 50)),
            cover_image=data.get('cover_image'),
            is_deleted=False,
            category=data.get('category'),
            price_range=data.get('price_range'),
            opening_hours=data.get('opening_hours'),
            contact_phone=data.get('contact_phone'),
            website=data.get('website'),
            created_at=int(time.time())
        )
        self.db.add(stall)
        self.db.commit()
        self.db.refresh(stall)
        return stall

    def update_stall(self, stall_id: str, data: dict):
        stall = self.get_stall(stall_id)
        if not stall:
            return None
        
        # Validate new owner_id if provided
        if data.get('owner_id'):
            from models.owner import Owner
            owner = self.db.query(Owner).filter(Owner.id == data['owner_id']).first()
            if not owner:
                raise RuntimeError(f"Chủ quán với ID {data['owner_id']} không tìm thấy")
            stall.owner_id = data['owner_id']
        
        # Validate coordinates
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
        except (ValueError, TypeError):
            raise RuntimeError("Vĩ độ và kinh độ phải là số")
            
        stall.name = data['name']
        stall.latitude = latitude
        stall.longitude = longitude
        stall.radius = int(data.get('radius', 50))
        stall.cover_image = data.get('cover_image')
        stall.category = data.get('category')
        stall.price_range = data.get('price_range')
        stall.opening_hours = data.get('opening_hours')
        stall.contact_phone = data.get('contact_phone')
        stall.website = data.get('website')
        stall.updated_at = int(time.time())
        
        self.db.commit()
        return stall

    def deactivate_stall(self, stall_id: str):
        stall = self.get_stall(stall_id)
        if stall:
            stall.is_deleted = True
            self.db.commit()
        return stall

    def activate_stall(self, stall_id: str):
        stall = self.get_stall(stall_id)
        if stall:
            stall.is_deleted = False
            self.db.commit()
        return stall

    def list_all_active(self):
        return self.db.query(Stall).filter(Stall.is_deleted == False).all()

    def list_for_select(self):
        """Return stalls formatted for select dropdown"""
        stalls = self.list_all_active()
        return [
            {
                "id": s.id,
                "name": s.name,
                "owner_id": s.owner_id
            }
            for s in stalls
        ]
