from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from time import time
from core.database import get_db
from common.dto.response import success_response
from modules.auth.controllers.mobile_controller import get_current_user
from modules.listeningHistory.services.mobile_service import ListeningHistoryMobileService
from modules.listeningHistory.dto.mobile_dto import ListeningHistoryCreateRequest
from models.user import User

router = APIRouter(prefix="/listening-history")


@router.get("")
@router.get("/")
def list_listening_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    from_timestamp: int | None = Query(None),
    to_timestamp: int | None = Query(None),
):
    """Get current user listening history with optional date filter and pagination"""
    service = ListeningHistoryMobileService(db)
    result = service.get_user_listening_history(
        user_id=current_user.id,
        page=page,
        size=size,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
    )

    return success_response(
        message="Lấy dữ liệu thành công",
        data=result,
    )


@router.post("/")
def create_listening_history(
    payload: ListeningHistoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new listening history record for current user"""
    service = ListeningHistoryMobileService(db)

    if payload.listened_at <= 0:
        raise HTTPException(status_code=400, detail="Invalid listened_at")

    result = service.add_listening_history(
        user_id=current_user.id,
        stall_id=payload.stall_id,
        stall_content_id=payload.stall_content_id,
        listened_at=payload.listened_at,
        listen_duration=payload.listen_duration,
    )

    return success_response(
        message="Thêm lịch sử nghe thành công",
        data=result,
        status_code=201,
    )
