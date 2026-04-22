from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
 
from app.database import get_db
from app.models import User
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.auth.dependencies import get_current_user
from app.schemas import TokenResponse, TokenRefreshRequest, UserInfo
 
# Імпортуйте вашу функцію перевірки пароля з практичної №4
from app.security import verify_password
 
router = APIRouter(prefix="/auth", tags=["Authentication"])
 
 
# POST /auth/login — залишаємо з практичної №4, але тепер повертаємо токени
@router.post("/login", response_model=TokenResponse)
def login(username: str, password: str, db: Session = Depends(get_db)):
	# 1. Знаходимо користувача
	user = db.query(User).filter(User.username == username).first()
	if not user:
    	raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Невірний логін або пароль",
    	)
 
	# 2. Перевіряємо пароль (bcrypt з практичної №4)
	if not verify_password(password, user.password_hash):
    	raise HTTPException(
        	status_code=status.HTTP_401_UNAUTHORIZED,
        	detail="Невірний логін або пароль",
    	)
 
	# 3. Визначаємо роль (перша роль користувача)
	role = user.roles[0].name if user.roles else "student"
 
	# 4. Генеруємо токени
	access_token = create_access_token(user.id, role)
	refresh_token = create_refresh_token(user.id)
 
	return TokenResponse(
    	access_token=access_token,
    	refresh_token=refresh_token,
	)
