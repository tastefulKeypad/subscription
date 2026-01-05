from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.database import engine, Base
from .. import dependencies
from .. import schemas.user
from .. import db.models


router = APIRouter(prefix="/users")

@router.get("/", response_model=schemas.UserResponse)
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(dependencies.get_db)
):
    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if db_user:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
