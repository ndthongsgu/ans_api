from sqlalchemy.orm import Session
from models.stall import Stall
from models.stallTranslation import StallTranslation
from common.enums.language import LanguageCode
from utils.translation import translate_text
from utils.file_helper import delete_stall_image
import time
import logging
from typing import Tuple, List

logger = logging.getLogger(__name__)

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
        self.db.flush()  # Get stall ID without committing yet
        
        # Create translations for all available languages
        for lang_info in LanguageCode.LIST:
            language_code = lang_info['code']
            
            try:
                # Try to translate name and category to target language
                if language_code == 'vi':
                    # Vietnamese is the original language
                    translated_name = data['name']
                    translated_category = data.get('category')
                else:
                    # Translate to other languages
                    translated_name = translate_text(data['name'], 'vi', language_code)
                    translated_category = None
                    if data.get('category'):
                        translated_category = translate_text(data.get('category', ''), 'vi', language_code)
                
                translation = StallTranslation(
                    stall_id=stall.id,
                    language_code=language_code,
                    name=translated_name,
                    category=translated_category,
                )
                self.db.add(translation)
                logger.info(f"[CREATE] {language_code}: {translated_name} | {translated_category}")
            
            except Exception as e:
                # If translation fails, fall back to Vietnamese text
                logger.warning(f"[FALLBACK] Translation failed for {language_code}: {str(e)}, using Vietnamese text")
                
                translation = StallTranslation(
                    stall_id=stall.id,
                    language_code=language_code,
                    name=data['name'],
                    category=data.get('category'),
                )
                self.db.add(translation)
        
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
        
        # Validate and update coordinates if provided
        if data.get('latitude') is not None or data.get('longitude') is not None:
            try:
                latitude = float(data.get('latitude', stall.latitude))
                longitude = float(data.get('longitude', stall.longitude))
            except (ValueError, TypeError):
                raise RuntimeError("Vĩ độ và kinh độ phải là số")
            stall.latitude = latitude
            stall.longitude = longitude
        
        # Update name if provided
        if data.get('name') is not None:
            stall.name = data['name']
        
        # Update optional fields
        if data.get('radius') is not None:
            try:
                stall.radius = int(data['radius'])
            except (ValueError, TypeError):
                raise RuntimeError("Radius phải là số nguyên")
        if data.get('cover_image') is not None:
            stall.cover_image = data['cover_image']
        if data.get('category') is not None:
            stall.category = data['category']
        if data.get('price_range') is not None:
            stall.price_range = data['price_range']
        if data.get('opening_hours') is not None:
            stall.opening_hours = data['opening_hours']
        if data.get('contact_phone') is not None:
            stall.contact_phone = data['contact_phone']
        if data.get('website') is not None:
            stall.website = data['website']

        stall.updated_at = int(time.time())
        
        # Update Vietnamese translation if name or category provided
        if data.get('name') is not None or data.get('category') is not None:
            vi_translation = self.db.query(StallTranslation).filter(
                StallTranslation.stall_id == stall_id,
                StallTranslation.language_code == "vi"
            ).first()
            
            if vi_translation:
                if data.get('name') is not None:
                    vi_translation.name = data['name']
                if data.get('category') is not None:
                    vi_translation.category = data['category']
                vi_translation.updated_at = int(time.time())
            else:
                # Create Vietnamese translation if it doesn't exist
                vi_translation = StallTranslation(
                    stall_id=stall_id,
                    language_code="vi",
                    name=data.get('name', stall.name),
                    category=data.get('category'),
                )
                self.db.add(vi_translation)
            
            # Auto-translate to other languages when Vietnamese is updated
            for lang_info in LanguageCode.LIST:
                if lang_info['code'] == 'vi':
                    continue  # Already handled Vietnamese above
                
                language_code = lang_info['code']
                
                try:
                    # Translate Vietnamese name and category to target language
                    translated_name = translate_text(data.get('name', stall.name), 'vi', language_code)
                    translated_category = None
                    if data.get('category') or stall.category:
                        translated_category = translate_text(data.get('category', stall.category or ''), 'vi', language_code)
                    
                    # Update or create translation for this language
                    other_translation = self.db.query(StallTranslation).filter(
                        StallTranslation.stall_id == stall_id,
                        StallTranslation.language_code == language_code
                    ).first()
                    
                    if other_translation:
                        other_translation.name = translated_name
                        other_translation.category = translated_category
                        other_translation.updated_at = int(time.time())
                    else:
                        # Create translation if it doesn't exist
                        other_translation = StallTranslation(
                            stall_id=stall_id,
                            language_code=language_code,
                            name=translated_name,
                            category=translated_category,
                        )
                        self.db.add(other_translation)
                    
                    logger.info(f"[UPDATE] {language_code}: {translated_name} | {translated_category}")
                
                except Exception as e:
                    # If translation fails, fall back to Vietnamese text
                    logger.warning(f"[FALLBACK] Translation failed for {language_code}: {str(e)}, using Vietnamese text")
                    
                    other_translation = self.db.query(StallTranslation).filter(
                        StallTranslation.stall_id == stall_id,
                        StallTranslation.language_code == language_code
                    ).first()
                    
                    if other_translation:
                        other_translation.name = data.get('name', stall.name)
                        other_translation.category = data.get('category', stall.category)
                        other_translation.updated_at = int(time.time())
                    else:
                        other_translation = StallTranslation(
                            stall_id=stall_id,
                            language_code=language_code,
                            name=data.get('name', stall.name),
                            category=data.get('category', stall.category),
                        )
                        self.db.add(other_translation)
        
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

    def upload_stall_image(self, stall_id: str, image_url: str):
        """Update stall with new cover image URL"""
        stall = self.get_stall(stall_id)
        if not stall:
            return None
        
        # Delete old image if it exists
        if stall.cover_image:
            delete_stall_image(stall.cover_image)
        
        # Update with new image
        stall.cover_image = image_url
        stall.updated_at = int(time.time())
        self.db.commit()
        return stall

    def delete_stall_image(self, stall_id: str):
        """Delete stall cover image"""
        stall = self.get_stall(stall_id)
        if not stall:
            return None
        
        # Delete image file
        if stall.cover_image:
            delete_stall_image(stall.cover_image)
            stall.cover_image = None
            stall.updated_at = int(time.time())
            self.db.commit()
        
        return stall
