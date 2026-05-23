from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models import User
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import TokenResponse, TokenRefreshRequest, UserInfo, UserCreate, UserResponse
from app.middleware.rate_limiter import limiter
from app.security import hash_password, verify_password
from app.audit.logger import log_login_success, log_login_failed
from app.audit.detector import check_brute_force, check_off_hours_access

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Користувач '{user_data.username}' вже існує"
        )

    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user_data.email}' вже зареєстровано"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, username: str, password: str, db: Session = Depends(get_db)):

    ip = request.client.host

    if check_brute_force(db, ip):
        log_login_failed(db, username, ip, "brute_force_blocked")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Забагато невдалих спроб. Спробуйте пізніше."
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        log_login_failed(db, username, ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль",
        )

    if not verify_password(password, user.password_hash):
        log_login_failed(db, username, ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірний логін або пароль",
        )

    from datetime import datetime, timezone
    check_off_hours_access(
        db,
        user.id,
        user.username,
        ip,
        datetime.now(timezone.utc).hour
    )

    log_login_success(db, user.id, user.username, ip)

    role = user.roles[0].name if user.roles else "student"
    access_token = create_access_token(user.id, role)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )



@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("5/minute")
def refresh_token(request: Request, body: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = verify_token(body.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідний refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Потрібен refresh token, а не access token",
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    role = user.roles[0].name if user.roles else "student"
    new_access = create_access_token(user_id, role)
    new_refresh = create_refresh_token(user_id)

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    role = current_user.roles[0].name if current_user.roles else "student"
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=role,
    )