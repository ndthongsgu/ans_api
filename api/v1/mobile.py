from fastapi import APIRouter
from modules.auth.controllers.mobile_controller import router as auth_router
from modules.auth.controllers.ws_controller import router as ws_router
from modules.stall.controllers.mobile_controller import router as stall_router
from modules.stall_content.controllers.mobile_controller import router as stall_content_router
from modules.notification.controllers.mobile_controller import router as notification_router
from modules.listeningHistory.controllers.mobile_controller import router as listening_history_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(ws_router)
router.include_router(stall_router)
router.include_router(stall_content_router)
router.include_router(notification_router)
router.include_router(listening_history_router)