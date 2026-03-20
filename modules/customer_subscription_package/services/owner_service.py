import json
import time

from sqlalchemy.orm import Session

from models.owner import Owner
from models.subscription_package import SubscriptionPackage


class ServiceError(Exception):
	def __init__(self, code: str):
		self.code = code
		super().__init__(code)


class SubscriptionService:
	def __init__(self, db: Session):
		self.db = db

	def list_packages(self, active_only: bool = True):
		query = self.db.query(SubscriptionPackage)
		if active_only:
			query = query.filter(SubscriptionPackage.is_deleted == False)
		return query.order_by(SubscriptionPackage.price.asc()).all()

	def get_package(self, package_id: str):
		return self.db.query(SubscriptionPackage).filter(SubscriptionPackage.id == package_id).first()

	def get_owner(self, user_id: str):
		return self.db.query(Owner).filter(Owner.user_id == user_id).first()

	def purchase_package(self, user_id: str, package_id: str):
		owner = self.get_owner(user_id)
		if not owner:
			raise ServiceError("profile_not_found")

		package = self.get_package(package_id)
		if not package:
			raise ServiceError("package_not_found")

		expires_at = int(time.time()) + int(package.duration) * 24 * 60 * 60
		owner.subscription_package_id = package.id
		owner.subscription_expires_at = expires_at
		self.db.commit()
		self.db.refresh(owner)
		return owner, package

	def get_owner_subscription(self, user_id: str):
		owner = self.get_owner(user_id)
		if not owner:
			return None

		package = None
		if owner.subscription_package_id:
			package = self.get_package(owner.subscription_package_id)

		is_active = bool(owner.subscription_expires_at and int(owner.subscription_expires_at) > int(time.time()))
		return {
			"package": package,
			"expires_at": owner.subscription_expires_at,
			"active": is_active,
		}


def parse_package_features(features: str | None) -> list[str] | None:
	if not features:
		return None

	try:
		parsed = json.loads(features)
		if isinstance(parsed, list):
			return [str(item) for item in parsed]
	except json.JSONDecodeError:
		pass

	return [item.strip() for item in features.split(",") if item.strip()]
