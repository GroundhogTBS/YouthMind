from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta

from models.database import get_db, init_db, EmotionRecordModel
from routers.user import get_current_user, UserModel

logger = logging.getLogger(__name__)
router = APIRouter()

init_db()


class EmotionRecordRequest(BaseModel):
    emotionType: str
    intensity: int
    triggers: Optional[str] = None
    thoughts: Optional[str] = None
    copingMethods: Optional[str] = None


class EmotionRecordResponse(BaseModel):
    id: int
    emotionType: str
    intensity: int
    triggers: Optional[str]
    thoughts: Optional[str]
    copingMethods: Optional[str]
    recordedAt: str


class EmotionTrendResponse(BaseModel):
    emotion_type: str
    count: int
    avg_intensity: float


@router.post("", summary="创建情绪记录")
async def create_record(
    request: EmotionRecordRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = EmotionRecordModel(
        user_id=user.id,
        emotion_type=request.emotionType,
        intensity=request.intensity,
        triggers=request.triggers,
        thoughts=request.thoughts,
        coping_methods=request.copingMethods,
        created_at=datetime.now()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {
        "id": record.id,
        "emotionType": record.emotion_type,
        "intensity": record.intensity,
        "triggers": record.triggers,
        "thoughts": record.thoughts,
        "copingMethods": record.coping_methods,
        "recordedAt": record.created_at.isoformat()
    }


@router.get("/recent", response_model=List[EmotionRecordResponse], summary="获取最近情绪记录")
async def get_recent_records(
    limit: int = 10,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = db.query(EmotionRecordModel).filter(
        EmotionRecordModel.user_id == user.id
    ).order_by(EmotionRecordModel.created_at.desc()).limit(limit).all()
    
    return [
        EmotionRecordResponse(
            id=r.id,
            emotionType=r.emotion_type,
            intensity=r.intensity,
            triggers=r.triggers,
            thoughts=r.thoughts,
            copingMethods=r.coping_methods,
            recordedAt=r.created_at.isoformat()
        )
        for r in records
    ]


@router.get("/trend", response_model=List[EmotionTrendResponse], summary="获取情绪趋势")
async def get_emotion_trend(
    days: int = 7,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    start_date = datetime.now() - timedelta(days=days)
    
    from sqlalchemy import func
    
    results = db.query(
        EmotionRecordModel.emotion_type,
        func.count(EmotionRecordModel.id).label('count'),
        func.avg(EmotionRecordModel.intensity).label('avg_intensity')
    ).filter(
        EmotionRecordModel.user_id == user.id,
        EmotionRecordModel.created_at >= start_date
    ).group_by(
        EmotionRecordModel.emotion_type
    ).all()
    
    return [
        EmotionTrendResponse(
            emotion_type=r.emotion_type,
            count=r.count,
            avg_intensity=round(r.avg_intensity, 1)
        )
        for r in results
    ]


@router.get("/{record_id}", summary="获取单条情绪记录")
async def get_record(
    record_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(EmotionRecordModel).filter(
        EmotionRecordModel.id == record_id,
        EmotionRecordModel.user_id == user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return {
        "id": record.id,
        "emotionType": record.emotion_type,
        "intensity": record.intensity,
        "triggers": record.triggers,
        "thoughts": record.thoughts,
        "copingMethods": record.coping_methods,
        "recordedAt": record.created_at.isoformat()
    }
