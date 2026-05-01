from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from models.database import get_db, init_db, DiaryModel
from routers.user import get_current_user, UserModel

logger = logging.getLogger(__name__)
router = APIRouter()

init_db()


class DiaryCreateRequest(BaseModel):
    title: Optional[str] = None
    content: str
    mood: Optional[str] = None
    weather: Optional[str] = None


class DiaryUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    weather: Optional[str] = None


class DiaryResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    mood: Optional[str]
    weather: Optional[str]
    createdAt: str
    updatedAt: str


@router.post("", response_model=DiaryResponse, summary="创建日记")
async def create_diary(
    request: DiaryCreateRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diary = DiaryModel(
        user_id=user.id,
        title=request.title,
        content=request.content,
        mood=request.mood,
        weather=request.weather,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    
    return DiaryResponse(
        id=diary.id,
        title=diary.title,
        content=diary.content,
        mood=diary.mood,
        weather=diary.weather,
        createdAt=diary.created_at.isoformat(),
        updatedAt=diary.updated_at.isoformat()
    )


@router.get("", response_model=List[DiaryResponse], summary="获取日记列表")
async def get_diaries(
    limit: int = 20,
    offset: int = 0,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diaries = db.query(DiaryModel).filter(
        DiaryModel.user_id == user.id
    ).order_by(DiaryModel.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        DiaryResponse(
            id=d.id,
            title=d.title,
            content=d.content,
            mood=d.mood,
            weather=d.weather,
            createdAt=d.created_at.isoformat(),
            updatedAt=d.updated_at.isoformat()
        )
        for d in diaries
    ]


@router.get("/{diary_id}", response_model=DiaryResponse, summary="获取日记详情")
async def get_diary(
    diary_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diary = db.query(DiaryModel).filter(
        DiaryModel.id == diary_id,
        DiaryModel.user_id == user.id
    ).first()
    
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    return DiaryResponse(
        id=diary.id,
        title=diary.title,
        content=diary.content,
        mood=diary.mood,
        weather=diary.weather,
        createdAt=diary.created_at.isoformat(),
        updatedAt=diary.updated_at.isoformat()
    )


@router.put("/{diary_id}", response_model=DiaryResponse, summary="更新日记")
async def update_diary(
    diary_id: int,
    request: DiaryUpdateRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diary = db.query(DiaryModel).filter(
        DiaryModel.id == diary_id,
        DiaryModel.user_id == user.id
    ).first()
    
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    if request.title is not None:
        diary.title = request.title
    if request.content is not None:
        diary.content = request.content
    if request.mood is not None:
        diary.mood = request.mood
    if request.weather is not None:
        diary.weather = request.weather
    
    diary.updated_at = datetime.now()
    db.commit()
    db.refresh(diary)
    
    return DiaryResponse(
        id=diary.id,
        title=diary.title,
        content=diary.content,
        mood=diary.mood,
        weather=diary.weather,
        createdAt=diary.created_at.isoformat(),
        updatedAt=diary.updated_at.isoformat()
    )


@router.delete("/{diary_id}", summary="删除日记")
async def delete_diary(
    diary_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    diary = db.query(DiaryModel).filter(
        DiaryModel.id == diary_id,
        DiaryModel.user_id == user.id
    ).first()
    
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    db.delete(diary)
    db.commit()
    
    return {"success": True, "message": "日记已删除"}


@router.get("/stats/summary", summary="获取日记统计")
async def get_diary_stats(
    days: int = 30,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    start_date = datetime.now() - timedelta(days=days)
    
    total = db.query(DiaryModel).filter(
        DiaryModel.user_id == user.id,
        DiaryModel.created_at >= start_date
    ).count()
    
    return {
        "period_days": days,
        "total_diaries": total
    }
