from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from .core.db import get_session
from .core.security import decode_token
from .models import User
from .core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db(session: Session = Depends(get_session)):
    return session

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    user = db.exec(select(User).where(User.email == user_email)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inativo ou inexistente")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return user

def is_locked(user: User) -> bool:
    if user.lock_until is None:
        return False
    now = datetime.now(timezone.utc)
    return user.lock_until.replace(tzinfo=timezone.utc) > now
