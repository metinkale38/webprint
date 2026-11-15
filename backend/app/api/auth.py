from datetime import datetime, timezone

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.user import User
from ..schemas.auth import LoginRequest
from ..schemas.user import UserOut
from ..security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    decode_token,
    set_auth_cookies,
    verify_password,
)
from .deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not user.active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    set_auth_cookies(
        response,
        create_access_token(user.username, user.role),
        create_refresh_token(user.username, user.role),
    )
    return user


@router.post("/refresh", response_model=UserOut)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Kein Refresh-Token")
    try:
        payload = decode_token(refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Ungültiger Refresh-Token") from exc
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Ungültiger Token-Typ")
    user = db.query(User).filter(User.username == payload.get("sub"), User.active.is_(True)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Benutzer nicht gefunden")
    set_auth_cookies(
        response,
        create_access_token(user.username, user.role),
        create_refresh_token(user.username, user.role),
    )
    return user


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    clear_auth_cookies(response)
    return {"status": "ok"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
