import jwt
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.user import User
from ..security import decode_token

_CREDENTIALS_EXCEPTION = HTTPException(status_code=401, detail="Nicht angemeldet")


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise _CREDENTIALS_EXCEPTION
    try:
        payload = decode_token(access_token)
    except jwt.PyJWTError as exc:
        raise _CREDENTIALS_EXCEPTION from exc
    if payload.get("type") != "access":
        raise _CREDENTIALS_EXCEPTION
    user = db.query(User).filter(User.username == payload.get("sub"), User.active.is_(True)).first()
    if user is None:
        raise _CREDENTIALS_EXCEPTION
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Adminrechte erforderlich")
    return user
