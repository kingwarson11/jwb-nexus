from datetime import date as date_cls
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.deps import get_owned_business

router = APIRouter(prefix="/api/businesses/{business_id}/expenses", tags=["expenses"])


@router.post("", response_model=schemas.ExpenseOut)
def create_expense(business_id: str, payload: schemas.ExpenseCreate, db: Session = Depends(get_db),
                    business: models.Business = Depends(get_owned_business)):
    data = payload.model_dump()
    data["date"] = data.get("date") or date_cls.today()
    expense = models.Expense(business_id=business.id, **data)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=List[schemas.ExpenseOut])
def list_expenses(business_id: str, db: Session = Depends(get_db),
                   business: models.Business = Depends(get_owned_business)):
    return db.query(models.Expense).filter(models.Expense.business_id == business.id).order_by(
        models.Expense.date.desc()
    ).all()
