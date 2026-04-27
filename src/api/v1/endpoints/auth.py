import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
import logging

from src.core.config import settings
from src.core.security import get_current_user, get_secret_hash
from src.db.session import get_db
from src.models.user import User
from src.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    ConfirmForgotPasswordRequest,
    ConfirmForgotPasswordResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MeResponse,
    RefreshResponse,
    SignupRequest,
    SignupResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Cognito client — one instance shared across all requests
cognito_client = boto3.client(
    "cognito-idp",
    region_name=settings.AWS_REGION,
)


# ── SIGNUP ────────────────────────────────────────────────────────────────────
@router.post("/signup", response_model=SignupResponse, status_code=201)
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    Creates the user in Cognito, then saves to PostgreSQL.
    Cognito will send a 6-digit verification code to the email.
    """
    # Check local DB first — fast fail before hitting Cognito
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    try:
        cognito_response = cognito_client.sign_up(
            ClientId=settings.COGNITO_CLIENT_ID,
            Username=data.email,
            Password=data.password,
            SecretHash=get_secret_hash(data.email),
            UserAttributes=[
                {"Name": "email", "Value": data.email},
                {"Name": "name", "Value": data.name},
            ],
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]

        print(f"COGNITO SIGNUP ERROR >>> {error_code}: {error_msg}", flush=True)

        error_messages = {
            "UsernameExistsException": "An account with this email already exists.",
            "InvalidPasswordException": f"Password does not meet requirements: {error_msg}",
            "InvalidParameterException": f"Invalid input: {error_msg}",
            "LimitExceededException": "Too many signup attempts. Please try again later.",
            "TooManyRequestsException": "Too many requests. Please wait and try again.",
        }

        detail = error_messages.get(error_code, f"Signup failed: {error_msg}")
        status = 400
        raise HTTPException(status_code=status, detail=detail)

    cognito_sub = cognito_response.get("UserSub")
    if not cognito_sub:
        raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

    # Save to local DB
    try:
        new_user = User(
            name=data.name,
            email=data.email,
            cognito_sub=cognito_sub,
            is_verified=False,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        print(f"LOCAL DB SAVE ERROR >>> {e}", flush=True)
        db.rollback()
        # Don't fail — user is created in Cognito, DB save is secondary

    return SignupResponse(
        message="Signup successful! Please check your email for your 6-digit verification code.",
        email=data.email,
    )
    
    
# ── VERIFY EMAIL ──────────────────────────────────────────────────────────────
@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """
    Confirm the account using the 6-digit code Cognito sent to the email.
    """
    try:
        cognito_client.confirm_sign_up(
            ClientId=settings.COGNITO_CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.code,
            SecretHash=get_secret_hash(data.email),
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        
        error_messages = {
            "CodeMismatchException": "Invalid verification code. Please check and try again.",
            "ExpiredCodeException": "Verification code has expired. Please request a new code.",
            "NotAuthorizedException": "Account already verified. You can log in now.",
            "UserNotFoundException": "No account found with this email address.",
            "LimitExceededException": "Too many verification attempts. Please try again later.",
        }
        
        if error_code in error_messages:
            raise HTTPException(status_code=400, detail=error_messages[error_code])
        
        logger.error(f"Cognito verification error: {error_code} - {error_msg}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {error_msg}")

    # Update local DB if user exists
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if user:
            user.is_verified = True
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update user verification status: {e}")

    return VerifyEmailResponse(
        message="Email verified successfully! You can now log in to your account."
    )


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Login with email and password directly to Cognito.
    """
    try:
        cognito_response = cognito_client.initiate_auth(
            ClientId=settings.COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": data.email,
                "PASSWORD": data.password,
                "SECRET_HASH": get_secret_hash(data.email),
            },
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        
        error_messages = {
            "NotAuthorizedException": "Incorrect email or password. Please check your credentials.",
            "UserNotFoundException": "No account found with this email address. Please sign up first.",
            "UserNotConfirmedException": "Please verify your email address before logging in. Check your inbox for the verification code.",
            "PasswordResetRequiredException": "Password reset required. Please use the forgot password option.",
            "TooManyRequestsException": "Too many login attempts. Please wait a moment and try again.",
        }
        
        if error_code in error_messages:
            raise HTTPException(status_code=401 if error_code == "NotAuthorizedException" else 403, 
                              detail=error_messages[error_code])
        
        logger.error(f"Cognito login error: {error_code} - {error_msg}")
        raise HTTPException(status_code=500, detail=f"Login failed: {error_msg}")

    auth_result = cognito_response.get("AuthenticationResult")
    if not auth_result:
        raise HTTPException(status_code=500, detail="Authentication failed. Please try again.")

    access_token = auth_result.get("AccessToken")
    refresh_token = auth_result.get("RefreshToken")
    
    # CRITICAL FIX: Always get user info from Cognito and ensure local DB has the user
    cognito_sub = None
    user_name = data.email.split('@')[0]
    user_email = data.email
    is_verified = False
    db_user = None
    
    try:
        user_info = cognito_client.get_user(AccessToken=access_token)
        
        for attr in user_info.get("UserAttributes", []):
            if attr["Name"] == "sub":
                cognito_sub = attr["Value"]
            elif attr["Name"] == "name":
                user_name = attr["Value"]
            elif attr["Name"] == "email":
                user_email = attr["Value"]
            elif attr["Name"] == "email_verified":
                is_verified = attr["Value"] == "true"
        
        print(f"User info from Cognito: sub={cognito_sub}, name={user_name}, email={user_email}", flush=True)
        
        # ALWAYS create or update user in local DB
        # First try to find by cognito_sub
        if cognito_sub:
            db_user = db.query(User).filter(User.cognito_sub == cognito_sub).first()
        
        # If not found by sub, try by email
        if not db_user:
            db_user = db.query(User).filter(User.email == user_email).first()
        
        if db_user:
            # Update existing user
            db_user.name = user_name
            db_user.email = user_email
            db_user.is_verified = is_verified
            if cognito_sub and not db_user.cognito_sub:
                db_user.cognito_sub = cognito_sub
            print(f"Updated existing user in local DB: {user_email} (ID: {db_user.id})", flush=True)
        else:
            # Create new user
            db_user = User(
                name=user_name,
                email=user_email,
                cognito_sub=cognito_sub,
                is_verified=is_verified,
            )
            db.add(db_user)
            print(f"Created NEW user in local DB: {user_email}", flush=True)
        
        db.commit()
        db.refresh(db_user)
        
    except Exception as e:
        print(f"ERROR syncing user with local DB: {e}", flush=True)
        db.rollback()
        # If DB fails, we still continue - user can still use the app
        # but organizations endpoints will fail until fixed

    # Set cookies
    is_production = not settings.DEBUG

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Must be True for HTTPS (Vercel uses HTTPS)
        samesite="none",  # Required for cross-domain cookies
        max_age=3600,
        path="/",
        domain=".vercel.app"  # Allow across all vercel.app subdomains
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=60 * 60 * 24 * 30,
        path="/",
        domain=".vercel.app"
    )
    if cognito_sub:
        response.set_cookie(
            key="user_cognito_sub",
            value=cognito_sub,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=60 * 60 * 24 * 30,
            path="/",
            domain=".vercel.app"
        )

    return LoginResponse(
        message="Login successful! Welcome back.",
        email=user_email,
        access_token=access_token,
    )

# ── REFRESH TOKEN ─────────────────────────────────────────────────────────────
@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    response: Response,
    refresh_token: str = Cookie(None),
    user_cognito_sub: str = Cookie(None),
):
    """
    Use the refresh_token cookie to get a new access_token.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=401, 
            detail="No refresh token found. Please log in again."
        )
    
    if not user_cognito_sub:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again."
        )

    try:
        cognito_response = cognito_client.initiate_auth(
            ClientId=settings.COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_token,
                "SECRET_HASH": get_secret_hash(user_cognito_sub),
            },
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        
        error_messages = {
            "NotAuthorizedException": "Invalid or expired refresh token. Please log in again.",
            "InvalidParameterException": "Invalid refresh token. Please log in again.",
            "ExpiredCodeException": "Refresh token has expired. Please log in again.",
        }
        
        if error_code in error_messages:
            raise HTTPException(status_code=401, detail=error_messages[error_code])
        
        logger.error(f"Token refresh error: {error_code} - {error_msg}")
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {error_msg}")

    auth_result = cognito_response.get("AuthenticationResult")
    if not auth_result:
        raise HTTPException(status_code=500, detail="Failed to refresh token.")

    is_production = not settings.DEBUG

    response.set_cookie(
        key="access_token",
        value=auth_result.get("AccessToken"),
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=3600,
        path="/",
    )

    return RefreshResponse(
        message="Token refreshed successfully."
    )


# ── CHANGE PASSWORD ───────────────────────────────────────────────────────────
@router.post("/change-password", response_model=ChangePasswordResponse)
def change_password(
    data: ChangePasswordRequest,
    access_token: str = Cookie(None),
):
    """
    Change password for a logged-in user.
    """
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please log in first."
        )

    try:
        cognito_client.change_password(
            AccessToken=access_token,
            PreviousPassword=data.old_password,
            ProposedPassword=data.new_password,
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        
        error_messages = {
            "NotAuthorizedException": "Current password is incorrect. Please check and try again.",
            "InvalidPasswordException": f"New password requirements not met: {error_msg}",
            "LimitExceededException": "Too many password change attempts. Please try again later.",
            "PasswordResetRequiredException": "Password reset required. Use the forgot password option.",
        }
        
        if error_code in error_messages:
            raise HTTPException(
                status_code=401 if error_code == "NotAuthorizedException" else 400,
                detail=error_messages[error_code]
            )
        
        logger.error(f"Password change error: {error_code} - {error_msg}")
        raise HTTPException(status_code=500, detail=f"Password change failed: {error_msg}")

    return ChangePasswordResponse(
        message="Password changed successfully. Please use your new password for future logins."
    )


# ── FORGOT PASSWORD ───────────────────────────────────────────────────────────
@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(data: ForgotPasswordRequest):
    """
    Sends a password reset code to the user's email via Cognito.
    """
    try:
        cognito_client.forgot_password(
            ClientId=settings.COGNITO_CLIENT_ID,
            Username=data.email,
            SecretHash=get_secret_hash(data.email),
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        
        error_messages = {
            "UserNotFoundException": "If an account exists with this email, a password reset code will be sent.",
            "LimitExceededException": "Too many password reset attempts. Please try again later.",
            "TooManyRequestsException": "Too many requests. Please wait a moment and try again.",
        }
        
        # Don't reveal if user exists for security, but still provide friendly message
        if error_code == "UserNotFoundException":
            # Return success anyway for security
            return ForgotPasswordResponse(
                message="If an account exists with this email, you will receive a password reset code shortly."
            )
        
        if error_code in error_messages:
            raise HTTPException(status_code=400, detail=error_messages[error_code])
        
        logger.error(f"Forgot password error: {error_code} - {error_msg}")
        raise HTTPException(status_code=500, detail=f"Password reset request failed: {error_msg}")

    return ForgotPasswordResponse(
        message="Password reset code has been sent to your email. Please check your inbox."
    )


# ── CONFIRM FORGOT PASSWORD ───────────────────────────────────────────────────
@router.post("/confirm-forgot-password", response_model=ConfirmForgotPasswordResponse)
def confirm_forgot_password(data: ConfirmForgotPasswordRequest):
    """
    Reset the password using the code sent to email.
    """
    try:
        cognito_client.confirm_forgot_password(
            ClientId=settings.COGNITO_CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.code,
            Password=data.new_password,
            SecretHash=get_secret_hash(data.email),
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        error_msg = e.response["Error"]["Message"]
        
        error_messages = {
            "CodeMismatchException": "Invalid reset code. Please check and try again.",
            "ExpiredCodeException": "Reset code has expired. Please request a new password reset code.",
            "InvalidPasswordException": f"Password requirements not met: {error_msg}",
            "UserNotFoundException": "No account found with this email address.",
            "LimitExceededException": "Too many reset attempts. Please try again later.",
        }
        
        if error_code in error_messages:
            raise HTTPException(status_code=400, detail=error_messages[error_code])
        
        logger.error(f"Confirm forgot password error: {error_code} - {error_msg}")
        raise HTTPException(status_code=500, detail=f"Password reset failed: {error_msg}")

    return ConfirmForgotPasswordResponse(
        message="Password reset successful! You can now log in with your new password."
    )


# ── LOGOUT ────────────────────────────────────────────────────────────────────
@router.post("/logout")
def logout(response: Response):
    """
    Clears all auth cookies from the browser.
    """
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    response.delete_cookie("user_cognito_sub", path="/")
    return {"message": "Logged out successfully. See you next time!"}

@router.get("/me", response_model=MeResponse)
def me(
    request: Request,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user),
):
    """
    Returns the currently logged-in user's profile from Cognito.
    """
    email = claims.get("email") or claims.get("username")
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token. Please log in again."
        )

    # Get user details from Cognito to ensure we have latest data
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No access token found. Please log in again."
        )
    
    try:
        cognito_user = cognito_client.get_user(AccessToken=access_token)
        
        # Extract user attributes
        user_data = {
            "email": email,
            "name": email.split('@')[0],
            "cognito_sub": None,
            "is_verified": False,
        }
        
        for attr in cognito_user.get("UserAttributes", []):
            if attr["Name"] == "name":
                user_data["name"] = attr["Value"]
            elif attr["Name"] == "email":
                user_data["email"] = attr["Value"]
            elif attr["Name"] == "sub":
                user_data["cognito_sub"] = attr["Value"]
            elif attr["Name"] == "email_verified":
                user_data["is_verified"] = attr["Value"] == "true"
        
        # Find or create user in local DB - SAFER VERSION
        user = None
        
        # Try to find by email first
        if user_data["email"]:
            user = db.query(User).filter(User.email == user_data["email"]).first()
        
        # If not found by email, try by cognito_sub
        if not user and user_data["cognito_sub"]:
            user = db.query(User).filter(User.cognito_sub == user_data["cognito_sub"]).first()
        
        if not user:
            # Create new user
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                cognito_sub=user_data["cognito_sub"],
                is_verified=user_data["is_verified"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user in /me endpoint: {user_data['email']}", flush=True)
        else:
            # Update existing user
            user.name = user_data["name"]
            user.is_verified = user_data["is_verified"]
            if user_data["cognito_sub"] and not user.cognito_sub:
                user.cognito_sub = user_data["cognito_sub"]
            db.commit()
            db.refresh(user)
        
        return MeResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            is_verified=user.is_verified,
        )
        
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NotAuthorizedException":
            raise HTTPException(
                status_code=401,
                detail="Session expired or invalid. Please log in again."
            )
        
        print(f"Cognito error in /me: {e}", flush=True)
        
        # Fallback to local DB
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found. Please log in again."
            )
        
        return MeResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            is_verified=user.is_verified,
        )