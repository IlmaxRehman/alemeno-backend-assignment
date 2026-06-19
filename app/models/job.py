from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key = True, index = True)

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    file_name = Column(
        String,
        nullable=False
    )

    create_at = Column(
        DateTime(timezone=True),
        server_default=func.now() 
    )