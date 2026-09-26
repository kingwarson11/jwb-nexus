from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user, get_owned_business

router = APIRouter(prefix="/api/businesses/{business_id}/suppliers", tags=["suppliers"])


@router.post("", response_model=schemas.SupplierOut)
def create_supplier(business_id: str, payload: schemas.SupplierCreate, db: Session = Depends(get_db),
                     business: models.Business = Depends(get_owned_business)):
    supplier = models.Supplier(business_id=business.id, **payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("", response_model=List[schemas.SupplierOut])
def list_suppliers(business_id: str, db: Session = Depends(get_db),
                    business: models.Business = Depends(get_owned_business)):
    return db.query(models.Supplier).filter(models.Supplier.business_id == business.id).all()
