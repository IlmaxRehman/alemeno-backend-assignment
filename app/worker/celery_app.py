from celery import Celery

celery_app = Celery(
    "alemeno",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.worker.tasks"]
)