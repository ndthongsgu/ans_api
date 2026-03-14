from pydantic import BaseModel


class PackageOut(BaseModel):
	id: str
	name: str
	description: str | None = None
	price: float
	duration: int
	features: list[str] | None = None


class SubscriptionOut(BaseModel):
	packageId: str | None = None
	packageName: str | None = None
	expiresAt: int | None = None
	active: bool = False
