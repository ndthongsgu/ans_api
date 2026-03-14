from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from modules.auth.controllers.customer_controller import get_current_user
from modules.customer_subscription_package.dto.owner_dto import PackageOut, SubscriptionOut
from modules.customer_subscription_package.services.owner_service import (
	ServiceError,
	SubscriptionService,
	parse_package_features,
)
from utils.i18n import t


router = APIRouter(prefix="/subscription-packages")


@router.get("/", response_model=List[PackageOut])
def list_packages(
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	service = SubscriptionService(db)
	packages = service.list_packages(active_only=True)
	return [
		PackageOut(
			id=package.id,
			name=package.name,
			description=package.description,
			price=float(package.price),
			duration=package.duration,
			features=parse_package_features(package.features),
		)
		for package in packages
	]


@router.post("/{pkg_id}/purchase")
def purchase_package(
	pkg_id: str,
	current_user: object = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	service = SubscriptionService(db)
	try:
		owner, _package = service.purchase_package(current_user.id, pkg_id)
		return {
			"message": t("purchase_success", accept_language),
			"expiresAt": owner.subscription_expires_at,
		}
	except ServiceError as exc:
		raise HTTPException(status_code=400, detail=t(exc.code, accept_language))


@router.get("/my-subscription", response_model=SubscriptionOut)
def my_subscription(
	current_user: object = Depends(get_current_user),
	db: Session = Depends(get_db),
	accept_language: str | None = Header(None),
):
	service = SubscriptionService(db)
	subscription = service.get_owner_subscription(current_user.id)
	if subscription is None:
		raise HTTPException(status_code=404, detail=t("profile_not_found", accept_language))

	package = subscription["package"]
	return SubscriptionOut(
		packageId=package.id if package else None,
		packageName=package.name if package else None,
		expiresAt=subscription["expires_at"],
		active=subscription["active"],
	)
