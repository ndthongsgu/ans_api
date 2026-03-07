from fastapi import APIRouter
from modules.auth.controllers.admin_controller import router as auth_router
from modules.employee.controllers.admin_employee_controller import router as employee_router
from modules.customer.controllers.admin_controller import router as customer_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(employee_router)
router.include_router(customer_router)