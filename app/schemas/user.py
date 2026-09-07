from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email_or_username: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class UserProfileOut(UserOut):
    active_alerts_count: int = 0
    unread_notifications_count: int = 0
