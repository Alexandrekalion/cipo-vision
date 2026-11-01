from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .db import get_db
from .models import User

def current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer dev-"):
        raise HTTPException(401, "Autenticação necessária")
    username = authorization.removeprefix("Bearer dev-")
    user = db.query(User).filter(User.username == username, User.active.is_(True)).first()
    if not user: raise HTTPException(401, "Usuário de desenvolvimento inválido")
    return user

def require_roles(*roles):
    def dependency(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(403, "Perfil sem permissão para esta operação")
        return user
    return dependency
