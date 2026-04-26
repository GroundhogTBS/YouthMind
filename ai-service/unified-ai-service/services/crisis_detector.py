from typing import Dict, List, Optional
import logging
import re
from datetime import datetime

from core.constants import (
    CRISIS_KEYWORDS, 
    CRISIS_RESOURCES, 
    RISK_LEVELS, 
    RECOMMENDATIONS
)

logger = logging.getLogger(__name__)


class CrisisDetector:
    def __init__(self):
        self.crisis_keywords = CRISIS_KEYWORDS
        self.crisis_resources = CRISIS_RESOURCES
        self.risk_levels = RISK_LEVELS
        self.recommendations = RECOMMENDATIONS
        self.crisis_history = []

    async def detect(self, text: str, context: Optional[str] = None) -> Dict:
        combined_text = f"{context} {text}" if context else text
        
        risk_level, risk_score, matched_keywords = self._assess_risk(combined_text)
        
        resources = self._get_resources(risk_level)
        
        recommendations = self._get_recommendations(risk_level)
        
        immediate_actions = self._get_immediate_actions(risk_level)
        
        should_alert = risk_level in ["red", "orange"]
        
        result = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_name": self.risk_levels.get(risk_level, {}).get("name", "未知"),
            "matched_keywords": matched_keywords,
            "resources": resources,
            "recommendations": recommendations,
            "immediate_actions": immediate_actions,
            "should_alert": should_alert,
            "timestamp": datetime.now().isoformat()
        }
        
        if should_alert:
            self._log_crisis_event(result)
        
        return result

    def _assess_risk(self, text: str) -> tuple:
        matched = {"red": [], "orange": [], "yellow": []}
        
        for level, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    matched[level].append(keyword)
        
        if matched["red"]:
            score = 80 + min(len(matched["red"]) * 5, 20)
            return "red", score, matched["red"]
        
        if matched["orange"]:
            score = 60 + min(len(matched["orange"]) * 3, 20)
            return "orange", score, matched["orange"]
        
        if matched["yellow"]:
            score = 40 + min(len(matched["yellow"]) * 2, 20)
            return "yellow", score, matched["yellow"]
        
        return "green", 20, []

    def _get_resources(self, risk_level: str) -> List[Dict]:
        if risk_level == "red":
            return self.crisis_resources
        elif risk_level == "orange":
            return self.crisis_resources[:3]
        elif risk_level == "yellow":
            return [self.crisis_resources[3]]
        return []

    def _get_recommendations(self, risk_level: str) -> List[str]:
        return self.recommendations.get(risk_level, [])

    def _get_immediate_actions(self, risk_level: str) -> List[str]:
        actions = {
            "red": [
                "立即表达关心和担忧",
                "询问是否有具体计划",
                "提供心理援助热线：400-161-9995",
                "建议立即联系信任的成年人",
                "不要让用户独自一人",
                "强调困难是暂时的，有人愿意帮助"
            ],
            "orange": [
                "表达理解和支持",
                "询问最近发生了什么",
                "提供心理援助热线：400-161-9995",
                "建议与信任的人交流",
                "鼓励寻求专业帮助"
            ],
            "yellow": [
                "倾听用户的困扰",
                "表达理解和支持",
                "提供一些应对建议",
                "建议与朋友或家人交流"
            ],
            "green": [
                "继续保持关注",
                "提供积极的支持"
            ]
        }
        return actions.get(risk_level, [])

    def _log_crisis_event(self, result: Dict):
        event = {
            "timestamp": result["timestamp"],
            "risk_level": result["risk_level"],
            "risk_score": result["risk_score"],
            "keywords_count": len(result["matched_keywords"])
        }
        self.crisis_history.append(event)
        
        if len(self.crisis_history) > 100:
            self.crisis_history = self.crisis_history[-100:]
        
        logger.warning(f"危机事件检测: 风险等级={result['risk_level']}, 分数={result['risk_score']}")

    async def get_crisis_trend(self, messages: List[Dict]) -> Dict:
        if not messages:
            return {"trend": "stable", "risk_levels": []}
        
        risk_history = []
        for msg in messages[-10:]:
            if msg.get("role") == "user":
                result = await self.detect(msg.get("content", ""))
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

    def get_crisis_statistics(self) -> Dict:
        if not self.crisis_history:
            return {"total_events": 0, "by_level": {}}
        
        from collections import Counter
        level_counts = Counter(event["risk_level"] for event in self.crisis_history)
        
        return {
            "total_events": len(self.crisis_history),
            "by_level": dict(level_counts),
            "recent_events": self.crisis_history[-5:]
        }

    def generate_crisis_response(self, risk_level: str, user_message: str) -> str:
        if risk_level == "red":
            return (
                "我非常关心你现在的状况。如果你正在经历非常困难的时刻，"
                "请记住有人愿意帮助你。你可以拨打心理援助热线 400-161-9995，"
                "或者告诉一个你信任的成年人。你不需要独自面对这些困难。"
            )
        elif risk_level == "orange":
            return (
                "我能感受到你现在很痛苦。这种感受是真实的，也是可以被理解的。"
                "如果你愿意，可以和我说说发生了什么。同时，如果你觉得需要更多帮助，"
                "可以拨打心理援助热线 400-161-9995。"
            )
        elif risk_level == "yellow":
            return (
                "我理解你现在的感受。每个人都会经历困难的时刻，"
                "这并不代表你不够好。如果你愿意，可以和我聊聊发生了什么。"
            )
        return ""
