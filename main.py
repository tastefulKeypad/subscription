from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db
import schemas
import endpoints
import dependencies
from db.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Init FastAPI app
app = FastAPI()
