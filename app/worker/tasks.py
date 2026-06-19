from app.worker.celery_app import celery_app

from app.db.database import SessionLocal
from app.models.job import Job
from app.models.transaction import Transaction

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

        for _, row in df.iterrows():

              amount_value = row.get("amount")

              if pd.isna(amount_value):
                  amount_value = 0
              else:
                  amount_value = str(amount_value).replace("$", "").strip()
              transaction = Transaction(
                 job_id=job.id,
                 txn_id=str(row.get("txn_id")),
                 date=str(row.get("date")),
                 merchant=str(row.get("merchant")),
                 amount=float(amount_value),
                 currency=str(row.get("currency")),
                 status=str(row.get("status")),
                 category=str(row.get("category")),
                 account_id=str(row.get("account_id")),
                 is_anomaly=False
           )
        
              db.add(transaction)

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