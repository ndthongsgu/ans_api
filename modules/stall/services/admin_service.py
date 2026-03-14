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
            
        if filters.get('status') is not None:
            q = q.filter(Stall.status == filters['status'])
            
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
        stall = Stall(
            owner_id=data['owner_id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            radius=data.get('radius', 50),
            cover_image=data.get('cover_image'),
            status=True,
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
            
        stall.owner_id = data['owner_id']
        stall.name = data['name']
        stall.latitude = data['latitude']
        stall.longitude = data['longitude']
        stall.radius = data.get('radius', 50)
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
            stall.status = False
            self.db.commit()
        return stall

    def activate_stall(self, stall_id: str):
        stall = self.get_stall(stall_id)
        if stall:
            stall.status = True
            self.db.commit()
        return stall

    def list_all_active(self):
        return self.db.query(Stall).filter(Stall.status == True).all()

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
