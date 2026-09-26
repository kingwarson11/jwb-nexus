from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/trends", response_model=List[schemas.MarketTrendOut])
def market_trends(area: Optional[str] = None, category: Optional[str] = None,
                   db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Anonymised, aggregated demand trends (blueprint sections 8-9).
    Never returns anything tied to an individual business — market_metrics only
    ever stores aggregated numbers plus a participating-business count.
    """
    query = db.query(models.MarketMetric)
    if area:
        query = query.filter(models.MarketMetric.area == area)
    if category:
        query = query.filter(models.MarketMetric.category == category)
    return query.order_by(models.MarketMetric.period_end.desc()).limit(100).all()


@router.get("/areas")
def list_areas(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    rows = db.query(models.MarketMetric.area).distinct().all()
    return [r[0] for r in rows]
