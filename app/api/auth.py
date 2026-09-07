from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.alert import PriceAlert
from app.models.notification import Notification
from app.schemas.user import UserRegister, UserLogin, TokenOut, UserProfileOut, UserOut
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_user_optional
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenOut)
async def register(
    data: UserRegister,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    email_clean = data.email.strip().lower()
    username_clean = data.username.strip()

    # Check if email exists
    email_check = await db.execute(select(User).where(User.email == email_clean))
    if email_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered."
        )

    # Check if username exists
    user_check = await db.execute(select(User).where(User.username == username_clean))
    if user_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken."
        )

    user = User(
        email=email_clean,
        username=username_clean,
        hashed_password=hash_password(data.password),
        full_name=data.full_name or username_clean
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Link any previous guest alerts matching this email to this user
    await db.execute(
        select(PriceAlert).where(PriceAlert.email == email_clean)
    )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    # Set cookie for browser session
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600 * 72,
        samesite="lax"
    )

    return TokenOut(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.post("/login", response_model=TokenOut)
async def login(
    data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    login_id = data.email_or_username.strip().lower()
    
    res = await db.execute(
        select(User).where(
            (func.lower(User.email) == login_id) | 
            (func.lower(User.username) == login_id)
        )
    )
    user = res.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password."
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=3600 * 72,
        samesite="lax"
    )

    return TokenOut(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user)
    )

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserProfileOut)
async def get_my_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Count active alerts
    alerts_count = (await db.execute(
        select(func.count(PriceAlert.id)).where(
            (PriceAlert.user_id == user.id) | (PriceAlert.email == user.email),
            PriceAlert.is_active == True
        )
    )).scalar() or 0

    # Count unread notifications
    notif_count = (await db.execute(
        select(func.count(Notification.id)).where(
            (Notification.user_id == user.id) | (Notification.email == user.email),
            Notification.is_read == False
        )
    )).scalar() or 0

    return UserProfileOut(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        active_alerts_count=alerts_count,
        unread_notifications_count=notif_count
    )
