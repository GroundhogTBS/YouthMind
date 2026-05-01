from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import json
import uuid
import hashlib
import jwt
from datetime import datetime, timedelta

from models.database import get_db, init_db, UserModel, SessionModel, MessageModel, AssessmentModel, EmotionRecordModel
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

init_db()


class LoginRequest(BaseModel):
    phone: str
    code: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    nickname: Optional[str] = None
    signature: Optional[str] = None
    age_group: Optional[str] = None
    avatar: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    phone: str
    nickname: Optional[str]
    avatar: Optional[str]
    signature: Optional[str]
    age_group: Optional[str]
    user_type: Optional[str] = None
    created_at: str


class UserStatsResponse(BaseModel):
    chat_days: int
    assessments: int
    emotion_records: int


def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserModel:
    if not credentials:
        raise HTTPException(status_code=401, detail="未登录")
    
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="登录已过期")
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return user


@router.post("/login", summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    if not request.phone or len(request.phone) != 11:
        raise HTTPException(status_code=400, detail="请输入正确的手机号")
    
    user = db.query(UserModel).filter(UserModel.phone == request.phone).first()
    
    if not user:
        user = UserModel(
            id=str(uuid.uuid4()),
            phone=request.phone,
            nickname=f"用户{request.phone[-4:]}",
            created_at=datetime.now()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    user.last_login_at = datetime.now()
    db.commit()
    
    token = create_token(user.id)
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "signature": user.signature,
            "age_group": user.age_group,
            "created_at": user.created_at.isoformat()
        }
    }


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(user: UserModel = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        phone=user.phone,
        nickname=user.nickname,
        avatar=user.avatar,
        signature=user.signature,
        age_group=user.age_group,
        user_type=getattr(user, 'user_type', None),
        created_at=user.created_at.isoformat()
    )


@router.put("/profile", summary="更新用户资料")
async def update_profile(
    request: UpdateProfileRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.nickname is not None:
        user.nickname = request.nickname
    if request.signature is not None:
        user.signature = request.signature
    if request.age_group is not None:
        user.age_group = request.age_group
    if request.avatar is not None:
        user.avatar = request.avatar
    
    user.updated_at = datetime.now()
    db.commit()
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "signature": user.signature,
            "age_group": user.age_group
        }
    }


@router.get("/stats", response_model=UserStatsResponse, summary="获取用户统计数据")
async def get_user_stats(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    unique_dates = db.query(func.date(MessageModel.created_at)).join(
        SessionModel, MessageModel.session_id == SessionModel.id
    ).filter(
        SessionModel.user_id == user.id
    ).distinct().count()
    
    assessments = db.query(AssessmentModel).filter(
        AssessmentModel.user_id == user.id
    ).count()
    
    emotion_records = db.query(EmotionRecordModel).filter(
        EmotionRecordModel.user_id == user.id
    ).count()
    
    return UserStatsResponse(
        chat_days=unique_dates,
        assessments=assessments,
        emotion_records=emotion_records
    )


@router.post("/logout", summary="退出登录")
async def logout(user: UserModel = Depends(get_current_user)):
    return {"success": True}
