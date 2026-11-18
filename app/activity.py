"""Аналіз навчальної активності: простий індикатор ризику відсіву."""
from dataclasses import dataclass


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
