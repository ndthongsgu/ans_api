from pydantic import BaseModel, validator
from typing import Any, List, Optional
import json

class RolePageRequest(BaseModel):
    page: int
    size: int
    sortBy: Optional[str] = None
    sortDirection: Optional[str] = "DESC"
    # filters
    code: Optional[str] = None
    name: Optional[str] = None


def normalize_permissions(value: Any) -> Optional[List[str]]:
    if value is None:
        return None

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except ValueError:
            return [item.strip() for item in value.split(",") if item.strip()]

        return [str(parsed).strip()] if str(parsed).strip() else None

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    normalized = str(value).strip()
    return [normalized] if normalized else None


class RoleCreate(BaseModel):
    code: str
    name: str
    permissions: Optional[List[str]] = None

    _normalize_permissions = validator("permissions", pre=True, allow_reuse=True)(normalize_permissions)


class RoleUpdate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

    _normalize_permissions = validator("permissions", pre=True, allow_reuse=True)(normalize_permissions)


class RoleOut(BaseModel):
    id: str
    code: str
    name: str
    permissions: Optional[List[str]]
