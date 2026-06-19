import os

from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.dependencies import get_db
from app.models.job import Job

router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...),
                      db: Session = Depends(get_db)):

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

    return {
        "job_id": job.id,
        "status": job.status
    }