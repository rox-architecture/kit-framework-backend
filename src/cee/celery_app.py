"""Celery application shared by the API coordinator and workers."""

from celery import Celery  # type: ignore[import-untyped]

from cee.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "cee",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["cee.tasks"],
)
celery_app.conf.update(
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    task_track_started=True,
    task_acks_late=False,
    task_reject_on_worker_lost=False,
    worker_prefetch_multiplier=1,
)
