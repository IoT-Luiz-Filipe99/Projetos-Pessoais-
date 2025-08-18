from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from ..schemas import LoginRequest, TokenPair, RefreshRequest, UserOut
from ..core.security import verify_password, hash_password, create_token, decode_token
from ..core.config import settings
from ..deps import get_db, is_locked
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.email == payload.email)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # bloqueio por tentativas
    if is_locked(user):
        raise HTTPException(status_code=423, detail="Usuário bloqueado temporariamente. Tente mais tarde.")

    if not verify_password(payload.password, user.hashed_password):
        user.failed_attempts += 1
        if user.failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            user.lock_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCK_MINUTES)
            user.failed_attempts = 0  # zera para próximo ciclo
        db.add(user); db.commit()
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # sucesso: zera contadores
    user.failed_attempts = 0
    user.lock_until = None
    db.add(user); db.commit()

    access = create_token(user.email, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh = create_token(user.email, settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest):
    decoded = decode_token(payload.refresh_token)
    if not decoded:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    email = decoded.get("sub")
    access = create_token(email, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh = create_token(email, settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return TokenPair(access_token=access, refresh_token=refresh)

# endpoint simples para criar admin no início (remova em prod)
@router.post("/bootstrap-admin", response_model=UserOut)
def bootstrap_admin(db: Session = Depends(get_db)):
    existing = db.exec(select(User).where(User.email == "admin@local.test")).first()
    if existing: return existing
    user = User(
        email="admin@local.test",
        full_name="Admin Local",
        hashed_password=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(user); db.commit(); db.refresh(user)
    return user
