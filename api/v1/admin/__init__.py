from fastapi import APIRouter
from .users import router as user_router
from .areas import router as area_router
from .owners import router as owner_router
from .stalls import router as stall_router
from .stall_contents import router as stall_content_router
from .roles import router as role_router
from .user_roles import router as user_role_router
from .employees import router as employee_router
from .subscription_packages import router as subscription_package_router

router = APIRouter()

router.include_router(user_router)
router.include_router(area_router)
router.include_router(owner_router)
router.include_router(stall_router)
router.include_router(stall_content_router)
router.include_router(role_router)
router.include_router(user_role_router)
router.include_router(employee_router)
router.include_router(subscription_package_router)
