from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db
import schemas
import endpoints
from db.database import Base, engine
import db.database as appdb
from endpoints.user import router as user_router

# Init JWT token data 
SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create database tables
Base.metadata.create_all(bind=engine)

# Init FastAPI app
security = HTTPBasic()
app = FastAPI()
app.include_router(user_router)

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Public endpoint"}
