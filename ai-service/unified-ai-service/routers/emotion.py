from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from services.emotion_analyzer import EmotionAnalyzer
from core.constants import EMOTION_LABELS

logger = logging.getLogger(__name__)
router = APIRouter()

emotion_analyzer = EmotionAnalyzer()


class EmotionRequest(BaseModel):
    text: str
    context: Optional[str] = None


class EmotionResponse(BaseModel):
    primary_emotion: str
    primary_label: str
    confidence: float
    intensity: str
    emotions: List[Dict[str, Any]]
    keywords: List[str]
    emotion_categories: Dict[str, Any]


class BatchRequest(BaseModel):
    texts: List[str]


@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(request: EmotionRequest):
    try:
        result = await emotion_analyzer.analyze(request.text, request.context)
        return EmotionResponse(**result)
    except Exception as e:
        logger.error(f"Emotion analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_analyze(request: BatchRequest):
    results = []
    for text in request.texts:
        try:
            result = await emotion_analyzer.analyze(text)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "text": text})
    return {"results": results, "count": len(results)}


@router.get("/supported")
async def get_supported_emotions():
    return {
        "emotions": [
            {"type": emotion, "label": label}
            for emotion, label in EMOTION_LABELS.items()
        ],
        "count": len(EMOTION_LABELS)
    }


@router.get("/keywords")
async def get_emotion_keywords():
    from core.constants import EMOTION_KEYWORDS
    return {
        "keywords": {
            emotion: keywords[:10]
            for emotion, keywords in EMOTION_KEYWORDS.items()
        }
    }


@router.post("/trend")
async def analyze_trend(messages: List[Dict[str, Any]]):
    try:
        trend = await emotion_analyzer.get_emotion_trend(messages)
        return trend
    except Exception as e:
        logger.error(f"Emotion trend analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
