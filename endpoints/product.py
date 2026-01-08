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
import schemas.user, schemas.token, schemas.product
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/products", tags=["products"])

# Endpoints
@router.post("/create_product", response_model=schemas.product.ProductResponse)
def create_product(
    product: schemas.product.ProductCreate,
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
):
    """
    Create a new product and add it to database

    Must be admin to use this endpoint
    """
    # Check if user is admin
    if not token_user.isAdmin:
        raise_exception_admin()

    # Check if product name is already taken
    db_product = db.query(models.Product).filter(
        models.Product.name == product.name
    ).first()

    if db_product:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name already taken"
        )

    # Add new product to db
    new_product = models.Product(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/get_products", response_model=List[schemas.product.ProductResponse])
def get_products(
    db: Session = Depends(appdb.get_db)
):
    """
    Get list of all avaiable products
    """
    return db.query(models.Product).all()


@router.post("/update_product", response_model=schemas.product.ProductResponse)
def update_product(
    id: int,
    product: schemas.product.ProductCreate,
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
):
    """
    Update product's name and price in database

    Must be admin to use this endpoint
    """
    # Check if user is admin
    if not token_user.isAdmin:
        raise_exception_admin()

    # Check if product name is already taken
    db_product = db.query(models.Product).filter(
        models.Product.name == product.name
    ).first()
    if db_product:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name already taken"
        )

    # Check if product exists in db
    db_target_product = db.query(models.Product).filter(
        models.Product.id == id
    ).first()
    if not db_target_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product does not exist"
        )

    # Update product in db
    db_target_product.name = product.name
    db_target_product.price = product.price

    db.commit()
    db.refresh(db_target_product)
    return db_target_product
