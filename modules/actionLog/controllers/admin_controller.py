from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.actionLog.services.admin_service import ActionLogService
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User
from typing import List
from modules.actionLog.dto.admin_dto import ActionLogPageRequest

router = APIRouter(prefix="/api/action-logs")


@router.post("/pagination")
def paginate(
    req: ActionLogPageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ActionLogService(db)

    filters = {}
    if req.functionType:
        filters["functionType"] = req.functionType
    if req.functionId:
        filters["functionId"] = req.functionId
    if req.type:
        filters["action"] = req.type
    if req.createdBy:
        filters["createdBy"] = req.createdBy

    total, items = service.list_action_logs(
        filters, req.page, req.size, req.sortBy, req.sortDirection
    )

    # Convert to output DTOs and include user name
    results = []
    for log in items:
        user = db.query(User).filter(User.id == log.created_by).first() if log.created_by else None
        results.append({
            "id": log.id,
            "functionType": log.function_type,
            "functionId": log.function_id,
            "action": log.action,
            "changeDetails": log.change_details,
            "oldValues": log.old_values,
            "newValues": log.new_values,
            "createdDate": log.created_at,
            "createdBy": log.created_by,
            "createdByName": user.username if user else "System",
        })

    return {"content": results, "totalElements": total}
