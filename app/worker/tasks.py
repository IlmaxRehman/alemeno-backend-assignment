from app.worker.celery_app import celery_app

from app.db.database import SessionLocal
from app.models.job import Job
from app.models.transaction import Transaction

from app.services.gemini_service import (
    classify_missing_categories,
    generate_summary
)

import pandas as pd


@celery_app.task
def process_csv(job_id: int):

    db = SessionLocal()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            return

        job.status = "processing"
        db.commit()

        file_path = f"uploads/{job.file_name}"

        df = pd.read_csv(file_path)

        total_rows = len(df)

        # Data Cleaning

        df = df.drop_duplicates()

        missing_category_mask = df["category"].isna()

        df["category"] = df["category"].fillna("Uncategorised")

        df["status"] = df["status"].astype(str).str.upper()

        df["currency"] = df["currency"].astype(str).str.upper()

        df["amount"] = pd.to_numeric(
            df["amount"]
            .astype(str)
            .str.replace("$", "", regex=False),
            errors="coerce"
        ).fillna(0)

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce",
            dayfirst=True
        ).dt.strftime("%Y-%m-%d")

        # Gemini Category Classification

        missing_rows = df[missing_category_mask]

        if len(missing_rows) > 0:

            payload = []

            for _, row in missing_rows.iterrows():

                payload.append(
                    {
                        "merchant": str(row["merchant"]),
                        "notes": str(row.get("notes", ""))
                    }
                )

            llm_result = classify_missing_categories(payload)

            if llm_result:

                for index, category_result in zip(
                    missing_rows.index,
                    llm_result
                ):
                    df.loc[index, "category"] = category_result.get(
                        "category",
                        "Other"
                    )

            else:

                # Fallback Classification

                for index, row in missing_rows.iterrows():

                    merchant = str(row["merchant"]).lower()

                    if "swiggy" in merchant:
                        df.loc[index, "category"] = "Food"

                    elif "zomato" in merchant:
                        df.loc[index, "category"] = "Food"

                    elif "ola" in merchant:
                        df.loc[index, "category"] = "Transport"

                    elif "uber" in merchant:
                        df.loc[index, "category"] = "Transport"

                    elif "irctc" in merchant:
                        df.loc[index, "category"] = "Travel"

                    elif "amazon" in merchant:
                        df.loc[index, "category"] = "Shopping"

                    elif "flipkart" in merchant:
                        df.loc[index, "category"] = "Shopping"

                    else:
                        df.loc[index, "category"] = "Other"

        # Anomaly Detection

        account_median = (
            df.groupby("account_id")["amount"]
            .transform("median")
        )

        df["is_anomaly"] = (
            df["amount"] > (3 * account_median)
        )

        df["anomaly_reason"] = None

        df.loc[
            df["is_anomaly"],
            "anomaly_reason"
        ] = "Amount exceeds 3x account median"

        domestic_merchants = [
            "Swiggy",
            "Ola",
            "IRCTC"
        ]

        currency_anomaly = (
            (df["currency"] == "USD")
            &
            (df["merchant"].isin(domestic_merchants))
        )

        df.loc[
            currency_anomaly,
            "is_anomaly"
        ] = True

        df.loc[
            currency_anomaly,
            "anomaly_reason"
        ] = "USD transaction with domestic merchant"

        # Gemini Narrative Summary

        merchant_totals = (
            df.groupby("merchant")["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(3)
        )

        summary_input = {
            "total_spend_inr": float(
                df[df["currency"] == "INR"]["amount"].sum()
            ),
            "total_spend_usd": float(
                df[df["currency"] == "USD"]["amount"].sum()
            ),
            "top_merchants": merchant_totals.index.tolist(),
            "anomaly_count": int(
                df["is_anomaly"].sum()
            )
        }

        summary_result = generate_summary(
            summary_input
        )

        if summary_result:

            job.summary = summary_result.get(
                "narrative"
            )

            job.risk_level = summary_result.get(
                "risk_level"
            )

        else:

            anomaly_count = int(
                df["is_anomaly"].sum()
            )

            job.summary = (
                f"Processed {len(df)} transactions. "
                f"Detected {anomaly_count} anomalies. "
                f"Fallback summary generated because "
                f"LLM was unavailable."
            )

            if anomaly_count >= 5:
                job.risk_level = "high"
            elif anomaly_count >= 2:
                job.risk_level = "medium"
            else:
                job.risk_level = "low"

        # Store Transactions

        for _, row in df.iterrows():

            transaction = Transaction(
                job_id=job.id,
                txn_id=None if pd.isna(row.get("txn_id")) else str(row.get("txn_id")),
                date=None if pd.isna(row.get("date")) else str(row.get("date")),
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

        job.row_count_raw = total_rows
        job.row_count_clean = len(df)

        job.status = "completed"

        db.commit()

    except Exception as e:

        job.status = "failed"
        job.error_message = str(e)

        db.commit()

    finally:
        db.close()