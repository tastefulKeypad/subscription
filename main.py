from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from contextlib import asynccontextmanager
from typing import Annotated, List
import asyncio
import schedule 
import time
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports from local files
import db
import schemas
import endpoints
from db.database import Base, engine, SessionLocal
import db.database as appdb
import db.models as models
import schemas.user, schemas.transaction, schemas.sub
from endpoints import fakePayment
from endpoints.user import router as user_router
from endpoints.auth import router as token_router
from endpoints.product import router as product_router
from endpoints.promo import router as promo_router
from endpoints.sub import router as sub_router
from endpoints.transaction import router as transaction_router
from endpoints.refund import router as refund_router

# How often scheduled task runs in seconds
SCHEDULED_TASK_TIME = 10

################# Init FastAPI app #################
# Create database tables if they dont exist yet
Base.metadata.create_all(bind=engine)

security = HTTPBasic()
app = FastAPI()
app.include_router(user_router)
app.include_router(token_router)
app.include_router(product_router)
app.include_router(promo_router)
app.include_router(sub_router)
app.include_router(transaction_router)
app.include_router(refund_router)

################# Scheduled tasks #################
async def process_pending_transactions():
    db = appdb.SessionLocal()
    db_transactions = db.query(models.Transaction).filter(
        models.Transaction.userId == 0
    ).all()

    # Try to process every pending transaction
    for transaction in db_transactions:
        price_final = transaction.bankChange
        if transaction.action == "Refund request":
            price_final = transaction.toRefund
        payment_service_response = fakePayment.fake_payment_method(price_final)

        # Update db only on successfull payment
        if payment_service_response.status == "Success":
            new_transaction = models.Transaction(
                userId = transaction.hiddenUserId,
                productId = transaction.productId,
                action = transaction.action,
                dateTime = datetime.now(timezone.utc),
                status = "Success",
            )
            
            if transaction.action == "Refund request":
                transaction.toRefund = payment_service_response.bankChange
            else:
                transaction.bankChange = payment_service_response.bankChange

            db.delete(transaction)
            db.add(new_transaction)
    db.commit()
    db.close()

# Automatically cancel all subscriptions that expired for longer than 3 days
# async def cancel_expired_subscriptions():

# Check expired subscriptions and try to automatically refresh them
'''
async def add_new_pending_transactions():
    db = appdb.SessionLocal()
    db_transactions = db.query(models.Sub).filter(
        models.Transaction.userId == 0
    ).all()

    # Try to process every pending transaction
    for transaction in db_transactions:
        price_final = transaction.bankChange
        if transaction.action == "Refund request":
            price_final = transaction.toRefund
        payment_service_response = fakePayment.fake_payment_method(price_final)

        # Update db only on successfull payment
        if payment_service_response.status == "Success":
            new_transaction = models.Transaction(
                userId = transaction.hiddenUserId,
                productId = transaction.productId,
                action = transaction.action,
                dateTime = datetime.now(timezone.utc),
                status = "Success",
            )
            
            if transaction.action == "Refund request":
                transaction.toRefund = payment_service_response.bankChange
            else:
                transaction.bankChange = payment_service_response.bankChange

            db.delete(transaction)
            db.add(new_transaction)
    db.commit()
    db.close()
'''

async def periodic_task():
    while True:
        print("Processing pending payments")
        #await add_new_pending_transactions()
        await process_pending_transactions()
        #await cancel_expired_subscriptions()
        await asyncio.sleep(SCHEDULED_TASK_TIME)

@app.on_event("startup")
async def app_startup():
    # Start the periodic task
    asyncio.create_task(periodic_task())


################# Endpoints #################
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
    
