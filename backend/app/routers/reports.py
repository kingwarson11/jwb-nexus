from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas, analytics
from app.deps import get_owned_business

router = APIRouter(prefix="/api/businesses/{business_id}/reports", tags=["reports"])


def _today_bounds():
    start = datetime.combine(date.today(), datetime.min.time())
    end = start + timedelta(days=1)
    return start, end


@router.get("/dashboard", response_model=schemas.DashboardSummary)
def dashboard(business_id: str, db: Session = Depends(get_db),
              business: models.Business = Depends(get_owned_business)):
    """The main dashboard, per blueprint section 14."""
    start, end = _today_bounds()

    today_sales = db.query(models.Sale).filter(
        models.Sale.business_id == business.id,
        models.Sale.created_at >= start, models.Sale.created_at < end,
        models.Sale.status == "COMPLETED",
    ).all()

    today_revenue = sum(s.total for s in today_sales)
    today_cogs = sum(s.cost_of_goods_sold for s in today_sales)

    inventory_value = (
        db.query(func.coalesce(func.sum(models.Product.quantity * models.Product.cost_price), 0))
        .filter(models.Product.business_id == business.id)
        .scalar()
    ) or 0

    low_stock_count = len(analytics.low_stock_products(db, business.id))
    expiring_soon_count = len(analytics.expiring_products(db, business.id, within_days=7))
    slow_moving_count = len(analytics.slow_moving_products(db, business.id))

    return schemas.DashboardSummary(
        today_revenue=round(today_revenue, 2),
        today_sales_count=len(today_sales),
        gross_profit_today=round(today_revenue - today_cogs, 2),
        inventory_value=round(inventory_value, 2),
        low_stock_count=low_stock_count,
        expiring_soon_count=expiring_soon_count,
        slow_moving_count=slow_moving_count,
    )


@router.get("/income-statement", response_model=schemas.IncomeStatement)
def income_statement(business_id: str, start: date, end: date, db: Session = Depends(get_db),
                      business: models.Business = Depends(get_owned_business)):
    """Revenue - COGS = Gross profit; Gross profit - Opex = Net profit (blueprint section 13)."""
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    sales = db.query(models.Sale).filter(
        models.Sale.business_id == business.id,
        models.Sale.created_at >= start_dt, models.Sale.created_at <= end_dt,
        models.Sale.status == "COMPLETED",
    ).all()
    revenue = sum(s.total for s in sales)
    cogs = sum(s.cost_of_goods_sold for s in sales)
    gross_profit = revenue - cogs

    opex = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0))
        .filter(models.Expense.business_id == business.id,
                models.Expense.date >= start, models.Expense.date <= end)
        .scalar()
    ) or 0

    return schemas.IncomeStatement(
        period_start=start, period_end=end,
        revenue=round(revenue, 2), cost_of_goods_sold=round(cogs, 2),
        gross_profit=round(gross_profit, 2), operating_expenses=round(opex, 2),
        net_profit=round(gross_profit - opex, 2),
    )


@router.get("/cash-flow", response_model=schemas.CashFlowStatement)
def cash_flow(business_id: str, start: date, end: date, opening_balance: float = 0,
              db: Session = Depends(get_db), business: models.Business = Depends(get_owned_business)):
    """Opening balance + revenue (cash in) - expenses (cash out) = closing position (blueprint section 13)."""
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    cash_in = (
        db.query(func.coalesce(func.sum(models.Sale.total), 0))
        .filter(models.Sale.business_id == business.id,
                models.Sale.created_at >= start_dt, models.Sale.created_at <= end_dt,
                models.Sale.status == "COMPLETED")
        .scalar()
    ) or 0

    cash_out = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0))
        .filter(models.Expense.business_id == business.id,
                models.Expense.date >= start, models.Expense.date <= end)
        .scalar()
    ) or 0

    closing = opening_balance + cash_in - cash_out

    return schemas.CashFlowStatement(
        period_start=start, period_end=end,
        opening_balance=round(opening_balance, 2), cash_in=round(cash_in, 2),
        cash_out=round(cash_out, 2), closing_balance=round(closing, 2),
        net_cash_flow=round(cash_in - cash_out, 2),
    )
