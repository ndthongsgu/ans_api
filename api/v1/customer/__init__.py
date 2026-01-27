from fastapi import APIRouter
from .customers import router as customer_router
from .listening_histories import router as listening_history_router
from .stalls import router as stall_router
from .stall_contents import router as stall_content_router

router = APIRouter()

router.include_router(customer_router)
router.include_router(listening_history_router)
router.include_router(stall_router)
router.include_router(stall_content_router)
