from fastapi import APIRouter
from .owners import router as owner_router
from .stalls import router as stall_router
from .stall_contents import router as stall_content_router
from .subscription_packages import router as subscription_package_router

router = APIRouter()

router.include_router(owner_router)
router.include_router(stall_router)
router.include_router(stall_content_router)
router.include_router(subscription_package_router)
