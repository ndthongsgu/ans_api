from sqlalchemy.orm import Session
from common.enums.language import LanguageCode
from models.stall import Stall
from models.stallTranslation import StallTranslation
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class StallMobileService:
    """Service for mobile API - read-only operations with translations"""
    
    def __init__(self, db: Session):
        self.db = db

    def _get_translation_by_language(self, stall_id: str, language_code: str) -> StallTranslation | None:
        """Get translation for specific language, fallback to default language if not found"""
        trans = self.db.query(StallTranslation).filter(
            StallTranslation.stall_id == stall_id,
            StallTranslation.language_code == language_code
        ).first()
        
        if not trans and language_code != LanguageCode.DEFAULT:
            # Fallback to default language
            trans = self.db.query(StallTranslation).filter(
                StallTranslation.stall_id == stall_id,
                StallTranslation.language_code == LanguageCode.DEFAULT
            ).first()
        
        return trans

    def list_stalls(self, language_code: str = "vi", search: str = None) -> List[dict]:
        """Get all active stalls with multilingual translations, optionally filtered by name"""
        query = self.db.query(Stall).filter(Stall.is_deleted == False)
        
        # Filter by search term if provided
        if search:
            search_lower = search.lower()
            # Search in translated names
            stalls = []
            for s in query.all():
                trans = self._get_translation_by_language(s.id, language_code)
                stall_name = (trans.name if trans else s.name).lower()
                if search_lower in stall_name:
                    stalls.append(s)
        else:
            stalls = query.all()
        
        results = []
        for s in stalls:
            trans = self._get_translation_by_language(s.id, language_code)
            
            results.append({
                "id": s.id,
                "owner_id": s.owner_id,
                "owner_name": s.owner.full_name if s.owner else None,
                "name": trans.name if trans else s.name,
                "category": trans.category if trans else s.category,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "radius": s.radius,
                "cover_image": s.cover_image,
                "price_range": s.price_range,
                "opening_hours": s.opening_hours,
                "contact_phone": s.contact_phone,
                "website": s.website,
                "average_rating": s.average_rating,
                "total_reviews": s.total_reviews,
            })
        
        logger.info(f"Retrieved {len(results)} stalls for language {language_code}")
        return results

    def get_stall(self, stall_id: str, language_code: str = "vi") -> dict | None:
        """Get stall detail with multilingual translations"""
        stall = self.db.query(Stall).filter(
            Stall.id == stall_id,
            Stall.is_deleted == False
        ).first()
        
        if not stall:
            logger.warning(f"Stall {stall_id} not found")
            return None
        
        trans = self._get_translation_by_language(stall.id, language_code)
        
        data = {
            "id": stall.id,
            "owner_id": stall.owner_id,
            "owner_name": stall.owner.full_name if stall.owner else None,
            "name": trans.name if trans else stall.name,
            "category": trans.category if trans else stall.category,
            "latitude": stall.latitude,
            "longitude": stall.longitude,
            "radius": stall.radius,
            "cover_image": stall.cover_image,
            "price_range": stall.price_range,
            "opening_hours": stall.opening_hours,
            "contact_phone": stall.contact_phone,
            "website": stall.website,
            "average_rating": stall.average_rating,
            "total_reviews": stall.total_reviews,
            "language_code": language_code,
        }
        
        logger.info(f"Retrieved stall {stall_id} for language {language_code}")
        return data

    def get_nearby_stalls(self, center_stall_id: str, language_code: str = "vi") -> List[dict]:
        """Get nearby stalls with multilingual translations"""
        # Verify center stall exists
        center_stall = self.db.query(Stall).filter(
            Stall.id == center_stall_id,
            Stall.is_deleted == False
        ).first()
        
        if not center_stall:
            logger.warning(f"Center stall {center_stall_id} not found")
            return None
        
        # Get all other active stalls (in production, use PostGIS or distance calculation)
        nearby_stalls = self.db.query(Stall).filter(
            Stall.id != center_stall_id,
            Stall.is_deleted == False
        ).all()
        
        results = []
        for s in nearby_stalls:
            trans = self._get_translation_by_language(s.id, language_code)
            results.append({
                "id": s.id,
                "owner_id": s.owner_id,
                "owner_name": s.owner.full_name if s.owner else None,
                "name": trans.name if trans else s.name,
                "category": trans.category if trans else s.category,
                "latitude": s.latitude,
                "longitude": s.longitude,
                "radius": s.radius,
                "cover_image": s.cover_image,
                "average_rating": s.average_rating,
                "total_reviews": s.total_reviews,
            })
        
        logger.info(f"Retrieved {len(results)} nearby stalls for {center_stall_id} in language {language_code}")
        return results

    def get_available_languages_for_stall(self, stall_id: str) -> List[str]:
        """Get all available languages for a stall"""
        languages = self.db.query(StallTranslation.language_code).filter(
            StallTranslation.stall_id == stall_id
        ).distinct().all()
        
        lang_list = [lang[0] for lang in languages]
        logger.info(f"Retrieved {len(lang_list)} available languages for stall {stall_id}")
        return lang_list
