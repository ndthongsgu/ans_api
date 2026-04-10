from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user import User
from models.owner import Owner


def ensure_owner(user: User, db: Session, locale: str | None = None):
    owner = db.query(Owner).filter(Owner.user_id == user.id).first()
    if not owner:
        raise HTTPException(status_code=403, detail="Không phải chủ quán, không có quyền truy cập")
    return owner