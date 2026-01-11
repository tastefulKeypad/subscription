from datetime import datetime, timedelta, timezone
from typing import Annotated, List
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import update
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Imports from local files
import db.database as appdb
import db.models as models
import schemas.user, schemas.token, schemas.product, schemas.promo, schemas.sub, schemas.transaction
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/refunds", tags=["refunds"])

# Endpoints
@router.post("/ask_for_refund", response_model=schemas.transaction.TransactionResponse)
def ask_for_refund(
    token_user: Annotated[models.User, Depends(get_token_user)],
    transactionId: int,
    db: Session = Depends(appdb.get_db)
):
    """
    Post a refund request for admins to review

    Refunds can only be asked for transactions that resulted in a successful payment
    AND it was made in the past 7 days
    AND user did not try to refund it earlier

    You can get a list of eligible refunds using:
    /transactions/get_transactions_eligible_for_refund

    Must be normal user to use this endpoint
    """
    # Check if user is a normal user
    if token_user.isAdmin:
        raise_exception_user()

    # Check if specified transactionId is eligible for refund
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id           == transactionId,
        models.Transaction.userId       == token_user.id,
        or_(
            models.Transaction.triedRefund == False,
            models.Transaction.triedRefund.is_(None)
        )
    ).first()
    if not db_transaction:
        raise_exception_no_transaction()

    date_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    if not db_transaction.bankChange > 0 or not db_transaction.status == "Success" or not db_transaction.dateTime.timestamp() >= date_cutoff.timestamp():
        raise_exception_transaction_not_refundable()

    new_transaction = models.Transaction(
        userId = db_transaction.userId,
        productId = db_transaction.productId,
        promoName = db_transaction.promoName,
        action = "Refund request",
        dateTime = datetime.now(timezone.utc),
        status = "Pending",
        toRefund = db_transaction.bankChange,
        bankChange = 0
    )
    db_transaction.triedRefund = True
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.get("/get_pending_refunds", response_model=List[schemas.transaction.TransactionResponse])
def get_pending_refunds(
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
):
    """
    Get a list of all pending refunds

    Must be admin to use this endpoint
    """
    # Check if user is admin
    if not token_user.isAdmin:
        raise_exception_admin()

    # Get list of pending refunds
    return db.query(models.Transaction).filter(
        models.Transaction.action == "Refund request",
        models.Transaction.status == "Pending",
        or_(
            models.Transaction.triedRefund == False,
            models.Transaction.triedRefund.is_(None)
        )
    ).all()

# Admins can approve/decline pending refunds 
# If refund is approved, send it to scheduled tasks service
@router.post("/control_refund")
def control_refund(
    transactionId: int,
    approved: bool,
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
):
    """
    Approve/decline refund request 

    If refund was approved, send it to scheduled tasks queue

    Must be admin to use this endpoint
    """
    # Check if user is admin
    if not token_user.isAdmin:
        raise_exception_admin()

    # Check that specified transaction id exists and it is eligible for refund
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id           == transactionId,
        models.Transaction.action == "Refund request",
        models.Transaction.status == "Pending",
        or_(
            models.Transaction.triedRefund == False,
            models.Transaction.triedRefund.is_(None)
        )
    ).first()
    if not db_transaction:
        raise_exception_no_transaction()
    

    db_transaction.triedRefund = True
    if not approved:
        new_transaction = models.Transaction(
            userId = db_transaction.userId,
            productId = db_transaction.productId,
            promoName = db_transaction.promoName,
            action = "Refund request",
            dateTime = datetime.now(timezone.utc),
            status = "Declined",
            toRefund = db_transaction.toRefund,
            bankChange = 0
        )
        db.add(new_transaction)
    else:
        new_transaction = models.Transaction(
            userId = 0,
            hiddenUserId = db_transaction.userId,
            productId = db_transaction.productId,
            promoName = db_transaction.promoName,
            action = "Refund request",
            dateTime = datetime.now(timezone.utc),
            status = "Awaiting scheduled task",
            toRefund = db_transaction.toRefund,
            bankChange = 0
        )
        db.add(new_transaction)
    
    db.commit()
    return {"message": "Successfully dealt with specified refund request"}
