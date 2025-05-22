from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.config import settings
from app.utilities.auth_utils import ALGORITHM
from app.utilities.db import get_db

from app.utilities.static_values import INVALID_TOKEN, TOKEN_EXPIRED, USER_NOT_FOUND

security = HTTPBearer()


def fetch_user_from_db(username: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def create_access_token(username: str) -> str:
    """Generate a new JWT access token for the given username."""
    expires_at = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": username, "exp": expires_at},
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )

def validate_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Validate the access token and return the username.
    """
    token = credentials.credentials
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
        username: str = payload["sub"]
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=TOKEN_EXPIRED
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN
        )
