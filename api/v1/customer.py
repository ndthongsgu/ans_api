from fastapi import APIRouter
from modules.auth.controllers.customer_controller import router as auth_router
from modules.customer_subscription_package.controllers.customer_controller import router as subscription_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(subscription_router)
