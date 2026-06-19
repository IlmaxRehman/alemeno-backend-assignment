from pydantic import BaseModel

class JobResponse(BaseModel):
    job_id : int
    status : str