import sys
import os
import uuid
import time
import json

# Add current dir to path to import modules
sys.path.append(os.getcwd())

from core.database import SessionLocal
from models.user import User
from models.role import Role
from models.userRole import UserRole
from models.owner import Owner
from models.customer import Customer
from models.employee import Employee
from models.area import Area
from utils.security import hash_password

def seed_data():
    db = SessionLocal()
    try:
        print("🌱 Seeding data...")

        # 1. Define Roles
        
        # Permissions for OWNER
        owner_permissions = json.dumps({
            "STALL": {
                "code": "STALL",
                "name": "Quản lý quán",
                "description": "Quản lý thông tin quán",
                "urlPageView": "/stall-manager",
                "isCanRead": True, "isCanCreate": True, "isCanUpdate": True, "isCanDelete": True,
                "isCanActivate": True, "isCanDeactivate": True, "isCanImport": False, "isCanExport": False
            }
        })

        roles_data = [
            {"code": "ADMIN", "name": "Administrator", "permissions": None}, # Admin bypass checks
            {"code": "OWNER", "name": "Shop Owner", "permissions": owner_permissions},
            {"code": "CUSTOMER", "name": "Customer", "permissions": "{}"},
            {"code": "EMPLOYEE", "name": "Employee", "permissions": "{}"},
        ]

        roles_map = {} # code -> role_obj

        for r_data in roles_data:
            role = db.query(Role).filter(Role.code == r_data["code"]).first()
            if not role:
                role = Role(
                    id=str(uuid.uuid4()),
                    code=r_data["code"],
                    name=r_data["name"],
                    permissions=r_data["permissions"]
                )
                db.add(role)
                print(f"✅ Created Role: {r_data['name']}")
            else:
                 print(f"ℹ️ Role exists: {r_data['name']}. Updating permissions...")
                 role.permissions = r_data["permissions"]
                 db.add(role)
            roles_map[r_data["code"]] = role
        
        db.commit()

        # 2. Define Users
        users_config = [
            {
                "username": "admin", "email": "admin@example.com", "password": "1",
                "role_code": "ADMIN", "profile_model": None
            },
            {
                "username": "owner1", "email": "owner1@example.com", "password": "1",
                "role_code": "OWNER", 
                "profile_model": Owner, "profile_data": {"full_name": "Nguyen Van Chu Quan", "phone": "0901112222"}
            },
            {
                "username": "customer1", "email": "customer1@example.com", "password": "1",
                "role_code": "CUSTOMER", 
                "profile_model": Customer, "profile_data": {"full_name": "Tran Thi Khach Hang", "phone": "0903334444"}
            },
            {
                "username": "employee1", "email": "employee1@example.com", "password": "1",
                "role_code": "EMPLOYEE", 
                "profile_model": Employee, "profile_data": {"full_name": "Le Van Nhan Vien", "phone": "0905556666", "position": "Manager"}
            },
        ]

        timestamp = int(time.time())

        for u_conf in users_config:
            user = db.query(User).filter(User.username == u_conf["username"]).first()
            if not user:
                user_id = str(uuid.uuid4())
                user = User(
                    id=user_id,
                    username=u_conf["username"],
                    email=u_conf["email"],
                    password_hash=hash_password(u_conf["password"]),
                    created_at=timestamp,
                    is_active=True
                )
                db.add(user)
                db.flush() # flush to get user.id if needed, though we set it manually

                # Link Role
                role = roles_map.get(u_conf["role_code"])
                if role:
                    user_role = UserRole(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        role_id=role.id
                    )
                    db.add(user_role)
                
                # Create Profile
                if u_conf["profile_model"]:
                    profile_data = u_conf["profile_data"]
                    profile_data["id"] = str(uuid.uuid4())
                    profile_data["user_id"] = user_id
                    profile = u_conf["profile_model"](**profile_data)
                    db.add(profile)

                print(f"✅ Created User: {u_conf['username']} (Pass: {u_conf['password']})")
            else:
                print(f"ℹ️ User exists: {u_conf['username']}")

        db.commit()

        # Seed Areas
        areas_data = [
            {"name": "Khu vực Trung Tâm", "lat": 10.762622, "long": 106.660172},
            {"name": "Khu vực Phía Bắc", "lat": 10.8, "long": 106.7}
        ]
        
        print("\n--- Available Areas (Copy ID to create Stall) ---")
        for a_data in areas_data:
            area = db.query(Area).filter(Area.name == a_data["name"]).first()
            if not area:
                area = Area(
                    id=str(uuid.uuid4()),
                    name=a_data["name"],
                    center_lat=a_data["lat"],
                    center_long=a_data["long"]
                )
                db.add(area)
                db.commit() # Commit to get ID
                print(f"✅ Created Area: {a_data['name']} - ID: {area.id}")
            else:
                print(f"ℹ️ Area: {a_data['name']} - ID: {area.id}")

        print("🚀 Seed data completed successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
