from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.services.ws_manager import manager
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws")


@router.websocket("/online/{device_id}")
async def websocket_endpoint(device_id: str, websocket: WebSocket):
    """
    WebSocket endpoint for tracking online users in real-time
    
    For mobile users: device_id = actual device ID
    For admin viewers: device_id = "admin-xxx" (will not count as online user)
    
    Expected message format:
    {
        "action": "connect" or "disconnect" or "ping",
        "device_id": "unique-device-id",
        "user_id": optional user_id,
        "platform": "android" or "ios"
    }
    """
    
    user_id = None
    platform = None
    is_admin = device_id.startswith('admin-')
    
    try:
        # Accept the connection
        await manager.connect(websocket, device_id, user_id, platform)
        if is_admin:
            logger.info(f"Admin viewer connected: {device_id}")
        else:
            logger.info(f"Mobile user connected: {device_id}")
        
        # Listen for incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "ping":
                # Send pong response with online count
                await websocket.send_json({
                    "type": "pong",
                    "online_count": manager.get_online_count()
                })
            
            elif action == "update_user":
                # Update user_id and platform info (only for mobile users)
                if not is_admin:
                    user_id = message.get("user_id")
                    platform = message.get("platform")
                    if device_id in manager.online_users:
                        manager.online_users[device_id].update({
                            "user_id": user_id,
                            "platform": platform
                        })
                    await manager.broadcast_online_count()
            
            logger.debug(f"Message from {device_id}: {action}")
    
    except WebSocketDisconnect:
        if is_admin:
            logger.info(f"Admin viewer disconnected: {device_id}")
        else:
            logger.info(f"Mobile user disconnected: {device_id}")
        manager.disconnect(device_id)
        if not is_admin:
            await manager.broadcast_online_count()
    
    except Exception as e:
        logger.error(f"WebSocket error for {device_id}: {e}")
        manager.disconnect(device_id)
        if not is_admin:
            await manager.broadcast_online_count()


@router.get("/online/count")
def get_online_count():
    """Get current online user count from active socket connections"""
    count = manager.get_online_count()
    return {"online_count": count}


@router.get("/online/users")
def get_online_users(limit: int = 100):
    """Get list of online users from active socket connections"""
    users = manager.get_online_users()
    if limit:
        users = users[:limit]
    return {
        "total": len(users),
        "users": users
    }

