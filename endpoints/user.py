from datetime import datetime, timedelta, timezone
from typing import Annotated, List
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Imports from local files
import db.database as appdb
import db.models as models
import schemas.user, schemas.token
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/users", tags=["users"])

# Endpoints
@router.post("/create_user", response_model=schemas.user.UserResponse)
def create_user(
        user: schemas.user.UserCreate,
        db: Session = Depends(appdb.get_db)
):
    # Check if email is already registered
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if db_user:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password and store users credentials to db
    new_user = models.User(**user.model_dump())
    new_user.password = password_hash.hash(new_user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

'''
@router.get("/get_user/", response_model=schemas.user.UserResponse)
def get_user(
    id: int,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(appdb.get_db)
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

    '''

@router.get("/get_users/", response_model=List[schemas.user.UserResponse])
def get_users(
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
):
    if not token_user.isAdmin:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Must be admin to use this endpoint!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return db.query(models.User).all()




