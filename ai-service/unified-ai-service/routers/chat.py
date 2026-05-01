from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
import json
import uuid
from datetime import datetime

from services.chat_generator import ChatGenerator
from services.emotion_analyzer import EmotionAnalyzer
from services.crisis_detector import CrisisDetector
from services.sensitive_filter import sensitive_filter
from models.database import (
    get_db, init_db, SessionModel, MessageModel, CrisisEventModel
)
from routers.user import get_current_user, UserModel

logger = logging.getLogger(__name__)
router = APIRouter()

chat_generator = ChatGenerator()
emotion_analyzer = EmotionAnalyzer()
crisis_detector = CrisisDetector()

init_db()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


class SendRequest(BaseModel):
    session_id: str = "default"
    content: str
    user_info: Optional[Dict[str, Any]] = None
    stream: bool = False


class SessionCreate(BaseModel):
    title: Optional[str] = "新对话"


class SessionUpdate(BaseModel):
    title: str


class ChatResponse(BaseModel):
    content: str
    emotion: Optional[Dict[str, Any]] = None
    crisis: Optional[Dict[str, Any]] = None
    alert: bool = False
    source: str


class SessionResponse(BaseModel):
    session_id: str
    title: str
    message_count: int
    created_at: str
    updated_at: str


@router.post("/send", response_model=ChatResponse, summary="发送消息")
async def send_message(
    request: SendRequest, 
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        has_sensitive, warning_msg, found_words = sensitive_filter.check_user_input(request.content)
        
        if has_sensitive:
            logger.warning(f"用户输入包含敏感词: {found_words}")
            return ChatResponse(
                content=warning_msg,
                emotion={"primary": "neutral", "score": 1.0},
                crisis={"risk_level": "green", "risk_score": 0},
                alert=False,
                source="filter"
            )
        
        session = db.query(SessionModel).filter(
            SessionModel.id == request.session_id,
            SessionModel.user_id == user.id
        ).first()
        
        if not session:
            session = SessionModel(
                id=request.session_id,
                user_id=user.id,
                title="新对话",
                message_count=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            db.add(session)
            db.commit()
        
        history = get_messages_from_db(db, request.session_id)
        
        result = await chat_generator.generate(
            message=request.content,
            history=history,
            user_info={"age_group": user.age_group} if user.age_group else None
        )
        
        filtered_content, _ = sensitive_filter.filter(result["content"])
        result["content"] = filtered_content
        
        save_message_to_db(db, request.session_id, "user", request.content)
        
        save_message_to_db(
            db, request.session_id, "assistant", 
            result["content"], 
            result.get("emotion", {}).get("primary"),
            result.get("emotion", {}).get("score")
        )
        
        update_session(db, request.session_id, request.content)
        
        if result.get("crisis") and result["crisis"].get("should_alert"):
            save_crisis_event(db, request.session_id, result["crisis"], user.id)
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat send failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=ChatResponse, summary="生成回复")
async def generate_response(request: ChatRequest):
    try:
        history = [{"role": m.role, "content": m.content} for m in request.messages[:-1]]
        current_message = request.messages[-1].content if request.messages else ""
        
        result = await chat_generator.generate(
            message=current_message,
            history=history
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_response(request: ChatRequest):
    async def generate():
        try:
            history = [{"role": m.role, "content": m.content} for m in request.messages[:-1]]
            current_message = request.messages[-1].content if request.messages else ""
            
            async for chunk in chat_generator.generate_stream(
                message=current_message,
                history=history
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Stream generation failed: {str(e)}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/session", response_model=SessionResponse, summary="创建会话")
async def create_session(
    request: SessionCreate = SessionCreate(), 
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session_id = str(uuid.uuid4())
    now = datetime.now()
    
    session = SessionModel(
        id=session_id,
        title=request.title,
        user_id=user.id,
        message_count=0,
        created_at=now,
        updated_at=now
    )
    db.add(session)
    db.commit()
    
    return SessionResponse(
        session_id=session_id,
        title=request.title,
        message_count=0,
        created_at=now.isoformat(),
        updated_at=now.isoformat()
    )


@router.get("/sessions", response_model=List[SessionResponse], summary="获取会话列表")
async def get_sessions(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == user.id
    ).order_by(SessionModel.updated_at.desc()).all()
    
    return [
        SessionResponse(
            session_id=s.id,
            title=s.title,
            message_count=s.message_count,
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat()
        )
        for s in sessions
    ]


@router.get("/history/{session_id}", summary="获取历史消息")
async def get_history(
    session_id: str, 
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(MessageModel).filter(
        MessageModel.session_id == session_id
    ).order_by(MessageModel.created_at).all()
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "emotion": m.emotion,
                "createdAt": m.created_at.isoformat()
            }
            for m in messages
        ],
        "session_info": {
            "id": session.id,
            "title": session.title,
            "messageCount": session.message_count
        }
    }


@router.put("/session/{session_id}")
async def update_session_title(
    session_id: str, 
    request: SessionUpdate, 
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.title = request.title
    session.updated_at = datetime.now()
    db.commit()
    
    return {"success": True, "title": request.title}


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str, 
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.query(MessageModel).filter(MessageModel.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    
    return {"success": True}


@router.get("/trend/{session_id}")
async def get_emotion_trend(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(MessageModel).filter(
        MessageModel.session_id == session_id,
        MessageModel.role == "user"
    ).order_by(MessageModel.created_at).limit(10).all()
    
    if not messages:
        return {"trend": "stable", "dominant_emotions": []}
    
    emotion_history = []
    for msg in messages:
        if msg.content:
            result = await emotion_analyzer.analyze(msg.content)
            emotion_history.append(result["primary_emotion"])
    
    if len(emotion_history) < 2:
        return {"trend": "stable", "dominant_emotions": emotion_history}
    
    from collections import Counter
    emotion_counts = Counter(emotion_history)
    dominant = emotion_counts.most_common(3)
    
    first_half = emotion_history[:len(emotion_history)//2]
    second_half = emotion_history[len(emotion_history)//2:]
    
    negative_emotions = ["sad", "angry", "anxious", "fear", "lonely", "confused", "inferior"]
    first_negative = sum(1 for e in first_half if e in negative_emotions)
    second_negative = sum(1 for e in second_half if e in negative_emotions)
    
    if second_negative > first_negative:
        trend = "worsening"
    elif second_negative < first_negative:
        trend = "improving"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "dominant_emotions": [e[0] for e in dominant],
        "emotion_history": emotion_history
    }


@router.get("/crisis-trend/{session_id}")
async def get_crisis_trend(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(MessageModel).filter(
        MessageModel.session_id == session_id,
        MessageModel.role == "user"
    ).order_by(MessageModel.created_at).limit(10).all()
    
    if not messages:
        return {"trend": "stable", "risk_levels": []}
    
    risk_history = []
    for msg in messages:
        if msg.content:
            result = await crisis_detector.detect(msg.content)
            risk_history.append(result["risk_level"])
    
    if len(risk_history) < 2:
        return {"trend": "stable", "risk_levels": risk_history}
    
    risk_scores = {"green": 1, "yellow": 2, "orange": 3, "red": 4}
    
    first_half = [risk_scores.get(r, 1) for r in risk_history[:len(risk_history)//2]]
    second_half = [risk_scores.get(r, 1) for r in risk_history[len(risk_history)//2:]]
    
    first_avg = sum(first_half) / len(first_half) if first_half else 1
    second_avg = sum(second_half) / len(second_half) if second_half else 1
    
    if second_avg > first_avg + 0.5:
        trend = "escalating"
    elif second_avg < first_avg - 0.5:
        trend = "decreasing"
    else:
        trend = "stable"
    
    return {
        "trend": trend,
        "risk_levels": risk_history,
        "average_risk": sum(risk_scores.get(r, 1) for r in risk_history) / len(risk_history)
    }


def get_messages_from_db(db: Session, session_id: str) -> List[Dict]:
    messages = db.query(MessageModel).filter(
        MessageModel.session_id == session_id
    ).order_by(MessageModel.created_at).limit(20).all()
    
    return [{"role": m.role, "content": m.content} for m in messages]


def save_message_to_db(db: Session, session_id: str, role: str, content: str, 
                       emotion: str = None, emotion_score: float = None):
    message = MessageModel(
        session_id=session_id,
        role=role,
        content=content,
        emotion=emotion,
        emotion_score=emotion_score
    )
    db.add(message)
    db.commit()


def update_session(db: Session, session_id: str, first_message: str):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if session:
        session.message_count += 1
        session.updated_at = datetime.now()
        if session.title == "新对话":
            session.title = first_message[:15] + ("..." if len(first_message) > 15 else "")
        db.commit()


def save_crisis_event(db: Session, session_id: str, crisis_data: Dict, user_id: str = None):
    event = CrisisEventModel(
        session_id=session_id,
        user_id=user_id,
        risk_level=crisis_data.get("risk_level"),
        risk_score=crisis_data.get("risk_score"),
        matched_keywords=json.dumps(crisis_data.get("matched_keywords", []))
    )
    db.add(event)
    db.commit()
