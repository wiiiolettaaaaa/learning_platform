"""Рекомендації: наступна тема на графі знань + повторення із забуванням."""
import math
from dataclasses import dataclass
from .graph import KnowledgeGraph

MASTERED = 0.85  # поріг засвоєння теми
HALF_LIFE_DAYS = 7.0  # швидкість забування


@dataclass
class Recommendation:
    topic_id: str
    kind: str          # "learn" або "review"
    explanation: str   # пояснення, чому саме це


def effective_mastery(p: float, days_since: float) -> float:
    """Знання поступово «забувається» без повторення."""
    return p * math.pow(0.5, days_since / HALF_LIFE_DAYS)


def recommend(graph: KnowledgeGraph, mastery: dict, days_since: dict):
    # 1) повторення: тема була засвоєна, але забулась
    for t, p in mastery.items():
        if p >= MASTERED and effective_mastery(p, days_since.get(t, 0)) < 0.6:
            return Recommendation(t, "review",
                f"Тему «{graph.title(t)}» варто повторити: минуло {days_since.get(t, 0):.0f} дн. без практики.")
    # 2) нова тема: усі передумови засвоєні, сама тема ще ні
    candidates = [
        t for t in graph.topics
        if mastery.get(t, 0.0) < MASTERED
        and all(mastery.get(r, 0.0) >= MASTERED for r in graph.prerequisites(t))
    ]
    if not candidates:
        return None
    best = max(candidates, key=lambda t: mastery.get(t, 0.0))  # найближча до засвоєння
    return Recommendation(best, "learn",
        f"Тема «{graph.title(best)}»: передумови засвоєно, поточний рівень {mastery.get(best, 0.0):.0%}.")
