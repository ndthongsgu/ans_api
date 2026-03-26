from typing import List, Dict
from common.enums.permissionCode import PermissionCode


Permission: List[Dict] = [
    # ===== AREA =====
    {
        "code": PermissionCode.AREA_VIEW,
        "module": "AREA",
        "label": "Xem khu vực"
    },
    {
        "code": PermissionCode.AREA_CREATE,
        "module": "AREA",
        "label": "Tạo khu vực"
    },
    {
        "code": PermissionCode.AREA_UPDATE,
        "module": "AREA",
        "label": "Cập nhật khu vực"
    },
    {
        "code": PermissionCode.AREA_DELETE,
        "module": "AREA",
        "label": "Xóa khu vực"
    },

    # ===== STALL =====
    {
        "code": PermissionCode.STALL_VIEW,
        "module": "STALL",
        "label": "Xem gian hàng"
    },
    {
        "code": PermissionCode.STALL_CREATE,
        "module": "STALL",
        "label": "Tạo gian hàng"
    },
    {
        "code": PermissionCode.STALL_UPDATE,
        "module": "STALL",
        "label": "Cập nhật gian hàng"
    },
    {
        "code": PermissionCode.STALL_DELETE,
        "module": "STALL",
        "label": "Xóa gian hàng"
    },

    # ===== STALL CONTENT =====
    {
        "code": PermissionCode.STALL_CONTENT_VIEW,
        "module": "STALL_CONTENT",
        "label": "Xem nội dung thuyết minh"
    },
    {
        "code": PermissionCode.STALL_CONTENT_CREATE,
        "module": "STALL_CONTENT",
        "label": "Tạo nội dung thuyết minh"
    },
    {
        "code": PermissionCode.STALL_CONTENT_UPDATE,
        "module": "STALL_CONTENT",
        "label": "Cập nhật nội dung thuyết minh"
    },
    {
        "code": PermissionCode.STALL_CONTENT_DELETE,
        "module": "STALL_CONTENT",
        "label": "Xóa nội dung thuyết minh"
    },

    # ===== USER =====
    {
        "code": PermissionCode.USER_VIEW,
        "module": "USER",
        "label": "Xem người dùng"
    },
    {
        "code": PermissionCode.USER_CREATE,
        "module": "USER",
        "label": "Tạo người dùng"
    },
    {
        "code": PermissionCode.USER_UPDATE,
        "module": "USER",
        "label": "Cập nhật người dùng"
    },
    {
        "code": PermissionCode.USER_DELETE,
        "module": "USER",
        "label": "Xóa người dùng"
    },

    # ===== ROLE =====
    {
        "code": PermissionCode.ROLE_VIEW,
        "module": "ROLE",
        "label": "Xem vai trò & phân quyền"
    },
    {
        "code": PermissionCode.ROLE_CREATE,
        "module": "ROLE",
        "label": "Tạo vai trò"
    },
    {
        "code": PermissionCode.ROLE_UPDATE,
        "module": "ROLE",
        "label": "Cập nhật vai trò"
    },
    {
        "code": PermissionCode.ROLE_DELETE,
        "module": "ROLE",
        "label": "Xóa vai trò"
    },

    # ===== LISTENING HISTORY =====
    {
        "code": PermissionCode.LISTENING_HISTORY_VIEW,
        "module": "LISTENING_HISTORY",
        "label": "Xem lịch sử nghe thuyết minh"
    },

    # ===== CUSTOMER =====
    {
        "code": PermissionCode.CUSTOMER_VIEW,
        "module": "CUSTOMER",
        "label": "Xem khách hàng"
    },
    {
        "code": PermissionCode.CUSTOMER_CREATE,
        "module": "CUSTOMER",
        "label": "Tạo khách hàng"
    },
    {
        "code": PermissionCode.CUSTOMER_UPDATE,
        "module": "CUSTOMER",
        "label": "Cập nhật khách hàng"
    },
    {
        "code": PermissionCode.CUSTOMER_DELETE,
        "module": "CUSTOMER",
        "label": "Xóa khách hàng"
    },

    # ===== EMPLOYEE =====
    {
        "code": PermissionCode.EMPLOYEE_VIEW,
        "module": "EMPLOYEE",
        "label": "Xem nhân viên"
    },
    {
        "code": PermissionCode.EMPLOYEE_CREATE,
        "module": "EMPLOYEE",
        "label": "Tạo nhân viên"
    },
    {
        "code": PermissionCode.EMPLOYEE_UPDATE,
        "module": "EMPLOYEE",
        "label": "Cập nhật nhân viên"
    },
    {
        "code": PermissionCode.EMPLOYEE_DELETE,
        "module": "EMPLOYEE",
        "label": "Xóa nhân viên"
    },
]
