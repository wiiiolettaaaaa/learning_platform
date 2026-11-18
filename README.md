# Платформа персоналізованого навчання (стартовий каркас)

Реалізовано ядро: BKT-модель знань, граф знань, рекомендації з повторенням, індикатор ризику відсіву, REST API.

## Запуск на macOS
```bash
cd learning-platform
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m unittest discover -s tests -t . -v   # тести ядра
uvicorn app.main:app --reload                   # API: http://127.0.0.1:8000/docs
```

## Структура
- app/knowledge.py – BKT
- app/graph.py – граф знань
- app/recommender.py – рекомендації
- app/activity.py – аналіз активності
- app/main.py – API
- data/sample_course.json – приклад курсу

## Наступні кроки
PostgreSQL замість пам'яті, автентифікація, фронтенд, ML-модель ризику, кабінет викладача.
