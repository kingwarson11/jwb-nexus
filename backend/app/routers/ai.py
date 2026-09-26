from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, ai_engine
from app.deps import get_owned_business

router = APIRouter(prefix="/api/businesses/{business_id}/ai", tags=["ai"])


@router.post("/query", response_model=schemas.AIResponse)
def ask(business_id: str, payload: schemas.AIQuery, db: Session = Depends(get_db),
        business: models.Business = Depends(get_owned_business)):
    """
    The 'JARVIS' component (blueprint section 7): merchant asks in plain language,
    we pull verified facts from the database, then explain them — never invented numbers.
    """
    facts = ai_engine.gather_facts(db, business)
    answer = ai_engine.explain_facts(payload.question, facts)
    return schemas.AIResponse(answer=answer, facts=facts)
