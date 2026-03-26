from sqlalchemy.orm import Session
from common.enums.language import LanguageCode
from models.stall import Stall
from models.stallTranslation import StallTranslation
from typing import List, Tuple, Optional
import logging
import math

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

    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula (in km)"""
        R = 6371  # Earth's radius in kilometers
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

    def list_stalls(
        self, 
        language_code: str = "vi", 
        search: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """Get active stalls with multilingual translations, sorted by distance if coordinates provided, with pagination"""
        query = self.db.query(Stall).filter(Stall.is_deleted == False)
        
        # Filter by search term if provided
        if search:
            search_lower = search.lower()
            # Search in translated names and categories
            stalls = []
            for s in query.all():
                trans = self._get_translation_by_language(s.id, language_code)
                stall_name = (trans.name if trans else s.name).lower()
                stall_category = (trans.category if trans else s.category or "").lower()
                if search_lower in stall_name or search_lower in stall_category:
                    stalls.append(s)
        else:
            stalls = query.all()
        
        results = []
        for s in stalls:
            trans = self._get_translation_by_language(s.id, language_code)
            
            result_item = {
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
            }
            
            # Add distance if user location is provided
            if latitude is not None and longitude is not None:
                distance_km = self._calculate_distance(latitude, longitude, s.latitude, s.longitude)
                result_item["distance_km"] = round(distance_km, 2)
            
            results.append(result_item)
        
        # Sort by distance if coordinates are provided
        if latitude is not None and longitude is not None:
            results.sort(key=lambda x: x.get("distance_km", float('inf')))
        
        # Apply pagination
        paginated_results = results[offset:offset + limit]
        
        logger.info(f"Retrieved {len(paginated_results)}/{len(results)} stalls for language {language_code}, offset={offset}, limit={limit}")
        return paginated_results

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
