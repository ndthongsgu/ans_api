from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from modules.auth.controllers.admin_controller import get_current_user
from models.user import User

router = APIRouter(prefix="/permissions")

# Permission modules definition matching frontend
PERMISSION_MODULES = [
    {
        "module": "AREA",
        "label": "Khu vực",
        "description": "Quản lý khu vực",
        "urlPageView": "/area",
        "permissions": [
            {"code": "AREA_VIEW", "label": "Xem"},
            {"code": "AREA_CREATE", "label": "Tạo"},
            {"code": "AREA_UPDATE", "label": "Cập nhật"},
            {"code": "AREA_DELETE", "label": "Xóa"},
        ],
    },
    {
        "module": "STALL",
        "label": "Gian hàng",
        "description": "Quản lý gian hàng",
        "urlPageView": "/stall",
        "permissions": [
            {"code": "STALL_VIEW", "label": "Xem"},
            {"code": "STALL_CREATE", "label": "Tạo"},
            {"code": "STALL_UPDATE", "label": "Cập nhật"},
            {"code": "STALL_DELETE", "label": "Xóa"},
        ],
    },
    {
        "module": "STALL_CONTENT",
        "label": "Nội dung thuyết minh",
        "description": "Quản lý nội dung thuyết minh",
        "urlPageView": "/stall-content",
        "permissions": [
            {"code": "STALL_CONTENT_VIEW", "label": "Xem"},
            {"code": "STALL_CONTENT_CREATE", "label": "Tạo"},
            {"code": "STALL_CONTENT_UPDATE", "label": "Cập nhật"},
            {"code": "STALL_CONTENT_DELETE", "label": "Xóa"},
        ],
    },
    {
        "module": "USER",
        "label": "Người dùng",
        "description": "Quản lý người dùng",
        "urlPageView": "/user",
        "permissions": [
            {"code": "USER_VIEW", "label": "Xem"},
            {"code": "USER_CREATE", "label": "Tạo"},
            {"code": "USER_UPDATE", "label": "Cập nhật"},
            {"code": "USER_DELETE", "label": "Xóa"},
        ],
    },
    {
        "module": "ROLE",
        "label": "Vai trò & phân quyền",
        "description": "Quản lý vai trò và phân quyền",
        "urlPageView": "/role",
        "permissions": [
            {"code": "ROLE_VIEW", "label": "Xem"},
            {"code": "ROLE_CREATE", "label": "Tạo"},
            {"code": "ROLE_UPDATE", "label": "Cập nhật"},
            {"code": "ROLE_DELETE", "label": "Xóa"},
        ],
    },
    {
        "module": "LISTENING_HISTORY",
        "label": "Lịch sử nghe thuyết minh",
        "description": "Xem lịch sử nghe thuyết minh",
        "urlPageView": "/listening-history",
        "permissions": [{"code": "LISTENING_HISTORY_VIEW", "label": "Xem"}],
    },
    {
        "module": "CUSTOMER",
        "label": "Khách hàng",
        "description": "Quản lý khách hàng",
        "urlPageView": "/customer",
        "permissions": [
            {"code": "CUSTOMER_VIEW", "label": "Xem"},
            {"code": "CUSTOMER_CREATE", "label": "Tạo"},
            {"code": "CUSTOMER_UPDATE", "label": "Cập nhật"},
            {"code": "CUSTOMER_DELETE", "label": "Xóa"},
        ],
    },
    {
        "module": "EMPLOYEE",
        "label": "Nhân viên",
        "description": "Quản lý nhân viên",
        "urlPageView": "/employee",
        "permissions": [
            {"code": "EMPLOYEE_VIEW", "label": "Xem"},
            {"code": "EMPLOYEE_CREATE", "label": "Tạo"},
            {"code": "EMPLOYEE_UPDATE", "label": "Cập nhật"},
            {"code": "EMPLOYEE_DELETE", "label": "Xóa"},
        ],
    },
    {
        "module": "STAFF",
        "label": "Nhân viên",
        "description": "Quản lý nhân viên",
        "urlPageView": "/staff",
        "permissions": [
            {"code": "STAFF_VIEW", "label": "Xem"},
            {"code": "STAFF_CREATE", "label": "Tạo"},
            {"code": "STAFF_UPDATE", "label": "Cập nhật"},
            {"code": "STAFF_DELETE", "label": "Xóa"},
        ],
    },
]


@router.get("/")
def get_all_permission_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Get all permission modules"""
    return PERMISSION_MODULES


@router.get("/{module_code}")
def get_module_permissions(
    module_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    accept_language: str | None = Header(None),
):
    """Get permissions for a specific module"""
    for module in PERMISSION_MODULES:
        if module["module"] == module_code:
            return module
    raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu")
