from typing import Set, Dict
from datetime import datetime
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections and online users"""
    
    def __init__(self):
        # Store active connections: {device_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Store online users: {device_id: {user_info}}
        self.online_users: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, device_id: str, user_id: int = None, platform: str = None):
        """Register a new connection"""
        await websocket.accept()
        self.active_connections[device_id] = websocket
        self.online_users[device_id] = {
            "device_id": device_id,
            "user_id": user_id,
            "platform": platform,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        logger.info(f"User connected: {device_id}, Total: {len(self.online_users)}")
        
        # Broadcast updated count to all connected clients
        await self.broadcast_online_count()
    
    def disconnect(self, device_id: str):
        """Remove a connection"""
        if device_id in self.active_connections:
            del self.active_connections[device_id]
        if device_id in self.online_users:
            del self.online_users[device_id]
        logger.info(f"User disconnected: {device_id}, Total: {len(self.online_users)}")
    
    async def broadcast_online_count(self):
        """Send updated online count to all connected clients"""
        # Count only mobile users (exclude admin viewers)
        mobile_users = {k: v for k, v in self.online_users.items() if not k.startswith('admin-')}
        count = len(mobile_users)
        
        message = {
            "type": "online_count",
            "count": count,
            "timestamp": datetime.utcnow().isoformat(),
            "users": list(mobile_users.values())
        }
        
        # Send to all active connections
        disconnected_users = []
        for device_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {device_id}: {e}")
                disconnected_users.append(device_id)
        
        # Remove dead connections
        for device_id in disconnected_users:
            self.disconnect(device_id)
    
    async def send_personal_message(self, message: str, device_id: str):
        """Send message to specific device"""
        if device_id in self.active_connections:
            try:
                await self.active_connections[device_id].send_text(message)
            except Exception as e:
                logger.error(f"Error sending personal message to {device_id}: {e}")
                self.disconnect(device_id)
    
    def get_online_count(self) -> int:
        """Get current online user count (excluding admin viewers)"""
        return len({k: v for k, v in self.online_users.items() if not k.startswith('admin-')})
    
    def get_online_users(self) -> list:
        """Get list of online users (excluding admin viewers)"""
        mobile_users = {k: v for k, v in self.online_users.items() if not k.startswith('admin-')}
        return list(mobile_users.values())


# Global connection manager instance
manager = ConnectionManager()
