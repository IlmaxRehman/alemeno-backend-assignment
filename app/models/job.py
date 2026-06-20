from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="pending"
    )

    row_count_raw = Column(
        Integer,
        nullable=True
    )

    row_count_clean = Column(
        Integer,
        nullable=True
    )

    error_message = Column(
        String,
        nullable=True
    )

    summary = Column(
        String,
        nullable=True
    )

    risk_level = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )