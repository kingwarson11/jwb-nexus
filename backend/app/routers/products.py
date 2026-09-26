from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.deps import get_owned_business

router = APIRouter(prefix="/api/businesses/{business_id}/products", tags=["products"])


@router.post("", response_model=schemas.ProductOut)
def create_product(business_id: str, payload: schemas.ProductCreate, db: Session = Depends(get_db),
                    business: models.Business = Depends(get_owned_business)):
    product = models.Product(business_id=business.id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    if product.quantity:
        movement = models.InventoryMovement(
            product_id=product.id,
            movement_type=models.MovementType.PURCHASE,
            quantity_change=product.quantity,
            note="Initial stock on product creation",
        )
        db.add(movement)
        db.commit()

    return product


@router.get("", response_model=List[schemas.ProductOut])
def list_products(business_id: str, db: Session = Depends(get_db),
                   business: models.Business = Depends(get_owned_business)):
    return db.query(models.Product).filter(models.Product.business_id == business.id).all()


@router.patch("/{product_id}", response_model=schemas.ProductOut)
def update_product(business_id: str, product_id: str, payload: schemas.ProductUpdate,
                    db: Session = Depends(get_db), business: models.Business = Depends(get_owned_business)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id, models.Product.business_id == business.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(business_id: str, product_id: str, db: Session = Depends(get_db),
                    business: models.Business = Depends(get_owned_business)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id, models.Product.business_id == business.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"ok": True}
