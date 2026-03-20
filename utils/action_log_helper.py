"""
Helper module for logging actions in the system
"""
from modules.actionLog.services.admin_service import ActionLogService
from sqlalchemy.orm import Session
import json
from typing import Any, Optional


def log_action(
    db: Session,
    function_type: str,
    function_id: str,
    action: str,
    user_id: Optional[str] = None,
    change_details: Optional[str] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """
    Log an action to the database
    
    Args:
        db: SQLAlchemy session
        function_type: Type of entity (e.g., "Roles", "Stalls", "Users")
        function_id: ID of the entity
        action: Type of action (Create, Update, Delete, Activate, Deactivate)
        user_id: ID of user performing the action
        change_details: Description of the change
        old_values: Previous values
        new_values: New values
        ip_address: IP address of the requester
        user_agent: User agent of the requester
    """
    service = ActionLogService(db)
    
    old_values_str = json.dumps(old_values) if old_values else None
    new_values_str = json.dumps(new_values) if new_values else None
    
    service.log_action(
        function_type=function_type,
        function_id=function_id,
        action=action,
        user_id=user_id,
        change_details=change_details,
        old_values=old_values_str,
        new_values=new_values_str,
        ip_address=ip_address,
        user_agent=user_agent,
    )
