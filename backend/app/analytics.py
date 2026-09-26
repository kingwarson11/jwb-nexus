"""
Lightweight analytics helpers — no ML needed yet, just moving averages,
per the blueprint's AI Architecture stage 2 (Analytics) and stage 4 (Forecasting).
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app import models


def average_daily_sales(db: Session, product_id: str, days: int = 14) -> float:
    since = datetime.utcnow() - timedelta(days=days)
    total = (
        db.query(func.coalesce(func.sum(models.SaleItem.quantity), 0))
        .join(models.Sale, models.Sale.id == models.SaleItem.sale_id)
        .filter(models.SaleItem.product_id == product_id, models.Sale.created_at >= since)
        .scalar()
    )
    return round((total or 0) / days, 2)


def stock_coverage_days(quantity: int, avg_daily_sales: float) -> float | None:
    if avg_daily_sales <= 0:
        return None
    return round(quantity / avg_daily_sales, 1)


def slow_moving_products(db: Session, business_id: str, recent_days: int = 7, baseline_days: int = 28,
                          decline_threshold: float = 0.30):
    """
    Compares recent sales velocity against a longer baseline per product.
    Flags products whose recent-period sales dropped more than `decline_threshold`.
    """
    now = datetime.utcnow()
    recent_start = now - timedelta(days=recent_days)
    baseline_start = now - timedelta(days=baseline_days)

    products = db.query(models.Product).filter(models.Product.business_id == business_id).all()
    results = []
    for product in products:
        recent_qty = (
            db.query(func.coalesce(func.sum(models.SaleItem.quantity), 0))
            .join(models.Sale, models.Sale.id == models.SaleItem.sale_id)
            .filter(models.SaleItem.product_id == product.id, models.Sale.created_at >= recent_start)
            .scalar()
        ) or 0
        baseline_qty = (
            db.query(func.coalesce(func.sum(models.SaleItem.quantity), 0))
            .join(models.Sale, models.Sale.id == models.SaleItem.sale_id)
            .filter(models.SaleItem.product_id == product.id, models.Sale.created_at >= baseline_start,
                    models.Sale.created_at < recent_start)
            .scalar()
        ) or 0

        baseline_period_days = baseline_days - recent_days
        baseline_weekly_avg = (baseline_qty / baseline_period_days) * recent_days if baseline_period_days > 0 else 0

        if baseline_weekly_avg >= 5:  # ignore near-zero-volume products (noise)
            decline = (baseline_weekly_avg - recent_qty) / baseline_weekly_avg
            if decline >= decline_threshold:
                results.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "recent_period_units": recent_qty,
                    "baseline_period_units": round(baseline_weekly_avg, 1),
                    "decline_pct": round(decline * 100, 1),
                    "current_stock": product.quantity,
                })
    return results


def expiring_products(db: Session, business_id: str, within_days: int = 7):
    cutoff = (datetime.utcnow() + timedelta(days=within_days)).date()
    return (
        db.query(models.Product)
        .filter(
            models.Product.business_id == business_id,
            models.Product.expiry_date.isnot(None),
            models.Product.expiry_date <= cutoff,
        )
        .all()
    )


def low_stock_products(db: Session, business_id: str):
    return (
        db.query(models.Product)
        .filter(
            models.Product.business_id == business_id,
            models.Product.quantity <= models.Product.minimum_stock,
        )
        .all()
    )
