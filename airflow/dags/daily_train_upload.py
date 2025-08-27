from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.pipeline.train import train  # noqa: E402


def train_task():
    train()


def _default_args():
    return {
        "owner": "ml",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }


dag = DAG(
    dag_id="daily_train_upload",
    default_args=_default_args(),
    schedule_interval="0 2 * * *",  # каждый день в 02:00
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["ml"],
)

with dag:
    train_op = PythonOperator(
        task_id="train_and_upload",
        python_callable=train_task,
    )

    train_op
