from app.db.database import Base, engine

from app.models import Job

Base.metadata.create_all(bind=engine)

print("Tables created successfully.")