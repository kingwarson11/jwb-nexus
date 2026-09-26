from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import decode_access_token
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_owned_business(business_id: str, db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)) -> models.Business:
    """Ensures the requested business belongs to the authenticated user."""
    business = db.query(models.Business).filter(
        models.Business.id == business_id,
        models.Business.owner_id == current_user.id,
    ).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
