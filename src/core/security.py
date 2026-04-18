import base64
import hashlib
import hmac
import logging

from jose import JWTError, jwt
from fastapi import Cookie, HTTPException, Request, Depends
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.session import get_db
from src.models.user import User

logger = logging.getLogger(__name__)


def get_secret_hash(email: str) -> str:
    """
    Cognito requires a SECRET_HASH when a client secret is configured.
    HMAC-SHA256 of (email + client_id) signed with client_secret.
    """
    message = email + settings.COGNITO_CLIENT_ID
    secret = settings.COGNITO_CLIENT_SECRET.encode("utf-8")
    digest = hmac.new(
        secret,
        message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


def get_current_user(
    request: Request,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    """
    FastAPI dependency — reads access_token cookie,
    decodes the Cognito JWT, returns the user object.
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated. No access token found.")

    try:
        # Decode without verification for claims extraction
        claims = jwt.get_unverified_claims(access_token)
        
        # Get cognito_sub from token
        cognito_sub = claims.get("sub")
        username = claims.get("username")
        email_from_token = claims.get("email")
        
        if not cognito_sub:
            logger.error("No sub claim in token")
            raise HTTPException(status_code=401, detail="Invalid token: missing sub claim")
        
        # Find user by cognito_sub in database
        user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
        
        # If not found by cognito_sub, try by email
        if not user and email_from_token:
            user = db.query(User).filter(User.email == email_from_token).first()
            if user:
                logger.info(f"Found user by email: {email_from_token}, updating cognito_sub")
                user.cognito_sub = cognito_sub
                db.commit()
        
        # If still not found, try by username if it looks like email
        if not user and username and "@" in username:
            user = db.query(User).filter(User.email == username).first()
            if user:
                logger.info(f"Found user by username email: {username}, updating cognito_sub")
                user.cognito_sub = cognito_sub
                db.commit()
        
        if not user:
            logger.error(f"No user found for cognito_sub: {cognito_sub}")
            raise HTTPException(status_code=401, detail="User not found in database. Please sign up first.")
        
        logger.info(f"Authenticated user: {user.email} (ID: {user.id})")
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "cognito_sub": user.cognito_sub,
            "sub": cognito_sub,
            "username": username
        }
        
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")