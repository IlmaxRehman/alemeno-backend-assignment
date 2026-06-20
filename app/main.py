from fastapi import FastAPI

from app.api.jobs import router as jobs_router

from app.db.database import Base, engine
from app.models.job import Job
from app.models.transaction import Transaction

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Alemeno Backend Assignment API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(
    jobs_router,
    prefix="/jobs",
    tags=["Jobs"]
)