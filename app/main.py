"""REST API (FastAPI). Зберігання поки в пам'яті; далі PostgreSQL."""
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .graph import KnowledgeGraph
from .knowledge import update_mastery
from .recommender import recommend
from .activity import ActivityStats, dropout_risk

graph = KnowledgeGraph.from_json(Path(__file__).parent.parent / "data" / "sample_course.json")
app = FastAPI(title="Платформа персоналізованого навчання")

# user_id -> {"mastery": {topic: p}, "last": {topic: datetime}, "fails": int}
DB: dict = {}


class Answer(BaseModel):
    user_id: str
    topic_id: str
    correct: bool


def _user(uid):
    return DB.setdefault(uid, {"mastery": {}, "last": {}, "fails": 0})


@app.post("/answers")
def submit_answer(a: Answer):
    if a.topic_id not in graph.topics:
        raise HTTPException(404, "Невідома тема")
    u = _user(a.user_id)
    u["mastery"][a.topic_id] = update_mastery(u["mastery"].get(a.topic_id, 0.2), a.correct)
    u["last"][a.topic_id] = datetime.now(timezone.utc)
    u["fails"] = 0 if a.correct else u["fails"] + 1
    return {"topic_id": a.topic_id, "mastery": round(u["mastery"][a.topic_id], 3)}


@app.get("/profile/{user_id}")
def profile(user_id: str):
    u = _user(user_id)
    return {"mastery": {t: round(p, 3) for t, p in u["mastery"].items()},
            "dropout_risk": dropout_risk(ActivityStats(fail_streak=u["fails"]))}


@app.get("/recommendation/{user_id}")
def recommendation(user_id: str):
    u = _user(user_id)
    now = datetime.now(timezone.utc)
    days = {t: (now - d).total_seconds() / 86400 for t, d in u["last"].items()}
    r = recommend(graph, u["mastery"], days)
    return r.__dict__ if r else {"message": "Курс завершено"}
