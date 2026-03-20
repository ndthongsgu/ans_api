from sqlalchemy import (
    Column, String, Integer, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from models.base import BaseModel


class ActionLog(BaseModel):
    __tablename__ = "action_logs"

    # User who performed the action
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # The entity type being acted upon (e.g., "Stalls", "Roles", "Users")
    function_type = Column(String(100), nullable=False)
    
    # The ID of the entity
    function_id = Column(String(36), nullable=False)
    
    # Type of action: Create, Update, Delete, Activate, Deactivate, etc.
    action = Column(String(50), nullable=False)
    
    # Details of the change (JSON string or text description)
    change_details = Column(Text, nullable=True)
    
    # Before and after values (JSON)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    
    # IP address from which action was performed
    ip_address = Column(String(45), nullable=True)
    
    # User agent / device info
    user_agent = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="action_logs")
