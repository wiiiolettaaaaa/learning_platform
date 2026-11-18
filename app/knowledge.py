"""Модель знань користувача: байєсівське відстеження знань (BKT)."""
from dataclasses import dataclass


@dataclass
class BKTParams:
    p_init: float = 0.2   # початкова ймовірність знання теми
    p_learn: float = 0.15  # ймовірність засвоїти тему після спроби
    p_guess: float = 0.2   # вгадав, не знаючи
    p_slip: float = 0.1    # помилився, знаючи


def update_mastery(p_known: float, correct: bool, prm: BKTParams = BKTParams()) -> float:
    """Повертає нову ймовірність того, що користувач знає тему."""
    if correct:
        num = p_known * (1 - prm.p_slip)
        den = num + (1 - p_known) * prm.p_guess
    else:
        num = p_known * prm.p_slip
        den = num + (1 - p_known) * (1 - prm.p_guess)
    posterior = num / den
    return posterior + (1 - posterior) * prm.p_learn
