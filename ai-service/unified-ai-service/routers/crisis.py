from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
import logging

from services.crisis_detector import CrisisDetector
from core.constants import CRISIS_RESOURCES, RISK_LEVELS, RECOMMENDATIONS

logger = logging.getLogger(__name__)
router = APIRouter()

crisis_detector = CrisisDetector()


class RiskLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class CrisisRequest(BaseModel):
    text: str
    user_id: Optional[str] = None
    context: Optional[List[str]] = None


class CrisisResponse(BaseModel):
    risk_level: RiskLevel
    risk_score: int
    risk_name: str
    matched_keywords: List[str]
    recommendations: List[str]
    immediate_actions: List[str]
    resources: List[Dict[str, Any]]
    should_alert: bool


@router.post("/detect", response_model=CrisisResponse)
async def detect_crisis(request: CrisisRequest):
    try:
        context = " ".join(request.context) if request.context else None
        result = await crisis_detector.detect(request.text, context)
        return CrisisResponse(**result)
    except Exception as e:
        logger.error(f"Crisis detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def get_crisis_resources():
    return {
        "resources": CRISIS_RESOURCES,
        "count": len(CRISIS_RESOURCES)
    }


@router.get("/risk-levels")
async def get_risk_levels():
    return {
        "levels": {
            level: {
                "name": info["name"],
                "score_range": info["score_range"]
            }
            for level, info in RISK_LEVELS.items()
        }
    }


@router.get("/recommendations/{risk_level}")
async def get_recommendations(risk_level: RiskLevel):
    return {
        "risk_level": risk_level.value,
        "recommendations": RECOMMENDATIONS.get(risk_level.value, [])
    }


@router.get("/keywords")
async def get_crisis_keywords():
    from core.constants import CRISIS_KEYWORDS
    return {
        "keywords": {
            level: keywords[:20]
            for level, keywords in CRISIS_KEYWORDS.items()
        },
        "counts": {
            level: len(keywords)
            for level, keywords in CRISIS_KEYWORDS.items()
        }
    }


@router.post("/trend")
async def analyze_crisis_trend(messages: List[Dict[str, Any]]):
    try:
        trend = await crisis_detector.get_crisis_trend(messages)
        return trend
    except Exception as e:
        logger.error(f"Crisis trend analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_crisis_statistics():
    stats = crisis_detector.get_crisis_statistics()
    return stats


@router.post("/response/{risk_level}")
async def generate_crisis_response(risk_level: RiskLevel, text: str):
    try:
        response = crisis_detector.generate_crisis_response(risk_level.value, text)
        return {
            "risk_level": risk_level.value,
            "response": response
        }
    except Exception as e:
        logger.error(f"Crisis response generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
