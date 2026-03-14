from pydantic import BaseModel


class ListenChartPoint(BaseModel):
	period: str
	listenCount: int


class OwnerDashboardResponse(BaseModel):
	totalListenCount: int
	averageRating: float
	totalFavorites: int
	listenChart: list[ListenChartPoint]
