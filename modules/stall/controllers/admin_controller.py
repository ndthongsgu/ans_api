from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from core.database import get_db
from modules.stall.services.admin_service import StallService
from modules.stall.dto.admin_dto import (
    StallPageRequest,
    StallCreate,
    StallUpdate,
    StallOut,
)
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from models.stallTranslation import StallTranslation
from common.dto.response import success_response
from typing import List, Optional
from utils.file_helper import save_stall_image

router = APIRouter(prefix="/stalls")

# Helper to check if user is admin
def ensure_admin(user: User, locale: str | None = None):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

@router.post("/pagination")
def paginate(req: StallPageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    total, items = service.list_stalls(req.dict(), req.page, req.size, req.sortBy, req.sortDirection)
    
    # Convert to output
    results = []
    for s in items:
        # Get all translations
        translations = db.query(StallTranslation).filter(
            StallTranslation.stall_id == s.id
        ).all()
        
        # Get Vietnamese translation for primary display
        vi_trans = next((t for t in translations if t.language_code == "vi"), None)
        
        results.append({
            "id": s.id,
            "owner_id": s.owner_id,
            "owner_name": s.owner.full_name if s.owner else None,
            "name": vi_trans.name if vi_trans else s.name,
            "category": vi_trans.category if vi_trans else s.category,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "radius": s.radius,
            "is_deleted": s.is_deleted,
            "cover_image": s.cover_image,
            "price_range": s.price_range,
            "opening_hours": s.opening_hours,
            "contact_phone": s.contact_phone,
            "website": s.website,
            "average_rating": s.average_rating,
            "total_reviews": s.total_reviews,
            "vi_trans": {
                "language_code": vi_trans.language_code,
                "name": vi_trans.name,
                "category": vi_trans.category,
            } if vi_trans else None,
            "translations": [
                {
                    "language_code": t.language_code,
                    "name": t.name,
                    "category": t.category,
                }
                for t in translations
            ]
        })
    return success_response(
        message="Lấy dữ liệu thành công",
        data={"content": results, "totalElements": total}
    )

@router.get("/")
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    stalls = service.list_all_active()
    data = [{"id": s.id, "name": s.name, "owner_id": s.owner_id} for s in stalls]
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.get("/select")
def select(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    data = service.list_for_select()
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/")
async def create(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
    owner_id: str = Form(...),
    name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    radius: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    price_range: Optional[str] = Form(None),
    opening_hours: Optional[str] = Form(None),
    contact_phone: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    
    # Create stall data (without image handling)
    stall_data = {
        "owner_id": owner_id,
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius,
        "category": category,
        "price_range": price_range,
        "opening_hours": opening_hours,
        "contact_phone": contact_phone,
        "website": website,
        "cover_image": None,  # Image will be uploaded separately
    }
    
    try:
        s = service.create_stall(stall_data)
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    
    data = {
        "id": s.id,
        "owner_id": s.owner_id,
        "name": s.name,
        "latitude": s.latitude,
        "longitude": s.longitude,
        "radius": s.radius,
        "is_deleted": s.is_deleted,
        "cover_image": s.cover_image,
        "category": s.category,
        "price_range": s.price_range,
        "opening_hours": s.opening_hours,
        "contact_phone": s.contact_phone,
        "website": s.website,
        "created_at": s.created_at,
    }
    return success_response(
        message="Tạo cửa hàng thành công",
        data=data,
        status_code=201
    )

@router.put("/{stall_id}")
async def update(
    stall_id: str,
    req: StallUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    ensure_admin(current_user, accept_language)
    service = StallService(db)

    # Build update data (without image handling - use dedicated endpoint for images)
    stall_data = req.dict(exclude_unset=True)
    
    try:
        s = service.update_stall(stall_id, stall_data)
        if not s:
            raise HTTPException(status_code=404, detail="Không tìm thấy")
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    return success_response(
        message="Cập nhật cửa hàng thành công"
    )

@router.get("/{stall_id}")
def detail(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    s = service.get_stall(stall_id)
    if not s:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    
    # Get all translations
    translations = db.query(StallTranslation).filter(
        StallTranslation.stall_id == s.id
    ).all()
    
    # Get Vietnamese translation for primary display
    vi_trans = next((t for t in translations if t.language_code == "vi"), None)
    
    data = {
        "id": s.id,
        "owner_id": s.owner_id,
        "name": vi_trans.name if vi_trans else s.name,
        "category": vi_trans.category if vi_trans else s.category,
        "latitude": s.latitude,
        "longitude": s.longitude,
        "radius": s.radius,
        "cover_image": s.cover_image,
        "price_range": s.price_range,
        "opening_hours": s.opening_hours,
        "contact_phone": s.contact_phone,
        "website": s.website,
        "is_deleted": s.is_deleted,
        "average_rating": s.average_rating,
        "total_reviews": s.total_reviews,
        "owner": {
            "id": s.owner.id,
            "full_name": s.owner.full_name,
        } if s.owner else None,
        "vi_trans": {
            "language_code": vi_trans.language_code,
            "name": vi_trans.name,
            "category": vi_trans.category,
        } if vi_trans else None,
        "translations": [
            {
                "language_code": t.language_code,
                "name": t.name,
                "category": t.category,
            }
            for t in translations
        ]
    }
    return success_response(
        message="Lấy dữ liệu thành công",
        data=data
    )

@router.post("/deactivate/{stall_id}")
def deactivate(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    s = service.deactivate_stall(stall_id)
    if not s:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Ngưng hoạt động cửa hàng thành công"
    )

@router.post("/activate/{stall_id}")
def activate(stall_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), accept_language: str | None = Header(None)):
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    s = service.activate_stall(stall_id)
    if not s:
        raise HTTPException(status_code=404, detail="Không tìm thấy")
    return success_response(
        message="Kích hoạt cửa hàng thành công"
    )

@router.post("/{stall_id}/upload-image")
async def upload_image(
    stall_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
    cover_image: UploadFile = File(...),
):
    """Upload or replace stall cover image"""
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    
    # Verify stall exists
    stall = service.get_stall(stall_id)
    if not stall:
        raise HTTPException(status_code=404, detail="Không tìm thấy cửa hàng")
    
    # Handle image upload
    try:
        file_content = await cover_image.read()
        image_url = save_stall_image(file_content, cover_image.filename or "image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi tải ảnh: {str(e)}")
    
    # Update stall with new image URL
    try:
        s = service.upload_stall_image(stall_id, image_url)
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    
    return success_response(
        message="Tải ảnh cửa hàng thành công",
        data={
            "id": s.id,
            "cover_image": s.cover_image,
        }
    )

@router.post("/{stall_id}/image")
async def upload_image_alt(
    stall_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
    cover_image: UploadFile = File(...),
):
    """Upload or replace stall cover image (alternative endpoint)"""
    return await upload_image(stall_id, current_user, db, accept_language, cover_image)

@router.delete("/{stall_id}/image")
def delete_image(
    stall_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Delete stall cover image"""
    ensure_admin(current_user, accept_language)
    service = StallService(db)
    
    # Verify stall exists
    stall = service.get_stall(stall_id)
    if not stall:
        raise HTTPException(status_code=404, detail="Không tìm thấy cửa hàng")
    
    # Delete image
    try:
        s = service.delete_stall_image(stall_id)
        if not s:
            raise HTTPException(status_code=404, detail="Không tìm thấy cửa hàng")
    except RuntimeError as err:
        raise HTTPException(status_code=400, detail=str(err))
    
    return success_response(
        message="Xóa ảnh cửa hàng thành công",
        data={
            "id": s.id,
            "cover_image": s.cover_image,
        }
    )
