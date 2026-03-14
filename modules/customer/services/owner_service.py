import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.listeningHistory import ListeningHistory
from models.owner import Owner
from models.stall import Stall


class ServiceError(Exception):
	def __init__(self, code: str):
		self.code = code
		super().__init__(code)


class OwnerDashboardService:
	def __init__(self, db: Session):
		self.db = db

	def _ensure_owner_id(self, user_id: str) -> str:
		owner = self.db.query(Owner).filter(Owner.user_id == user_id).first()
		if not owner:
			raise ServiceError("profile_not_found")
		return owner.id

	def _period_label(self, ts: int, group_by: str) -> str:
		dt = datetime.fromtimestamp(ts, tz=timezone.utc)
		if group_by == "week":
			year, week, _ = dt.isocalendar()
			return f"{year}-W{week:02d}"
		if group_by == "month":
			return dt.strftime("%Y-%m")
		return dt.strftime("%Y-%m-%d")

	def _month_start(self, dt: datetime) -> datetime:
		return datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)

	def _build_period_labels(self, from_ts: int, to_ts: int, group_by: str) -> list[str]:
		from_dt = datetime.fromtimestamp(from_ts, tz=timezone.utc)
		to_dt = datetime.fromtimestamp(to_ts, tz=timezone.utc)

		labels: list[str] = []
		if group_by == "day":
			cursor = datetime(from_dt.year, from_dt.month, from_dt.day, tzinfo=timezone.utc)
			end = datetime(to_dt.year, to_dt.month, to_dt.day, tzinfo=timezone.utc)
			while cursor <= end:
				labels.append(cursor.strftime("%Y-%m-%d"))
				cursor += timedelta(days=1)
			return labels

		if group_by == "week":
			from_monday = datetime(
				from_dt.year,
				from_dt.month,
				from_dt.day,
				tzinfo=timezone.utc,
			) - timedelta(days=from_dt.weekday())
			to_monday = datetime(
				to_dt.year,
				to_dt.month,
				to_dt.day,
				tzinfo=timezone.utc,
			) - timedelta(days=to_dt.weekday())

			cursor = from_monday
			while cursor <= to_monday:
				year, week, _ = cursor.isocalendar()
				labels.append(f"{year}-W{week:02d}")
				cursor += timedelta(days=7)
			return labels

		cursor = self._month_start(from_dt)
		end = self._month_start(to_dt)
		while cursor <= end:
			labels.append(cursor.strftime("%Y-%m"))
			if cursor.month == 12:
				cursor = datetime(cursor.year + 1, 1, 1, tzinfo=timezone.utc)
			else:
				cursor = datetime(cursor.year, cursor.month + 1, 1, tzinfo=timezone.utc)
		return labels

	def get_dashboard(self, user_id: str, group_by: str, from_timestamp: int | None, to_timestamp: int | None):
		owner_id = self._ensure_owner_id(user_id)

		now = int(time.time())
		to_ts = to_timestamp if to_timestamp is not None else now
		from_ts = from_timestamp if from_timestamp is not None else (to_ts - 30 * 24 * 60 * 60)

		if from_ts > to_ts:
			raise ServiceError("invalid_time_range")

		stall_ids = [
			stall_id
			for (stall_id,) in self.db.query(Stall.id).filter(Stall.owner_id == owner_id).all()
		]

		if not stall_ids:
			labels = self._build_period_labels(from_ts, to_ts, group_by)
			return {
				"totalListenCount": 0,
				"averageRating": 0.0,
				"totalFavorites": 0,
				"listenChart": [{"period": label, "listenCount": 0} for label in labels],
			}

		total_listen_count = (
			self.db.query(func.count(ListeningHistory.id))
			.filter(ListeningHistory.stall_id.in_(stall_ids))
			.scalar()
			or 0
		)

		weighted_sum, total_reviews = (
			self.db.query(
				func.coalesce(func.sum(Stall.average_rating * Stall.total_reviews), 0),
				func.coalesce(func.sum(Stall.total_reviews), 0),
			)
			.filter(Stall.owner_id == owner_id)
			.first()
		)
		average_rating = 0.0
		if total_reviews:
			average_rating = round(float(weighted_sum) / float(total_reviews), 2)

		# The current schema does not have a favorite table yet.
		total_favorites = 0

		listened_rows = (
			self.db.query(ListeningHistory.listened_at)
			.filter(
				ListeningHistory.stall_id.in_(stall_ids),
				ListeningHistory.listened_at >= from_ts,
				ListeningHistory.listened_at <= to_ts,
			)
			.all()
		)

		period_counts = defaultdict(int)
		for (listened_at,) in listened_rows:
			if listened_at is None:
				continue
			label = self._period_label(listened_at, group_by)
			period_counts[label] += 1

		labels = self._build_period_labels(from_ts, to_ts, group_by)
		chart = [{"period": label, "listenCount": period_counts[label]} for label in labels]

		return {
			"totalListenCount": int(total_listen_count),
			"averageRating": average_rating,
			"totalFavorites": int(total_favorites),
			"listenChart": chart,
		}
