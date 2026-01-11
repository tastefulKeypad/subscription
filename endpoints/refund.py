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
import db.database as appdb
import db.models as models
import schemas.user, schemas.token, schemas.product, schemas.promo, schemas.sub, schemas.transaction
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/refunds", tags=["refunds"])

# Endpoints
@router.post("/ask_for_refund", response_model=List[schemas.transaction.TransactionResponse])
def ask_for_refund(
    token_user: Annotated[models.User, Depends(get_token_user)],
    transactionId: int,
    db: Session = Depends(appdb.get_db)
):
    """
    Post a refund request for admins to review

    Refunds can only be asked for transactions that resulted in a successful payment
    AND it was made in the past 7 days

    You can get a list of eligible refunds using:
    /transactions/get_transactions_eligible_for_refund

    Must be normal user to use this endpoint
    """
    # Check if user is a normal user
    if token_user.isAdmin:
        raise_exception_user()

    # Check if specified transactionId is eligible for refund
    db_transaction = db.query(models.Transaction).filter(
        models.Transaction.id     == transactionId,
        models.Transaction.userId == token_user.id
    ).first()
    if not db_transaction:
        raise_exception_no_transaction()

    return db.query(models.Transaction).filter(models.Transaction.userId == userId).all()
