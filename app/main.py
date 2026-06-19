from fastapi import FastAPI

from app.api.jobs import router as jobs_router

app = FastAPI()


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