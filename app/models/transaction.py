from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey
)

from app.db.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    txn_id = Column(String)
    date = Column(String)

    merchant = Column(String)

    amount = Column(Float)

    currency = Column(String)

    status = Column(String)

    category = Column(String)

    account_id = Column(String)

    is_anomaly = Column(
        Boolean,
        default=False
    )

    anomaly_reason = Column(
        String,
        nullable=True
    )