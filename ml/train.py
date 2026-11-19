"""Навчання моделі ризику відсіву (логістична регресія) на синтетичній вибірці.

Запуск (з кореня проєкту):  python -m ml.train
Потрібні scikit-learn і numpy: pip install -r requirements-ml.txt
Результат: models/dropout_logreg.json (ваги моделі) та models/metrics.json.
"""
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler

from app.activity import ActivityStats, dropout_risk
from ml.simulate import FEATURES, HORIZON, generate

OUT = Path(__file__).parent.parent / "models"


def main(n_students: int = 4000, seed: int = 42):
    X, y, groups = map(np.array, generate(n_students, seed))

    # Ділимо за студентами, щоб точки одного студента не потрапили і в train, і в test
    split = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed)
    train, test = next(split.split(X, y, groups))
    scaler = StandardScaler().fit(X[train])

    logreg = LogisticRegression(max_iter=1000).fit(scaler.transform(X[train]), y[train])
    gboost = GradientBoostingClassifier(random_state=seed).fit(X[train], y[train])

    p_lr = logreg.predict_proba(scaler.transform(X[test]))[:, 1]
    p_gb = gboost.predict_proba(X[test])[:, 1]
    p_rules = np.array([dropout_risk(ActivityStats(int(r[0]), int(r[1]), int(r[2]))) for r in X[test]])
    pred = (p_lr >= 0.5).astype(int)

    # Складніший випадок «раннього попередження»: студент ще активний (<= 2 днів без спроб)
    active = X[test][:, 0] <= 2
    yt = y[test][active]
    early = {
        "early_rows": int(active.sum()),
        "early_positive_rate": round(float(yt.mean()), 3),
        "early_auc_rules": round(roc_auc_score(yt, p_rules[active]), 3),
        "early_auc_logreg": round(roc_auc_score(yt, p_lr[active]), 3),
        "early_auc_gradient_boosting": round(roc_auc_score(yt, p_gb[active]), 3),
    }

    metrics = {
        "data": "synthetic (ml/simulate.py)",
        "horizon_days": HORIZON,
        "students": n_students,
        "rows": int(len(y)),
        "test_rows": int(len(test)),
        "positive_rate": round(float(y.mean()), 3),
        "auc_rules": round(roc_auc_score(y[test], p_rules), 3),
        "auc_logreg": round(roc_auc_score(y[test], p_lr), 3),
        "auc_gradient_boosting": round(roc_auc_score(y[test], p_gb), 3),
        "logreg_accuracy": round(accuracy_score(y[test], pred), 3),
        "logreg_precision": round(precision_score(y[test], pred), 3),
        "logreg_recall": round(recall_score(y[test], pred), 3),
        **early,
        "logreg_coefficients": {f: round(float(c), 3) for f, c in zip(FEATURES, logreg.coef_[0])},
    }

    model = {
        "features": FEATURES,
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "coef": logreg.coef_[0].tolist(),
        "intercept": float(logreg.intercept_[0]),
        "note": "Навчено на синтетичних даних (ml/simulate.py)",
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "dropout_logreg.json").write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
