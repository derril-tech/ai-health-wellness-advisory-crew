from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Celery configuration
celery_app = Celery(
    "health_crew_workers",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "workers.tasks.intake_normalizer",
        "workers.tasks.tdee_macro_engine", 
        "workers.tasks.mealplanner",
        "workers.tasks.workout_periodization",
        "workers.tasks.habit_engine",
        "workers.tasks.progress_analyzer",
        "workers.tasks.device_ingestor",
        "workers.tasks.grocery_builder",
        "workers.tasks.reporter"
    ]
)

# Celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

if __name__ == "__main__":
    celery_app.start()
