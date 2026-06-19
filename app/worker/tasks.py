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

        # Remove exact duplicate rows
        df = df.drop_duplicates()

        # Fill missing categories
        df["category"] = df["category"].fillna("Uncategorised")

        # Normalize status
        df["status"] = df["status"].astype(str).str.upper()

        # Normalize currency
        df["currency"] = df["currency"].astype(str).str.upper()

        # Clean amount column
        df["amount"] = pd.to_numeric(
            df["amount"]
            .astype(str)
            .str.replace("$", "", regex=False),
            errors="coerce"
        ).fillna(0)

        # Normalize dates to ISO format
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce",
            dayfirst=True
        ).dt.strftime("%Y-%m-%d")

        # -----------------------------
        # Anomaly Detection
        # -----------------------------

        # Account median amount
        account_median = df.groupby("account_id")["amount"].transform("median")

        # Rule 1: amount > 3x account median
        df["is_anomaly"] = df["amount"] > (3 * account_median)

        df["anomaly_reason"] = None

        df.loc[
            df["is_anomaly"],
            "anomaly_reason"
        ] = "Amount exceeds 3x account median"

        # Rule 2: USD with domestic merchants
        domestic_merchants = ["Swiggy", "Ola", "IRCTC"]

        currency_anomaly = (
            (df["currency"] == "USD")
            &
            (df["merchant"].isin(domestic_merchants))
        )

        df.loc[currency_anomaly, "is_anomaly"] = True

        df.loc[
            currency_anomaly,
            "anomaly_reason"
        ] = "USD transaction with domestic merchant"

        # -----------------------------
        # Store transactions
        # -----------------------------

        for _, row in df.iterrows():

            transaction = Transaction(
                job_id=job.id,
                txn_id=str(row.get("txn_id")),
                date=str(row.get("date")),
                merchant=str(row.get("merchant")),
                amount=float(row.get("amount")),
                currency=str(row.get("currency")),
                status=str(row.get("status")),
                category=str(row.get("category")),
                account_id=str(row.get("account_id")),
                is_anomaly=bool(row["is_anomaly"]),
                anomaly_reason=row["anomaly_reason"]
            )

            db.add(transaction)

        # update counts
        job.row_count_raw = total_rows
        job.row_count_clean = len(df)

        # mark completed
        job.status = "completed"

        db.commit()

    except Exception as e:

        job.status = "failed"
        job.error_message = str(e)

        db.commit()

    finally:
        db.close()