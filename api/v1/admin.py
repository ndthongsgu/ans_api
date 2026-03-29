from fastapi import APIRouter
from modules.auth.controllers.admin_controller import router as auth_router
from modules.employee.controllers.admin_controller import router as employee_router
from modules.customer.controllers.admin_controller import router as customer_router
from modules.role.controllers.admin_controller import router as role_router
from modules.owner.controllers.admin_controller import router as owner_router
from modules.stall.controllers.admin_controller import router as stall_router
from modules.stallContent.controllers.admin_controller import router as stall_content_router
from modules.permission.controllers.admin_controller import router as permission_router
from modules.notification.controllers.admin_controller import router as notification_router
from modules.subscriptionPackage.controllers.admin_controller import router as subscription_package_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(employee_router)
router.include_router(customer_router)
router.include_router(role_router)
router.include_router(owner_router)
router.include_router(stall_router)
router.include_router(stall_content_router)
router.include_router(permission_router)
router.include_router(notification_router)
router.include_router(subscription_package_router)