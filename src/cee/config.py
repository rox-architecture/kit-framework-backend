"""Environment-backed application settings."""

import os
from pathlib import Path

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://admin:admin@localhost:5432/workflowdb",
)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
ARTIFACT_ROOT = Path(os.getenv("ARTIFACT_ROOT", ".cee-artifacts"))
SCHEDULER_POLL_INTERVAL = float(os.getenv("SCHEDULER_POLL_INTERVAL", "0.5"))
ARTIFACT_RETENTION = int(os.getenv("ARTIFACT_RETENTION", "3600"))
RETAIN_FAILED_ARTIFACTS = os.getenv("RETAIN_FAILED_ARTIFACTS", "true").lower() in {
    "1",
    "true",
    "yes",
}
