from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, analytics
from app.deps import get_owned_business

router = APIRouter(prefix="/api/businesses/{business_id}/inventory", tags=["inventory"])


@router.get("")
def inventory_overview(business_id: str, db: Session = Depends(get_db),
                        business: models.Business = Depends(get_owned_business)):
    """Stock levels enriched with velocity + estimated days of cover, per blueprint section 4."""
    products = db.query(models.Product).filter(models.Product.business_id == business.id).all()
    overview = []
    for p in products:
        avg_daily = analytics.average_daily_sales(db, p.id)
        coverage = analytics.stock_coverage_days(p.quantity, avg_daily)
        overview.append({
            "product_id": p.id,
            "name": p.name,
            "quantity": p.quantity,
            "minimum_stock": p.minimum_stock,
            "avg_daily_sales": avg_daily,
            "estimated_days_of_cover": coverage,
            "low_stock": p.quantity <= p.minimum_stock,
            "expiry_date": p.expiry_date,
        })
    return overview


@router.get("/expiring")
def expiring(business_id: str, within_days: int = 7, db: Session = Depends(get_db),
             business: models.Business = Depends(get_owned_business)):
    products = analytics.expiring_products(db, business.id, within_days)
    return [{"product_id": p.id, "name": p.name, "quantity": p.quantity, "expiry_date": p.expiry_date}
            for p in products]


@router.get("/slow-moving")
def slow_moving(business_id: str, db: Session = Depends(get_db),
                 business: models.Business = Depends(get_owned_business)):
    return analytics.slow_moving_products(db, business.id)


@router.post("/{product_id}/adjust", response_model=schemas.ProductOut)
def adjust_stock(business_id: str, product_id: str, payload: schemas.StockAdjustment,
                  db: Session = Depends(get_db), business: models.Business = Depends(get_owned_business)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id, models.Product.business_id == business.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_qty = product.quantity + payload.quantity_change
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Adjustment would result in negative stock")

    product.quantity = new_qty
    movement = models.InventoryMovement(
        product_id=product.id,
        movement_type=models.MovementType.ADJUSTMENT,
        quantity_change=payload.quantity_change,
        note=payload.note,
    )
    db.add(movement)
    db.commit()
    db.refresh(product)
    return product
