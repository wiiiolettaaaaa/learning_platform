"""Аналіз навчальної активності: простий індикатор ризику відсіву."""
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ActivityStats:
    days_inactive: int = 0
    fail_streak: int = 0
    attempts_last_week: int = 0


def dropout_risk(s: ActivityStats) -> float:
    """Ризик від 0 до 1 за простими правилами (базова версія, пізніше ML)."""
    risk = 0.05 * min(s.days_inactive, 10)
    risk += 0.1 * min(s.fail_streak, 5)
    if s.attempts_last_week == 0:
        risk += 0.2
    return round(min(risk, 1.0), 2)


def build_stats(attempts: list, fail_streak: int, now: datetime) -> ActivityStats:
    """Збирає статистику активності зі списку часових міток спроб."""
    week_ago = now - timedelta(days=7)
    return ActivityStats(
        days_inactive=(now - max(attempts)).days if attempts else 0,
        fail_streak=fail_streak,
        attempts_last_week=sum(1 for t in attempts if t >= week_ago),
    )
