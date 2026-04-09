from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from models.user import User
from modules.auth.controllers.owner_controller import get_current_user
from modules.stall_content.dto.owner_dto import (
    StallContentCreateRequest,
    StallContentUpdateRequest,
)
from modules.stall_content.services.owner_service import OwnerStallContentService, ServiceError
from common.dto.response import success_response
from utils.i18n import t

router = APIRouter(prefix="/stall-contents")


def _ensure_owner_role(current_user: User, locale: str | None):
    if not any(role.code == "OWNER" for role in current_user.roles):
        raise HTTPException(status_code=403, detail=t("forbidden", locale))


def _content_to_dict(content):
    return {
        "id": content.id,
        "stall_id": content.stall_id,
        "stall_name": content.stall_name,
        "tts_script": content.tts_script,
        "created_at": content.created_at,
        "updated_at": content.updated_at,
        "is_deleted": content.is_deleted,
    }


@router.post("")
def create_stall_content(
    payload: StallContentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        content = service.create_content(current_user.id, payload)
        return success_response(
            message="Tạo nội dung thành công",
            data=[_content_to_dict(content)],
            status_code=201,
        )
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.get("/available-stalls")
def list_available_stalls_for_content(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        data = service.list_stalls_without_content(current_user.id, skip, limit)
        return success_response(
            message="Danh sách quán chưa có nội dung",
            data=data,
        )
    except ServiceError as exc:
        if exc.code == "profile_not_found":
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.get("/all")
def list_owner_contents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
    language_code: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List all contents across all stalls owned by current user"""
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        data, total = service.list_owner_contents(
            current_user.id, language_code, skip, limit
        )
        return success_response(
            message="Lấy dữ liệu thành công",
            data=data,
        )
    except ServiceError as exc:
        if exc.code == "profile_not_found":
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.get("/{stall_id}/available-languages")
def get_available_languages(
    stall_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Get available languages for a stall's content"""
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        languages = service.get_available_languages(current_user.id, stall_id)
        return success_response(
            message="Lấy dữ liệu thành công",
            data=languages,
        )
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.get("/{stall_id}/language/{language_code}")
def list_stall_contents_by_language(
    stall_id: str,
    language_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """List stall contents in a specific language for current owner"""
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        data, total = service.list_stall_contents(
            current_user.id,
            stall_id,
            language_code,
        )
        return success_response(
            message="Lấy dữ liệu thành công",
            data=data,
        )
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.get("/{stall_id}/{content_id}")
def get_stall_content(
    stall_id: str,
    content_id: str,
    language_code: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Get a specific content"""
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        content = service.get_content(current_user.id, stall_id, content_id, language_code)
        return success_response(
            message="Lấy dữ liệu thành công",
            data=[_content_to_dict(content)],
        )
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found", "content_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.put("/{stall_id}/{content_id}")
def update_stall_content(
    stall_id: str,
    content_id: str,
    payload: StallContentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Update stall content"""
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        content = service.update_content(current_user.id, stall_id, content_id, payload)
        return success_response(
            message="Cập nhật nội dung thành công",
            data=[_content_to_dict(content)],
        )
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found", "content_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.delete("/{stall_id}/{content_id}")
def delete_stall_content(
    stall_id: str,
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Delete stall content permanently"""
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        service.delete_content(current_user.id, stall_id, content_id)
        return success_response(
            message="Xóa nội dung thành công",
            data=[],
        )
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found", "content_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))


@router.patch("/{stall_id}/{content_id}/status")
def toggle_stall_content_status(
    stall_id: str,
    content_id: str,
    is_deleted: int = Query(..., ge=0, le=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Toggle stall content active status via is_deleted (0/1)"""
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        content = service.set_content_deleted_status(
            current_user.id,
            stall_id,
            content_id,
            bool(is_deleted),
        )
        return success_response(
            message="Cập nhật trạng thái nội dung thành công",
            data=[_content_to_dict(content)],
        )
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found", "content_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))
