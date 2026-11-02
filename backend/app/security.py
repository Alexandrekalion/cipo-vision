from datetime import datetime, timedelta, timezone
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Cookie, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db
from .models import User, UserCredential, UserSession

SESSION_COOKIE = "cipo_session"
CSRF_HEADER = "X-CSRF-Token"
SESSION_HOURS = 8
hasher = PasswordHasher()

def hash_password(password: str) -> str:
    return hasher.hash(password)

def verify_password(password: str, encoded: str) -> bool:
    try:
        return hasher.verify(encoded, password)
    except (VerifyMismatchError, VerificationError):
        return False

def create_session(response: Response, user: User, db: Session) -> UserSession:
    now = datetime.now(timezone.utc)
    session = UserSession(id=secrets.token_urlsafe(48), user_id=user.id, csrf_token=secrets.token_urlsafe(32), expires_at=now + timedelta(hours=SESSION_HOURS))
    db.add(session); db.commit()
    response.set_cookie(SESSION_COOKIE, session.id, httponly=True, secure=False, samesite="lax", max_age=SESSION_HOURS * 3600)
    return session

def current_session(cipo_session: str | None = Cookie(default=None), db: Session = Depends(get_db)) -> tuple[User, UserSession]:
    if not cipo_session: raise HTTPException(401, "Autenticação necessária")
    session = db.get(UserSession, cipo_session)
    now = datetime.now(timezone.utc)
    if not session or session.revoked_at or session.expires_at <= now: raise HTTPException(401, "Sessão inválida ou expirada")
    user = db.get(User, session.user_id)
    if not user or not user.active: raise HTTPException(401, "Usuário inativo")
    return user, session

def current_user(session_data=Depends(current_session)) -> User:
    return session_data[0]

def require_csrf(x_csrf_token: str | None = Header(default=None), session_data=Depends(current_session)):
    if not x_csrf_token or not secrets.compare_digest(x_csrf_token, session_data[1].csrf_token):
        raise HTTPException(403, "Proteção CSRF inválida")

def require_roles(*roles):
    def dependency(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(403, "Perfil sem permissão")
        return user
    return dependency
