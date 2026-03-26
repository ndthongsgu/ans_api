from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.user import User
from modules.auth.controllers.customer_controller import get_current_user
from modules.stallContent.dto.owner_dto import (
    OwnerStallContentCreateRequest,
    OwnerStallContentResponse,
)
from modules.stallContent.services.owner_service import OwnerStallContentService, ServiceError
from utils.i18n import t

router = APIRouter(prefix="/stall-contents")


def _ensure_owner_role(current_user: User, locale: str | None):
    if not any(role.code == "OWNER" for role in current_user.roles):
        raise HTTPException(status_code=403, detail=t("forbidden", locale))


@router.post("", response_model=OwnerStallContentResponse)
def create_stall_content(
    payload: OwnerStallContentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    locale = accept_language
    _ensure_owner_role(current_user, locale)
    service = OwnerStallContentService(db)

    try:
        return service.create_content(current_user.id, payload)
    except ServiceError as exc:
        if exc.code in {"profile_not_found", "stall_not_found"}:
            raise HTTPException(status_code=404, detail=t(exc.code, locale))
        raise HTTPException(status_code=400, detail=t(exc.code, locale))
