import os

from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.dependencies import get_db
from app.models.job import Job
from app.models.transaction import Transaction
from app.worker.tasks import process_csv

router = APIRouter()


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    job = Job(
        status="pending",
        file_name=file.filename
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    process_csv.delay(job.id)

    return {
        "job_id": job.id,
        "status": job.status
    }


@router.get("/")
def list_jobs(
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).all()

    return [
        {
            "job_id": job.id,
            "file_name": job.file_name,
            "status": job.status,
            "row_count_raw": job.row_count_raw,
            "row_count_clean": job.row_count_clean,
            "created_at": job.created_at,
            "error_message": job.error_message
        }
        for job in jobs
    ]


@router.get("/{job_id}/status")
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job_id": job.id,
        "status": job.status,
        "row_count_raw": job.row_count_raw,
        "row_count_clean": job.row_count_clean,
        "error_message": job.error_message
    }


@router.get("/{job_id}/results")
def get_job_results(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.job_id == job_id)
        .all()
    )

    anomalies = [
        {
            "txn_id": t.txn_id,
            "merchant": t.merchant,
            "amount": t.amount,
            "currency": t.currency,
            "reason": t.anomaly_reason
        }
        for t in transactions
        if t.is_anomaly
    ]

    category_breakdown = {}

    for t in transactions:

        category = t.category

        if not category:
            category = "Uncategorised"

        category_breakdown[category] = (
            category_breakdown.get(category, 0)
            + t.amount
        )

    transaction_data = [
        {
            "txn_id": t.txn_id,
            "date": t.date,
            "merchant": t.merchant,
            "amount": t.amount,
            "currency": t.currency,
            "status": t.status,
            "category": t.category,
            "account_id": t.account_id,
            "is_anomaly": t.is_anomaly,
            "anomaly_reason": t.anomaly_reason
        }
        for t in transactions
    ]

    return {
        "job_id": job.id,
        "status": job.status,
        "row_count_raw": job.row_count_raw,
        "row_count_clean": job.row_count_clean,
        "total_transactions": len(transactions),
        "anomaly_count": len(anomalies),
        "category_breakdown": category_breakdown,
        "anomalies": anomalies,
        "transactions": transaction_data
    }