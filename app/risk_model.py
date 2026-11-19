"""Ризик відсіву: логістична регресія з ваг у models/dropout_logreg.json.

Модель навчається окремо (python -m ml.train), а тут використовується лише
формула sigmoid(w·x + b), тому під час роботи API бібліотеки ML не потрібні.
Якщо файлу моделі немає, використовується простий індикатор за правилами.
"""
import json
import math
from pathlib import Path

from .activity import ActivityStats, dropout_risk

MODEL_PATH = Path(__file__).parent.parent / "models" / "dropout_logreg.json"


def load_model(path: Path = MODEL_PATH):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


MODEL = load_model()


def mean_mastery(mastery: dict) -> float:
    return sum(mastery.values()) / len(mastery) if mastery else 0.0


def _values(stats: ActivityStats, avg_mastery: float) -> list:
    return [stats.days_inactive, stats.fail_streak, stats.attempts_last_week, avg_mastery]


def _contributions(model: dict, values: list) -> list:
    """Внесок кожної ознаки в лог-шанси: coef * (x - mean) / scale."""
    return [c * (v - m) / (s or 1.0)
            for c, v, m, s in zip(model["coef"], values, model["mean"], model["scale"])]


def risk(stats: ActivityStats, avg_mastery: float, model=MODEL) -> float:
    """Ймовірність відсіву від 0 до 1 (моделлю або, за її відсутності, за правилами)."""
    if model is None:
        return dropout_risk(stats)
    z = model["intercept"] + sum(_contributions(model, _values(stats, avg_mastery)))
    z = max(-30.0, min(30.0, z))
    return round(1 / (1 + math.exp(-z)), 2)


def risk_factors(stats: ActivityStats, avg_mastery: float, model=MODEL) -> list:
    """Ознаки, відсортовані за внеском у ризик (найбільш підвищувальні першими)."""
    if model is None:
        return []
    pairs = zip(model["features"], _contributions(model, _values(stats, avg_mastery)))
    return sorted(((f, round(c, 3)) for f, c in pairs), key=lambda p: -p[1])
