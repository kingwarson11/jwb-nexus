from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/api/businesses", tags=["businesses"])


@router.post("", response_model=schemas.BusinessOut)
def create_business(payload: schemas.BusinessCreate, db: Session = Depends(get_db),
                     current_user: models.User = Depends(get_current_user)):
    business = models.Business(owner_id=current_user.id, **payload.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@router.get("", response_model=List[schemas.BusinessOut])
def list_my_businesses(db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)):
    return db.query(models.Business).filter(models.Business.owner_id == current_user.id).all()


@router.get("/{business_id}", response_model=schemas.BusinessOut)
def get_business(business_id: str, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    from app.deps import get_owned_business
    return get_owned_business(business_id, db, current_user)
