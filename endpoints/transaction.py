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
router = APIRouter(prefix="/transactions", tags=["transactions"])

# Endpoints
@router.post("/get_transaction_history", response_model=List[schemas.transaction.TransactionResponse])
def get_transaction_history(
    token_user: Annotated[models.User, Depends(get_token_user)],
    userId: int,
    db: Session = Depends(appdb.get_db)
):
    """
    Get transaction history of specified user

    If normal user, return own transaction history
    """
    # Check if user is a normal user
    if not token_user.isAdmin:
        return db.query(models.Transaction).filter(models.Transaction.userId == token_user.id).all()

    # Check if specified user exists
    db_user = db.query(models.User).filter(
        models.User.id == userId
    ).first()
    if not db_user:
        raise_exception_no_user()

    return db.query(models.Transaction).filter(models.Transaction.userId == userId).all()
