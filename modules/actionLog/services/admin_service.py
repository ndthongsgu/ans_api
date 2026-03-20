from sqlalchemy.orm import Session
from models.actionLog import ActionLog
from models.user import User
from typing import Tuple, List
import time


class ActionLogService:
    def __init__(self, db: Session):
        self.db = db

    def list_action_logs(
        self,
        filters: dict,
        page: int,
        size: int,
        sortBy: str | None = None,
        sortDirection: str | None = None,
    ) -> Tuple[int, List[ActionLog]]:
        q = self.db.query(ActionLog)

        if filters.get("functionType"):
            q = q.filter(ActionLog.function_type == filters["functionType"])

        if filters.get("functionId"):
            q = q.filter(ActionLog.function_id == filters["functionId"])

        if filters.get("action"):
            q = q.filter(ActionLog.action == filters["action"])

        if filters.get("createdBy"):
            q = q.filter(ActionLog.created_by == filters["createdBy"])

        # Ordering
        if sortBy:
            column = getattr(ActionLog, sortBy, None)
            if column is not None:
                if sortDirection and sortDirection.upper() == "DESC":
                    q = q.order_by(column.desc())
                else:
                    q = q.order_by(column.asc())
        else:
            # Default sort by created_at descending
            q = q.order_by(ActionLog.created_at.desc())

        total = q.count()
        items = q.offset(page * size).limit(size).all()
        return total, items

    def create_action_log(self, data: dict):
        """Create an action log entry"""
        current_time = int(time.time())
        log = ActionLog(
            created_by=data.get("created_by"),
            function_type=data.get("function_type"),
            function_id=data.get("function_id"),
            action=data.get("action"),
            change_details=data.get("change_details"),
            old_values=data.get("old_values"),
            new_values=data.get("new_values"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            created_at=current_time,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def log_action(
        self,
        function_type: str,
        function_id: str,
        action: str,
        user_id: str | None = None,
        change_details: str | None = None,
        old_values: str | None = None,
        new_values: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ):
        """Helper method to log an action"""
        return self.create_action_log(
            {
                "created_by": user_id,
                "function_type": function_type,
                "function_id": function_id,
                "action": action,
                "change_details": change_details,
                "old_values": old_values,
                "new_values": new_values,
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )
