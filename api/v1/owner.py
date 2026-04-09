from fastapi import APIRouter
from modules.auth.controllers.owner_controller import router as auth_router
from modules.customer.controllers.owner_controller import router as dashboard_router
from modules.stall.controllers.owner_controller import router as stall_router
from modules.stall_content.controllers.owner_controller import router as stall_content_router
from modules.subscription_package.controllers.owner_controller import router as subscription_package_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(dashboard_router)
router.include_router(stall_router)
router.include_router(stall_content_router)
router.include_router(subscription_package_router)
