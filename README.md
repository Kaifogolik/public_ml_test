# Public ML Test – EDA, Training, API, Airflow

Проект демонстрирует пайплайн из ноутбука к продакшен-стеку по схеме: Jupyter → скрипты → Docker/API → Git → Server, плюс ежедневный Airflow DAG и хранение модели в S3.

## Содержимое репозитория
- `src/EDA.ipynb` – исследование данных и эксперименты.
- `src/pipeline/train.py` – обучение модели (HistGradientBoosting), сохранение артефакта и опциональная загрузка в S3.
- `src/api/app.py` – FastAPI-сервис предсказаний, загрузка модели при старте с диска или из S3.
- `src/utils/config.py`, `src/utils/s3_utils.py` – конфигурация (YAML + ENV) и утилиты S3.
- `airflow/dags/daily_train_upload.py` – DAG Airflow: ежедневное обучение и публикация модели.
- `Dockerfile` – контейнер FastAPI-сервиса.
- `requirements.txt` – зависимости проекта.
- `configs/config.yaml` – человекочитаемые настройки (ENV их перекрывают).

Данные не хранятся в репозитории. Путь к данным задаётся `paths.data` или `DATA_PATH`.

## Быстрый старт
1) Установка зависимостей
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

2) Настройки: YAML + ENV
- Отредактируйте `configs/config.yaml` (или создайте `configs/local.yaml` и укажите `CONFIG_PATH=configs/local.yaml`).
- ENV-переменные перекрывают YAML: `AWS_*`, `S3_BUCKET`, `MODEL_*`, `DATA_PATH`, `TARGET_COLUMN`, `UPLOAD_TO_S3`.

3) Обучение модели
```bash
python -m src.pipeline.train
```
- Сохранит `models/model.joblib` (модель + список фич).
- При `UPLOAD_TO_S3=true` загрузит в `s3://$S3_BUCKET/$MODEL_S3_KEY`.

4) Запуск API (uvicorn)
```bash
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```
Эндпоинты: `GET /health`, `POST /predict`.

5) Docker
```bash
docker build -t ml-api .
docker run --rm -p 8000:8000 \
  -e CONFIG_PATH="configs/config.yaml" \
  -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION \
  -e S3_BUCKET -e MODEL_S3_KEY -e MODEL_LOCAL_PATH \
  ml-api
```

6) Airflow
- Папка DAGs: `airflow/dags`. DAG `daily_train_upload` (ежедневно 02:00).
- Установите `PYTHONPATH=$(pwd)` для корректных импортов.

## Примечания
- В артефакте сохраняется список фич; API выравнивает вход под него.
- Исключено из Git: `venv/`, `src/input/`, `__pycache__/`, `.ipynb_checkpoints/`, `airflow/logs/`, `*.tfevents`, `src/catboost_info/`, а также `configs/local.yaml`.

## Идеи на будущее
- MLflow-трекинг и реестр моделей.
- CI/CD (GitHub Actions) и автосборка Docker.
- Подбор гиперпараметров (Grid/Optuna).
