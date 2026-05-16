import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-set-env-var")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    import models

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Sprint 4 — Role-based access control per proposal Section 3.2 NFRs.
# Role hierarchy: admin > staff > viewer.
# "user" is the legacy DB default — treat it as staff for back-compat with
# any rows created before the role column existed.
ROLE_RANK = {"viewer": 1, "user": 2, "staff": 2, "admin": 3}


def require_role(min_role: str):
    """FastAPI dependency factory enforcing a minimum role."""
    min_rank = ROLE_RANK[min_role]

    def dep(current_user=Depends(get_current_user)):
        user_role = (current_user.role or "staff").lower()
        if ROLE_RANK.get(user_role, 0) < min_rank:
            raise HTTPException(
                status_code=403,
                detail=f"Requires role '{min_role}' or higher. Your role: '{user_role}'.",
            )
        return current_user

    return dep
