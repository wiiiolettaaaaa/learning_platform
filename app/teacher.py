"""Зведення для кабінету викладача: стан студентів і складні теми."""
from datetime import datetime

from .activity import build_stats
from .risk_model import mean_mastery, risk


def student_summary(uid: str, u: dict, now: datetime) -> dict:
    stats = build_stats(u["attempts"], u["fails"], now)
    mastery = u["mastery"]
    avg = mean_mastery(mastery)
    return {
        "user_id": uid,
        "avg_mastery": round(avg, 3),
        "topics_started": len(mastery),
        "attempts_last_week": stats.attempts_last_week,
        "days_inactive": stats.days_inactive,
        "dropout_risk": risk(stats, avg),
    }


def topic_summary(db: dict, topic_ids: list) -> list:
    rows = []
    for t in topic_ids:
        correct = total = 0
        masteries = []
        for u in db.values():
            r = u.get("results", {}).get(t)
            if r:
                correct += r["correct"]
                total += r["total"]
            if t in u["mastery"]:
                masteries.append(u["mastery"][t])
        rows.append({
            "topic_id": t,
            "attempts": total,
            "accuracy": round(correct / total, 3) if total else None,
            "avg_mastery": round(sum(masteries) / len(masteries), 3) if masteries else None,
        })
    return rows
