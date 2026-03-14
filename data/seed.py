import os
import sys

# ensure project root is on path so 'core' and other packages can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.database import SessionLocal
from models.user import User
from models.role import Role
from models.userRole import UserRole
from utils.security import hash_password
import time


def seed_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@example.com"
        admin_username = "admin"
        admin_password = "admin123"  # You may change this in production

        # ensure ADMIN role exists
        role = db.query(Role).filter(Role.code == "ADMIN").first()
        if not role:
            role = Role(code="ADMIN", name="Administrator")
            db.add(role)
            db.commit()
            db.refresh(role)
            print("created ADMIN role")

        # check for existing user by email or username
        user = (
            db.query(User)
            .filter((User.email == admin_email) | (User.username == admin_username))
            .first()
        )
        if not user:
            user = User(
                username=admin_username,
                email=admin_email,
                password_hash=hash_password(admin_password),
                created_at=int(time.time()),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            user_role = UserRole(user_id=user.id, role_id=role.id, code=role.code)
            db.add(user_role)
            db.commit()
            print(f"admin user created ({admin_email}) with password '{admin_password}'")
        else:
            print("admin user alread exists in database")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
