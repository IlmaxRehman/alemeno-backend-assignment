from app.worker.celery_app import celery_app

from app.db.database import SessionLocal
from app.models.job import Job

import pandas as pd


@celery_app.task
def process_csv(job_id: int):

    db = SessionLocal()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            return

        # mark processing
        job.status = "processing"
        db.commit()

        # read uploaded csv
        file_path = f"uploads/{job.file_name}"

        df = pd.read_csv(file_path)

        total_rows = len(df)

        # update counts
        job.row_count_raw = total_rows
        job.row_count_clean = total_rows

        # mark completed
        job.status = "completed"

        db.commit()

    except Exception as e:

        job.status = "failed"
        job.error_message = str(e)

        db.commit()

    finally:
        db.close()