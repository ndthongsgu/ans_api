import time
from sqlalchemy.orm import Session

from models.owner import Owner
from models.user import User
from modules.auth.dto.owner_dto import RegisterRequest, UpdateProfileRequest
from utils.security import hash_password, verify_password


class ServiceError(Exception):
	def __init__(self, code: str):
		self.code = code
		super().__init__(code)


class OwnerService:
	def __init__(self, db: Session):
		self.db = db

	# def find_by_username(self, username: str):
	# 	return self.db.query(User).filter(User.username == username).first()

	def find_by_email(self, email: str):
		return self.db.query(User).filter(User.email == email).first()

	def find_by_email_excluding_user(self, email: str, user_id: str):
		return self.db.query(User).filter(User.email == email, User.id != user_id).first()

	def find_by_phone(self, phone: str):
		return self.db.query(Owner).filter(Owner.phone == phone).first()

	def find_by_phone_excluding_owner(self, phone: str, owner_id: str):
		return self.db.query(Owner).filter(Owner.phone == phone, Owner.id != owner_id).first()

	def authenticate_owner(self, username: str, password: str):
		# username can be email or phone
		user = self.db.query(User).filter((User.email == username)).first()
		
		if not user:
			owner = self.db.query(Owner).filter(Owner.phone == username).first()
			if owner:
				user = self.db.query(User).filter(User.id == owner.user_id).first()
		
		if not user:
			return None
		if not verify_password(password, user.password_hash):
			return None
		owner = self.db.query(Owner).filter(Owner.user_id == user.id).first()
		if not owner:
			return None
		return user

	def create_owner(self, register_request: RegisterRequest):
		# Check duplicate email
		if self.find_by_email(register_request.email):
			raise ServiceError("email_exists")
		
		# Check duplicate phone
		if self.find_by_phone(register_request.phone):
			raise ServiceError("phone_exists")

		# Use email as username
		username = register_request.email

		user = User(
			username=username,
			email=register_request.email,
			password_hash=hash_password(register_request.password),
			created_at=int(time.time()),
		)
		self.db.add(user)
		self.db.commit()
		self.db.refresh(user)

		owner = Owner(
			user_id=user.id,
			full_name=register_request.full_name,
			phone=register_request.phone,
			business_name=register_request.business_name,
			business_address=register_request.business_address,
		)
		self.db.add(owner)
		self.db.commit()
		self.db.refresh(owner)

		return user, owner

	def get_owner_profile(self, user_id: str):
		return self.db.query(Owner).filter(Owner.user_id == user_id).first()

	def update_owner_profile(self, user_id: str, payload: UpdateProfileRequest):
		user = self.db.query(User).filter(User.id == user_id).first()
		if not user:
			raise ServiceError("user_not_found")

		owner = self.get_owner_profile(user_id)
		if not owner:
			raise ServiceError("profile_not_found")

		if payload.email and self.find_by_email_excluding_user(payload.email, user.id):
			raise ServiceError("email_exists")

		if payload.phone and self.find_by_phone_excluding_owner(payload.phone, owner.id):
			raise ServiceError("phone_exists")

		if payload.full_name is not None:
			owner.full_name = payload.full_name
		if payload.phone is not None:
			owner.phone = payload.phone
		if payload.business_name is not None:
			owner.business_name = payload.business_name
		if payload.business_address is not None:
			owner.business_address = payload.business_address
		if payload.email is not None:
			user.email = payload.email
			user.username = payload.email

		self.db.commit()
		self.db.refresh(user)
		self.db.refresh(owner)
		return user, owner
