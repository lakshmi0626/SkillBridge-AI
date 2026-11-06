from datetime import datetime, timedelta, timezone
import jwt
from jwt import InvalidTokenError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

pwd = PasswordHasher()
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
def hash_password(value: str) -> str: return pwd.hash(value)
def verify_password(value: str, hashed: str) -> bool:
    try: return pwd.verify(hashed, value)
    except (VerifyMismatchError, InvalidHashError): return False
def create_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({"sub": str(user_id), "exp": exp}, settings.secret_key, algorithm="HS256")
def current_user(token: str = Depends(oauth2), db: Session = Depends(get_db)) -> User:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"})
    try: uid = int(jwt.decode(token, settings.secret_key, algorithms=["HS256"]).get("sub"))
    except (InvalidTokenError, TypeError, ValueError): raise error
    user = db.get(User, uid)
    if not user or not user.is_active: raise error
    return user
def admin_user(user: User = Depends(current_user)) -> User:
    if user.role != "admin": raise HTTPException(403, "Administrator access required")
    return user
