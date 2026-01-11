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
router = APIRouter(prefix="/transactions", tags=["transactions"])

# Endpoints
@router.get("/get_transaction_history", response_model=List[schemas.transaction.TransactionResponse])
def get_transaction_history(
    token_user: Annotated[models.User, Depends(get_token_user)],
    userId: int,
    db: Session = Depends(appdb.get_db)
):
    """
    Get transaction history of specified user

    If authorized as normal user, return own transaction history
    """
    # If user is a normal user, return his own transaction history
    if not token_user.isAdmin:
        return db.query(models.Transaction).filter(models.Transaction.userId == token_user.id).all()

    # Check if specified user exists and it's not system user with id == 0
    db_user = db.query(models.User).filter(
        models.User.id == userId
    ).first()
    if not db_user and userId != 0:
        raise_exception_no_user()

    return db.query(models.Transaction).filter(models.Transaction.userId == userId).all()

@router.get("/get_transactions_eligible_for_refund", response_model=List[schemas.transaction.TransactionResponse])
def get_transactions_eligible_for_refund(
    token_user: Annotated[models.User, Depends(get_token_user)],
    userId: int,
    db: Session = Depends(appdb.get_db)
):
    """
    Get transactions eligible for refund of specified user

    Transaction is considered to be eligible for refund only if payment was successful
    AND it was made in the past 7 days
    AND user did not try to refund it earlier

    If authorized as normal user, return own transactions eligible for refund
    """
    date_cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    # If user is a normal user, return his own transactions eligible for refund
    if not token_user.isAdmin:
        return db.query(models.Transaction).filter(
            models.Transaction.userId      == token_user.id,
            models.Transaction.status      == "Success",
            models.Transaction.dateTime    >= date_cutoff,
            models.Transaction.bankChange  > 0,
            or_(
                models.Transaction.triedRefund == False,
                models.Transaction.triedRefund.is_(None)
            )
        ).all()

    # Check if specified user exists
    db_user = db.query(models.User).filter(
        models.User.id == userId
    ).first()
    if not db_user:
        raise_exception_no_user()

    return db.query(models.Transaction).filter(
        models.Transaction.userId      == userId,
        models.Transaction.status      == "Success",
        models.Transaction.dateTime    >= date_cutoff,
        models.Transaction.bankChange  > 0,
        or_(
            models.Transaction.triedRefund == False,
            models.Transaction.triedRefund.is_(None)
        )
    ).all()
