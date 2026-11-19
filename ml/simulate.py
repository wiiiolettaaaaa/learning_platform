"""Імітаційна модель студентів для генерації навчальної вибірки.

УВАГА: дані синтетичні. Модель вчиться на припущеннях цієї симуляції, а не на
реальних студентах, тому метрики якості демонструють роботу конвеєра, а не
точність на реальних даних. Після збору справжніх логів тренувальну вибірку
слід замінити (формат ознак лишається тим самим).
"""
import random

DAYS = 60          # скільки днів симулюємо кожного студента
HORIZON = 14       # мітка: чи не буде жодної спроби в наступні HORIZON днів
FEATURES = ["days_inactive", "fail_streak", "attempts_last_week", "avg_mastery"]


def simulate_student(rng: random.Random):
    """Повертає по днях: кількість спроб, серію помилок і середнє засвоєння."""
    engagement = rng.uniform(0.3, 1.0)   # залученість (прихована змінна)
    skill = rng.uniform(0.25, 0.85)      # базова ймовірність правильної відповіді
    mastery, streak = 0.2, 0
    attempts, streaks, masteries = [], [], []
    for _ in range(DAYS):
        n = 0
        if rng.random() < min(0.95, engagement):
            n = max(1, round(rng.gauss(4 * engagement + 1, 1.5)))
            for _ in range(n):
                p_ok = min(0.97, max(0.05, skill + 0.4 * (mastery - 0.2)))
                if rng.random() < p_ok:
                    mastery += 0.08 * (1 - mastery)
                    streak = 0
                    engagement = min(1.0, engagement + 0.01)
                else:
                    mastery = max(0.0, mastery - 0.02)
                    streak += 1
                    if streak >= 3:          # серія невдач гасить мотивацію
                        engagement -= 0.06
        else:
            engagement -= 0.04               # пропущений день теж знижує залученість
        engagement += rng.gauss(0, 0.02)
        if rng.random() < 0.008:             # раптовий відсів (непередбачуваний)
            engagement = 0.0
        if engagement < 0.08:
            engagement = 0.0
        attempts.append(n)
        streaks.append(streak)
        masteries.append(mastery)
    return attempts, streaks, masteries


def generate(n_students: int = 4000, seed: int = 42):
    """Повертає (X, y, groups): ознаки, мітки відсіву й номери студентів."""
    rng = random.Random(seed)
    X, y, groups = [], [], []
    for sid in range(n_students):
        attempts, streaks, masteries = simulate_student(rng)
        for t in range(7, DAYS - HORIZON, 5):
            if sum(attempts[: t + 1]) == 0:
                continue
            last = max(d for d in range(t + 1) if attempts[d] > 0)
            X.append([
                t - last,
                streaks[t],
                sum(attempts[t - 6: t + 1]),
                masteries[t],
            ])
            y.append(1 if sum(attempts[t + 1: t + 1 + HORIZON]) == 0 else 0)
            groups.append(sid)
    return X, y, groups
