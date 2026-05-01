from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import json

from models.database import (
    get_db, UserModel, SessionModel, MessageModel,
    CrisisEventModel, EmotionRecordModel, AssessmentModel, ArticleModel,
    OperationLogModel
)
from routers.user import get_current_user, UserModel as UserSchema
from services.operation_log import operation_log_service

logger = logging.getLogger(__name__)
router = APIRouter()


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    total_sessions: int
    total_messages: int
    total_assessments: int
    total_emotion_records: int
    crisis_events_count: int
    unhandled_crisis: int
    new_users_today: int
    new_users_week: int
    messages_today: int
    messages_week: int


class DashboardResponse(BaseModel):
    stats: AdminStatsResponse
    user_growth: List[Dict[str, Any]]
    message_trend: List[Dict[str, Any]]
    emotion_distribution: Dict[str, int]
    crisis_trend: List[Dict[str, Any]]
    assessment_distribution: Dict[str, int]
    top_users: List[Dict[str, Any]]


class UserDetailResponse(BaseModel):
    id: str
    phone: str
    nickname: str
    age_group: str
    session_count: int
    message_count: int
    assessment_count: int
    emotion_record_count: int
    last_active: str
    created_at: str
    risk_level: str


class CrisisEventResponse(BaseModel):
    id: int
    user_id: str
    session_id: str
    risk_level: str
    risk_score: int
    matched_keywords: str
    handled: int
    handler_id: Optional[str]
    handled_at: Optional[str]
    notes: Optional[str]
    created_at: str


class CrisisHandleRequest(BaseModel):
    notes: Optional[str] = None


class OperationLogResponse(BaseModel):
    id: int
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Optional[Dict[str, Any]]
    ip_address: str
    user_agent: str
    created_at: str


async def require_admin(user: UserSchema = Depends(get_current_user)):
    if user.phone not in ["admin", "13800138000"]:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


@router.get("/dashboard", response_model=DashboardResponse, summary="管理后台仪表盘")
async def get_dashboard(
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_users = db.query(func.count(UserModel.id)).scalar() or 0
    
    new_users_today = db.query(func.count(UserModel.id)).filter(
        UserModel.created_at >= today
    ).scalar() or 0
    
    new_users_week = db.query(func.count(UserModel.id)).filter(
        UserModel.created_at >= week_ago
    ).scalar() or 0

    active_today = db.query(func.count(func.distinct(MessageModel.session_id))).join(
        SessionModel, MessageModel.session_id == SessionModel.id
    ).filter(MessageModel.created_at >= today).scalar() or 0
    
    active_week = db.query(func.count(func.distinct(SessionModel.user_id))).filter(
        SessionModel.updated_at >= week_ago
    ).scalar() or 0
    
    active_month = db.query(func.count(func.distinct(SessionModel.user_id))).filter(
        SessionModel.updated_at >= month_ago
    ).scalar() or 0

    total_sessions = db.query(func.count(SessionModel.id)).scalar() or 0
    total_messages = db.query(func.count(MessageModel.id)).scalar() or 0
    total_assessments = db.query(func.count(AssessmentModel.id)).scalar() or 0
    total_emotion = db.query(func.count(EmotionRecordModel.id)).scalar() or 0
    
    messages_today = db.query(func.count(MessageModel.id)).filter(
        MessageModel.created_at >= today
    ).scalar() or 0
    
    messages_week = db.query(func.count(MessageModel.id)).filter(
        MessageModel.created_at >= week_ago
    ).scalar() or 0

    crisis_count = db.query(func.count(CrisisEventModel.id)).scalar() or 0
    unhandled = db.query(func.count(CrisisEventModel.id)).filter(
        CrisisEventModel.handled == 0
    ).scalar() or 0

    user_growth = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        next_day = day + timedelta(days=1)
        count = db.query(func.count(UserModel.id)).filter(
            UserModel.created_at >= day,
            UserModel.created_at < next_day
        ).scalar() or 0
        user_growth.append({
            "date": day.strftime('%Y-%m-%d'),
            "count": count
        })

    message_trend = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        next_day = day + timedelta(days=1)
        count = db.query(func.count(MessageModel.id)).filter(
            MessageModel.created_at >= day,
            MessageModel.created_at < next_day
        ).scalar() or 0
        message_trend.append({
            "date": day.strftime('%Y-%m-%d'),
            "count": count
        })

    emotion_records = db.query(EmotionRecordModel).filter(
        EmotionRecordModel.created_at >= week_ago
    ).all()
    emotion_distribution = {}
    for r in emotion_records:
        et = r.emotion_type or 'neutral'
        emotion_distribution[et] = emotion_distribution.get(et, 0) + 1

    crisis_trend = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        next_day = day + timedelta(days=1)
        count = db.query(func.count(CrisisEventModel.id)).filter(
            CrisisEventModel.created_at >= day,
            CrisisEventModel.created_at < next_day
        ).scalar() or 0
        crisis_trend.append({
            "date": day.strftime('%Y-%m-%d'),
            "count": count
        })

    assessments = db.query(AssessmentModel).all()
    assessment_distribution = {}
    for a in assessments:
        st = a.scale_type or 'unknown'
        assessment_distribution[st] = assessment_distribution.get(st, 0) + 1

    top_users_query = db.query(
        SessionModel.user_id,
        func.count(SessionModel.id).label('session_count')
    ).group_by(SessionModel.user_id).order_by(desc('session_count')).limit(5).all()
    
    top_users = []
    for u in top_users_query:
        user = db.query(UserModel).filter(UserModel.id == u.user_id).first()
        if user:
            top_users.append({
                "id": user.id,
                "nickname": user.nickname or '未设置',
                "session_count": u.session_count
            })

    stats = AdminStatsResponse(
        total_users=total_users,
        active_users_today=active_today,
        active_users_week=active_week,
        active_users_month=active_month,
        total_sessions=total_sessions,
        total_messages=total_messages,
        total_assessments=total_assessments,
        total_emotion_records=total_emotion,
        crisis_events_count=crisis_count,
        unhandled_crisis=unhandled,
        new_users_today=new_users_today,
        new_users_week=new_users_week,
        messages_today=messages_today,
        messages_week=messages_week
    )

    return DashboardResponse(
        stats=stats,
        user_growth=user_growth,
        message_trend=message_trend,
        emotion_distribution=emotion_distribution,
        crisis_trend=crisis_trend,
        assessment_distribution=assessment_distribution,
        top_users=top_users
    )


@router.get("/stats", response_model=AdminStatsResponse, summary="管理后台统计数据")
async def get_admin_stats(
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_users = db.query(func.count(UserModel.id)).scalar() or 0
    
    new_users_today = db.query(func.count(UserModel.id)).filter(
        UserModel.created_at >= today
    ).scalar() or 0
    
    new_users_week = db.query(func.count(UserModel.id)).filter(
        UserModel.created_at >= week_ago
    ).scalar() or 0

    active_today = db.query(func.count(func.distinct(MessageModel.session_id))).join(
        SessionModel, MessageModel.session_id == SessionModel.id
    ).filter(MessageModel.created_at >= today).scalar() or 0
    
    active_week = db.query(func.count(func.distinct(SessionModel.user_id))).filter(
        SessionModel.updated_at >= week_ago
    ).scalar() or 0
    
    active_month = db.query(func.count(func.distinct(SessionModel.user_id))).filter(
        SessionModel.updated_at >= month_ago
    ).scalar() or 0

    total_sessions = db.query(func.count(SessionModel.id)).scalar() or 0
    total_messages = db.query(func.count(MessageModel.id)).scalar() or 0
    total_assessments = db.query(func.count(AssessmentModel.id)).scalar() or 0
    total_emotion = db.query(func.count(EmotionRecordModel.id)).scalar() or 0
    
    messages_today = db.query(func.count(MessageModel.id)).filter(
        MessageModel.created_at >= today
    ).scalar() or 0
    
    messages_week = db.query(func.count(MessageModel.id)).filter(
        MessageModel.created_at >= week_ago
    ).scalar() or 0

    crisis_count = db.query(func.count(CrisisEventModel.id)).scalar() or 0
    unhandled = db.query(func.count(CrisisEventModel.id)).filter(
        CrisisEventModel.handled == 0
    ).scalar() or 0
    
    return AdminStatsResponse(
        total_users=total_users,
        active_users_today=active_today,
        active_users_week=active_week,
        active_users_month=active_month,
        total_sessions=total_sessions,
        total_messages=total_messages,
        total_assessments=total_assessments,
        total_emotion_records=total_emotion,
        crisis_events_count=crisis_count,
        unhandled_crisis=unhandled,
        new_users_today=new_users_today,
        new_users_week=new_users_week,
        messages_today=messages_today,
        messages_week=messages_week
    )


@router.get("/users", response_model=List[UserDetailResponse], summary="用户列表")
async def get_admin_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query(""),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(UserModel)
    
    if search:
        query = query.filter(
            (UserModel.phone.contains(search)) |
            (UserModel.nickname.contains(search))
        )
    
    users = query.order_by(UserModel.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    result = []
    
    for u in users:
        session_count = db.query(func.count(SessionModel.id)).filter(
            SessionModel.user_id == u.id
        ).scalar() or 0
        
        message_count = db.query(func.count(MessageModel.id)).join(
            SessionModel, MessageModel.session_id == SessionModel.id
        ).filter(SessionModel.user_id == u.id).scalar() or 0
        
        assessment_count = db.query(func.count(AssessmentModel.id)).filter(
            AssessmentModel.user_id == u.id
        ).scalar() or 0
        
        emotion_count = db.query(func.count(EmotionRecordModel.id)).filter(
            EmotionRecordModel.user_id == u.id
        ).scalar() or 0
        
        last_msg = db.query(MessageModel.created_at).join(
            SessionModel, MessageModel.session_id == SessionModel.id
        ).filter(SessionModel.user_id == u.id).order_by(
            MessageModel.created_at.desc()
        ).first()
        
        crisis_count = db.query(func.count(CrisisEventModel.id)).filter(
            CrisisEventModel.user_id == u.id
        ).scalar() or 0
        
        high_risk = db.query(func.count(CrisisEventModel.id)).filter(
            CrisisEventModel.user_id == u.id,
            CrisisEventModel.risk_level == 'red'
        ).scalar() or 0
        
        if high_risk > 0:
            risk_level = 'high'
        elif crisis_count > 0:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        result.append(UserDetailResponse(
            id=u.id,
            phone=u.phone or '',
            nickname=u.nickname or '',
            age_group=u.age_group or '',
            session_count=session_count,
            message_count=message_count,
            assessment_count=assessment_count,
            emotion_record_count=emotion_count,
            last_active=last_msg[0].isoformat() if last_msg else '',
            created_at=u.created_at.isoformat() if u.created_at else '',
            risk_level=risk_level
        ))
    
    return result


@router.get("/crisis-events", response_model=List[CrisisEventResponse], summary="危机事件列表")
async def get_crisis_events(
    status: str = Query("", description="筛选状态: unhandled/handled/all"),
    risk_level: str = Query("", description="筛选风险等级: red/orange/yellow"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(CrisisEventModel)
    
    if status == "unhandled":
        query = query.filter(CrisisEventModel.handled == 0)
    elif status == "handled":
        query = query.filter(CrisisEventModel.handled == 1)
    
    if risk_level:
        query = query.filter(CrisisEventModel.risk_level == risk_level)
    
    events = query.order_by(
        desc(CrisisEventModel.risk_score),
        desc(CrisisEventModel.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return [
        CrisisEventResponse(
            id=e.id,
            user_id=e.user_id or '',
            session_id=e.session_id,
            risk_level=e.risk_level,
            risk_score=e.risk_score or 0,
            matched_keywords=e.matched_keywords or '',
            handled=e.handled or 0,
            handler_id=getattr(e, 'handler_id', None),
            handled_at=getattr(e, 'handled_at', None),
            notes=getattr(e, 'notes', None),
            created_at=e.created_at.isoformat() if e.created_at else ''
        )
        for e in events
    ]


@router.put("/crisis-events/{event_id}/handle", summary="处理危机事件")
async def handle_crisis_event(
    event_id: int,
    request: CrisisHandleRequest,
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    event = db.query(CrisisEventModel).filter(CrisisEventModel.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="事件不存在")
    
    event.handled = 1
    if hasattr(event, 'handler_id'):
        event.handler_id = admin.id
    if hasattr(event, 'handled_at'):
        event.handled_at = datetime.now()
    if hasattr(event, 'notes') and request.notes:
        event.notes = request.notes
    
    db.commit()
    
    operation_log_service.log(
        db=db,
        user_id=admin.id,
        action=operation_log_service.ACTION_HANDLE_CRISIS,
        resource_type="crisis_event",
        resource_id=str(event_id),
        details={
            "risk_level": event.risk_level,
            "notes": request.notes
        }
    )
    
    return {"success": True, "message": "事件已标记为已处理"}


@router.get("/operation-logs", response_model=List[OperationLogResponse], summary="操作日志")
async def get_operation_logs(
    user_id: str = Query("", description="筛选用户ID"),
    action: str = Query("", description="筛选操作类型"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(OperationLogModel)
    
    if user_id:
        query = query.filter(OperationLogModel.user_id == user_id)
    if action:
        query = query.filter(OperationLogModel.action == action)
    
    logs = query.order_by(
        desc(OperationLogModel.created_at)
    ).offset((page - 1) * page_size).limit(page_size).all()
    
    return [
        OperationLogResponse(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id or '',
            details=json.loads(log.details) if log.details else None,
            ip_address=log.ip_address or '',
            user_agent=log.user_agent or '',
            created_at=log.created_at.isoformat() if log.created_at else ''
        )
        for log in logs
    ]


@router.get("/emotion-trend", summary="全局情绪趋势")
async def get_emotion_trend(
    days: int = Query(7, ge=1, le=30),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    start_date = datetime.now() - timedelta(days=days)
    
    records = db.query(EmotionRecordModel).filter(
        EmotionRecordModel.created_at >= start_date
    ).all()
    
    emotion_counts: Dict[str, int] = {}
    daily_counts: Dict[str, Dict[str, int]] = {}
    
    for r in records:
        emotion_type = r.emotion_type or 'neutral'
        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
        
        day_key = r.created_at.strftime('%Y-%m-%d') if r.created_at else 'unknown'
        if day_key not in daily_counts:
            daily_counts[day_key] = {}
        daily_counts[day_key][emotion_type] = daily_counts[day_key].get(emotion_type, 0) + 1
    
    return {
        "period_days": days,
        "total_records": len(records),
        "emotion_distribution": emotion_counts,
        "daily_trend": daily_counts
    }


@router.get("/assessment-stats", summary="测评统计")
async def get_assessment_stats(
    days: int = Query(30, ge=1, le=90),
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    start_date = datetime.now() - timedelta(days=days)
    
    assessments = db.query(AssessmentModel).filter(
        AssessmentModel.created_at >= start_date
    ).all()
    
    scale_counts: Dict[str, int] = {}
    level_counts: Dict[str, int] = {}
    daily_counts: Dict[str, int] = {}
    
    for a in assessments:
        scale_type = a.scale_type or 'unknown'
        scale_counts[scale_type] = scale_counts.get(scale_type, 0) + 1
        
        level = a.result_level or 'unknown'
        level_counts[level] = level_counts.get(level, 0) + 1
        
        day_key = a.created_at.strftime('%Y-%m-%d') if a.created_at else 'unknown'
        daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
    
    return {
        "period_days": days,
        "total_assessments": len(assessments),
        "scale_distribution": scale_counts,
        "level_distribution": level_counts,
        "daily_trend": daily_counts
    }


@router.get("/export/users", summary="导出用户数据")
async def export_users(
    admin=Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(UserModel).all()
    
    operation_log_service.log(
        db=db,
        user_id=admin.id,
        action=operation_log_service.ACTION_ADMIN_EXPORT,
        resource_type="users",
        details={"count": len(users)}
    )
    
    return {
        "users": [
            {
                "id": u.id,
                "phone": u.phone,
                "nickname": u.nickname,
                "age_group": u.age_group,
                "created_at": u.created_at.isoformat() if u.created_at else ''
            }
            for u in users
        ]
    }
