from datetime import datetime, timedelta, timezone
from typing import Annotated, List
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import update
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Imports from local files
from endpoints import fakePayment
import sending_messages.emailSend as emailService
import db.database as appdb
import db.models as models
import schemas.user, schemas.token, schemas.product, schemas.promo, schemas.sub, schemas.transaction
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/subs", tags=["subs"])

# Endpoints
@router.post("/subscribe_to_product", response_model=schemas.sub.SubResponse)
def subscribe_to_product(
    product_id: int,
    token_user: Annotated[models.User, Depends(get_token_user)],
    promo_name: str | None = None,
    db: Session = Depends(appdb.get_db)
):
    """
    Try to subscribe to a product

    Must be normal user to use this endpoint
    """
    # Check if user is a normal user
    if token_user.isAdmin:
        raise_exception_user()

    # Check if product id exists
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    if not db_product:
        raise_exception_no_product()

    # Check if user is already subscribed to this product
    db_subscription = db.query(models.Sub).filter(
        models.Sub.userId == token_user.id,
        models.Sub.productId == product_id
    ).first()
    if db_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already subscribed to this product"
        )

    # Check if promo with specified name exists and it's valid for specified product id
    if promo_name:
        db_promo = db.query(models.Promo).filter(
            models.Promo.name == promo_name
        ).first()
        if not db_promo:
            raise_exception_no_promo()
        if db_promo.productId != product_id:
            raise_exception_no_promo()


    # Query payment provider
    price_final = db_product.price 
    if promo_name:
        price_final *= 1-db_promo.discount/100

    payment_service_response = fakePayment.fake_payment_method(price_final)

    # Add transaction to db and handle payment service errors
    dateTimeNow = datetime.now(timezone.utc)
    new_transaction = models.Transaction(
        userId = token_user.id,
        productId = product_id,
        promoName = promo_name,
        action = "New subscription",
        dateTime = dateTimeNow,
        status = payment_service_response.status,
        bankChange = payment_service_response.bankChange
    )

    db.add(new_transaction)
    db.commit()

    if payment_service_response.status == "Timeout":
        raise_exception_timeout()
    if payment_service_response.status == "Insufficient funds":
        raise_exception_insufficient_funds()

    # Add subscription to db
    new_sub = models.Sub(
        userId = token_user.id,
        productId = product_id,
        price = price_final,
        status = "Active",
        dateTime = dateTimeNow + timedelta(days=30)
    )
    emailService.new_subscription(token_user.email, db_product.name, price_final)

    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub


@router.get("/get_subscriptions", response_model=List[schemas.sub.SubResponse])
def get_subscriptions(
    token_user: Annotated[models.User, Depends(get_token_user)],
    userId: int | None = None,
    db: Session = Depends(appdb.get_db)
):
    """
    Get specified users active subscriptions

    If no userId is specified, get a list of all active subscriptions

    If authorized as normal user, return list of his own subscriptions
    """
    # Return users active subscriptions
    if not token_user.isAdmin:
        return db.query(models.Sub).filter(
            models.Sub.userId == token_user.id
        ).all()

    # If admin, return active subscriptions of specified user
    if userId:
        db_user = db.query(models.User).filter(
            models.User.id == userId
        ).first()

        if not db_user:
            raise_exception_no_user()

        return db.query(models.Sub).filter(
            models.Sub.userId == db_user.id
        ).all()

    # If admin, return all active subscriptions
    return db.query(models.Sub).all()
        
@router.delete("/cancel_subscription", response_model=schemas.transaction.TransactionResponse)
def cancel_subscription(
    token_user: Annotated[models.User, Depends(get_token_user)],
    productId: int,
    userId: int,
    db: Session = Depends(appdb.get_db)
):
    """
    Cancel specified users active subscription

    If authorized as normal user, you can only cancel your own subscriptions
    """
    # Cancel users subscription and write this action to db as transaction
    if not token_user.isAdmin:
        db_subscription = db.query(models.Sub).filter(
            models.Sub.userId == token_user.id,
            models.Sub.productId == productId
        ).first()
        if not db_subscription:
            raise_exception_no_subscription()

        new_transaction = models.Transaction(
            userId = token_user.id,
            productId = productId,
            action = "Cancel subscription",
            dateTime = datetime.now(timezone.utc),
            status = "Success",
            bankChange = 0
        )
        db.delete(db_subscription)
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction

    
    # If admin, cancel specified users subscription and write this action to db as transaction
    db_user = db.query(models.User).filter(
        models.User.id == userId
    ).first()
    if not db_user:
        raise_exception_no_user()

    db_subscription = db.query(models.Sub).filter(
        models.Sub.userId == userId,
        models.Sub.productId == productId
    ).first()
    if not db_subscription:
        raise_exception_no_subscription()

    new_transaction = models.Transaction(
        userId = userId,
        productId = productId,
        action = "ADMIN - Cancel subscription",
        dateTime = datetime.now(timezone.utc),
        status = "Success",
        bankChange = 0
    )
    db.delete(db_subscription)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction
