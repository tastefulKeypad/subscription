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
import schemas.user, schemas.token, schemas.product, schemas.promo
from endpoints.commonFunctions import *
from securityConfig import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter(prefix="/promos", tags=["promos"])

# Endpoints
@router.post("/create_promo", response_model=schemas.promo.PromoResponse)
def create_promo(
    promo: schemas.promo.PromoCreate,
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
):
    """
    Create a new promo and add it to database

    Must be admin to use this endpoint
    """
    # Check if user is admin
    if not token_user.isAdmin:
        raise_exception_admin()

    # Check if promo name is already taken
    db_promo = db.query(models.Promo).filter(
        models.Promo.name == promo.name
    ).first()

    if db_promo:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Promo name already taken"
        )

    # Check if product id exists
    db_product = db.query(models.Product).filter(
        models.Product.id == promo.productId
    ).first()

    if not db_product:
        raise_exception_no_product()

    # Add new promo to db
    new_promo = models.Promo(**promo.model_dump())
    db.add(new_promo)
    db.commit()
    db.refresh(new_promo)
    return new_promo

@router.get("/get_promos", response_model=List[schemas.promo.PromoResponse])
def get_promos(
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
):
    """
    Get list of all avaiable promos

    Must be admin to use this endpoint
    """
    if not token_user.isAdmin:
        raise_exception_admin()
    return db.query(models.Promo).all()

@router.delete("/delete_promo")
def delete_promo(
    promoName: str,
    token_user: Annotated[models.User, Depends(get_token_user)],
    db: Session = Depends(appdb.get_db)
) -> bool:
    """
    Delete promo from db

    Must be admin to use this endpoint
    """
    if not token_user.isAdmin:
        raise_exception_admin()

    # Check if promo with specified name exists
    db_promo = db.query(models.Promo).filter(
        models.Promo.name == promoName
    ).first()

    if not db_promo:
        raise_exception_no_promo()
    
    # Delete promo from db
    db.delete(db_promo)
    db.commit()
    return True
