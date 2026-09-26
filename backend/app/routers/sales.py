from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.deps import get_owned_business
from app.payments import get_adapter

router = APIRouter(prefix="/api/businesses/{business_id}/sales", tags=["sales"])


@router.post("", response_model=schemas.SaleOut)
def create_sale(business_id: str, payload: schemas.SaleCreate, db: Session = Depends(get_db),
                 business: models.Business = Depends(get_owned_business)):
    """
    The core POS loop (blueprint Figure 3.1 / section 29):
    validate stock -> create sale -> reduce inventory -> record payment -> financials update.
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="Sale must include at least one item")

    subtotal = 0.0
    cogs = 0.0
    line_items = []

    for item in payload.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id, models.Product.business_id == business.id
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product.name}")

        line_total = product.selling_price * item.quantity
        subtotal += line_total
        cogs += product.cost_price * item.quantity
        line_items.append((product, item.quantity, line_total))

    total = max(subtotal - payload.discount, 0)

    sale = models.Sale(
        business_id=business.id,
        customer_id=payload.customer_id,
        subtotal=subtotal,
        discount=payload.discount,
        total=total,
        cost_of_goods_sold=cogs,
    )
    db.add(sale)
    db.flush()  # get sale.id before commit

    for product, qty, line_total in line_items:
        db.add(models.SaleItem(
            sale_id=sale.id, product_id=product.id, quantity=qty,
            unit_price=product.selling_price, unit_cost=product.cost_price, line_total=line_total,
        ))
        product.quantity -= qty
        db.add(models.InventoryMovement(
            product_id=product.id, movement_type=models.MovementType.SALE,
            quantity_change=-qty, reference=sale.id,
        ))

    # Payment (mock MoMo / manual adapters — see app/payments.py)
    adapter = get_adapter(payload.payment.method)
    result = adapter.charge(payload.payment.amount)
    payment = models.Payment(
        sale_id=sale.id,
        method=payload.payment.method,
        amount=payload.payment.amount,
        status=result["status"],
        provider_reference=payload.payment.provider_reference or result["provider_reference"],
    )
    db.add(payment)

    db.commit()
    db.refresh(sale)
    return sale


@router.get("", response_model=List[schemas.SaleOut])
def list_sales(business_id: str, db: Session = Depends(get_db),
               business: models.Business = Depends(get_owned_business)):
    return db.query(models.Sale).filter(models.Sale.business_id == business.id).order_by(
        models.Sale.created_at.desc()
    ).all()


@router.get("/{sale_id}", response_model=schemas.SaleOut)
def get_sale(business_id: str, sale_id: str, db: Session = Depends(get_db),
             business: models.Business = Depends(get_owned_business)):
    sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id, models.Sale.business_id == business.id
    ).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.post("/{sale_id}/refund", response_model=schemas.SaleOut)
def refund_sale(business_id: str, sale_id: str, db: Session = Depends(get_db),
                 business: models.Business = Depends(get_owned_business)):
    sale = db.query(models.Sale).filter(
        models.Sale.id == sale_id, models.Sale.business_id == business.id
    ).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.status == "REFUNDED":
        raise HTTPException(status_code=400, detail="Sale already refunded")

    for item in sale.items:
        product = db.query(models.Product).get(item.product_id)
        if product:
            product.quantity += item.quantity
            db.add(models.InventoryMovement(
                product_id=product.id, movement_type=models.MovementType.ADJUSTMENT,
                quantity_change=item.quantity, reference=sale.id, note="Refund",
            ))
    sale.status = "REFUNDED"
    db.commit()
    db.refresh(sale)
    return sale
