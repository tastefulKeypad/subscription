from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import os, sys
from pwdlib import PasswordHash
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import db
import schemas
import endpoints
from db.database import Base, engine
import db.database as appdb
import db.models as models
from endpoints.user import router as user_router
from endpoints.auth import router as token_router
from endpoints.product import router as product_router
from endpoints.promo import router as promo_router
from endpoints.sub import router as sub_router
from endpoints.transaction import router as transaction_router
from endpoints.refund import router as refund_router

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
app.include_router(token_router)
app.include_router(product_router)
app.include_router(promo_router)
app.include_router(sub_router)
app.include_router(transaction_router)
app.include_router(refund_router)

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Public endpoint"}

@app.post("/populate_db")
def populate_db(
    db: Session = Depends(appdb.get_db)
):
    """
    Populates db with admin, users and products for debug 

    To authorize as admin:

    email: admin@example.com
    
    pass:  admin

    To authorize as normal user:

    email: user1@example.com 

    pass:  user

    """
    password_hash = PasswordHash.recommended()
    user_count = db.query(models.User).count()
    if user_count == 0:
        users = [
            models.User(
                name="Admin",
                email="admin@example.com",
                password=password_hash.hash("admin"),
                isAdmin=True
            ),
            models.User(
                name="User 1",
                email="user1@example.com",
                password=password_hash.hash("user"),
                isAdmin=False

            ),
            models.User(
                name="User 2",
                email="user2@example.com",
                password=password_hash.hash("user"),
                isAdmin=False
            )
        ]
        products = [
            models.Product(
                name="Product Basic",
                price=100
            ),
            models.Product(
                name="Product Advanced",
                price=500
            ),
            models.Product(
                name="Product Premium",
                price=1000
            )
        ]
        db.add_all(users)
        db.add_all(products)
        db.commit()
        return {"message": "Successfully populated db with basic objects"}
    
    return {"message": "Failed to populate db! Try to delete 'app.db' and try again"}
    
