"""REST API (FastAPI). Зберігання поки в пам'яті; далі PostgreSQL."""
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .graph import KnowledgeGraph
from .knowledge import update_mastery
from .recommender import recommend
from .activity import build_stats
from .risk_model import mean_mastery, risk
from .teacher import student_summary, topic_summary

BASE = Path(__file__).parent.parent
graph = KnowledgeGraph.from_json(BASE / "data" / "sample_course.json")
QUESTIONS: dict = json.loads((BASE / "data" / "questions.json").read_text(encoding="utf-8"))

app = FastAPI(title="Платформа персоналізованого навчання")

# Дозволяємо запити з фронтенду (Vite dev-сервер)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# user_id -> {"mastery": {topic: p}, "last": {topic: datetime}, "fails": int, "attempts": [datetime],
#                "results": {topic: {"correct": n, "total": n}}}
DB: dict = {}


class Answer(BaseModel):
    user_id: str
    topic_id: str
    correct: bool


class AnswerCheck(BaseModel):
    user_id: str
    topic_id: str
    question_id: str
    choice: int


def _user(uid):
    return DB.setdefault(uid, {"mastery": {}, "last": {}, "fails": 0, "attempts": [], "results": {}})


def _apply(uid: str, topic_id: str, correct: bool) -> float:
    """Оновлює оцінку знань користувача після відповіді."""
    if topic_id not in graph.topics:
        raise HTTPException(404, "Невідома тема")
    u = _user(uid)
    u["mastery"][topic_id] = update_mastery(u["mastery"].get(topic_id, 0.2), correct)
    now = datetime.now(timezone.utc)
    u["last"][topic_id] = now
    u["attempts"].append(now)
    r = u["results"].setdefault(topic_id, {"correct": 0, "total": 0})
    r["total"] += 1
    r["correct"] += int(correct)
    u["fails"] = 0 if correct else u["fails"] + 1
    return round(u["mastery"][topic_id], 3)


@app.get("/topics")
def topics():
    return [{"id": t, "title": graph.title(t), "prerequisites": list(graph.prerequisites(t))}
            for t in graph.topics]


@app.get("/topics/{topic_id}/question")
def question(topic_id: str, exclude: Optional[str] = None):
    """Випадкове питання теми (без правильної відповіді)."""
    if topic_id not in graph.topics:
        raise HTTPException(404, "Невідома тема")
    pool = QUESTIONS.get(topic_id, [])
    if not pool:
        raise HTTPException(404, "Для теми ще немає питань")
    options = [q for q in pool if q["id"] != exclude] or pool
    q = random.choice(options)
    return {"id": q["id"], "topic_id": topic_id, "text": q["text"], "options": q["options"]}


@app.post("/answers/check")
def check_answer(a: AnswerCheck):
    """Перевіряє відповідь на питання і оновлює модель знань."""
    q = next((x for x in QUESTIONS.get(a.topic_id, []) if x["id"] == a.question_id), None)
    if q is None:
        raise HTTPException(404, "Невідоме питання")
    correct = a.choice == q["answer"]
    mastery = _apply(a.user_id, a.topic_id, correct)
    return {"correct": correct, "correct_choice": q["answer"], "mastery": mastery}


@app.post("/answers")
def submit_answer(a: Answer):
    return {"topic_id": a.topic_id, "mastery": _apply(a.user_id, a.topic_id, a.correct)}


@app.get("/profile/{user_id}")
def profile(user_id: str):
    u = _user(user_id)
    return {"mastery": {t: round(p, 3) for t, p in u["mastery"].items()},
            "dropout_risk": risk(build_stats(u["attempts"], u["fails"], datetime.now(timezone.utc)),
                                 mean_mastery(u["mastery"]))}


@app.get("/recommendation/{user_id}")
def recommendation(user_id: str):
    u = _user(user_id)
    now = datetime.now(timezone.utc)
    days = {t: (now - d).total_seconds() / 86400 for t, d in u["last"].items()}
    r = recommend(graph, u["mastery"], days)
    return r.__dict__ if r else {"message": "Курс завершено"}


@app.get("/teacher/students")
def teacher_students():
    """Усі студенти: засвоєння, активність, ризик відсіву (найризикованіші першими)."""
    now = datetime.now(timezone.utc)
    rows = [student_summary(uid, u, now) for uid, u in DB.items()]
    return sorted(rows, key=lambda r: -r["dropout_risk"])


@app.get("/teacher/topics")
def teacher_topics():
    """Зведення за темами: кількість спроб, частка правильних, середнє засвоєння."""
    return [{**row, "title": graph.title(row["topic_id"])}
            for row in topic_summary(DB, list(graph.topics))]
