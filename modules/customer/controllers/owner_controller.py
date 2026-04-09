from typing import Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from common.dto.response import success_response
from models.user import User
from modules.auth.controllers.mobile_controller import get_current_user
from modules.customer.dto.owner_dto import OwnerDashboardResponse
from modules.customer.services.owner_service import OwnerDashboardService, ServiceError
from utils.i18n import t

router = APIRouter(prefix="/dashboard")


@router.get("")
def owner_dashboard(
	group_by: Literal["day", "week", "month"] = Query("day", alias="groupBy"),
	from_timestamp: int | None = Query(None, alias="fromTimestamp"),
	to_timestamp: int | None = Query(None, alias="toTimestamp"),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	locale = accept_language

	service = OwnerDashboardService(db)
	try:
		data = service.get_dashboard(
			user_id=current_user.id,
			group_by=group_by,
			from_timestamp=from_timestamp,
			to_timestamp=to_timestamp,
		)
		return success_response(message="Lấy dữ liệu thành công", data=data)
	except ServiceError as e:
		if e.code == "profile_not_found":
			raise HTTPException(status_code=404, detail=t(e.code, locale))
		raise HTTPException(status_code=400, detail=t(e.code, locale))
