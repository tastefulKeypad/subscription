# FastAPI dependencies for dependency injection
from db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
