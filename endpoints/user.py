from datetime import datetime, timedelta, timezone
from typing import Annotated, List
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

# Imports from local files
#from db.database import engine, Base
import db.database as appdb
import db.models as models
import schemas.user, schemas.token
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")
router = APIRouter(prefix="/users", tags=["users"])

# Functions
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def authenticate_user(
    email: str,
    password: str,
    db: Session
):
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(appdb.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.token.TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = db.query(models.User).filter(
        models.User.email == token_data.username
    ).first()
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@router.post("/token")
def login_for_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(appdb.get_db)
) -> schemas.token.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return schemas.token.Token(access_token=access_token, token_type="bearer")


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

    # Hash password and store user's credentials to db
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




