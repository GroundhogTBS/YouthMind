from typing import List, Dict, Optional
import logging
import re

from core.constants import EMOTION_KEYWORDS, EMOTION_LABELS

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    def __init__(self):
        self.emotion_patterns = EMOTION_KEYWORDS
        self.intensifiers = ["很", "非常", "特别", "极其", "相当", "十分", "超级", "太", "好", "真"]
        self.negators = ["不", "没", "无", "别", "莫", "非", "未", "没有"]
        self.degree_words = {
            "极度": 2.0, "非常": 1.5, "特别": 1.5, "很": 1.2, 
            "有点": 0.8, "稍微": 0.7, "一点": 0.7
        }

    async def analyze(self, text: str, context: Optional[str] = None) -> Dict:
        combined_text = f"{context} {text}" if context else text
        
        emotion_scores = self._calculate_emotion_scores(combined_text)
        
        sorted_emotions = sorted(
            emotion_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        if not sorted_emotions or sorted_emotions[0][1] == 0:
            primary_emotion = "neutral"
            confidence = 1.0
        else:
            primary_emotion = sorted_emotions[0][0]
            total_score = sum(score for _, score in sorted_emotions)
            confidence = sorted_emotions[0][1] / total_score if total_score > 0 else 0
        
        emotions = [
            {
                "type": emotion, 
                "label": EMOTION_LABELS.get(emotion, emotion),
                "score": round(score, 3)
            }
            for emotion, score in sorted_emotions[:5]
            if score > 0
        ]
        
        keywords = self._extract_keywords(combined_text)
        
        intensity = self._calculate_intensity(combined_text)
        
        return {
            "primary_emotion": primary_emotion,
            "primary_label": EMOTION_LABELS.get(primary_emotion, primary_emotion),
            "confidence": round(confidence, 3),
            "intensity": intensity,
            "emotions": emotions,
            "keywords": keywords,
            "emotion_categories": self._categorize_emotions(emotions),
        }

    def _calculate_emotion_scores(self, text: str) -> Dict[str, float]:
        scores = {emotion: 0.0 for emotion in self.emotion_patterns}
        
        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(re.escape(pattern), text))
                for match in matches:
                    base_score = 1.0
                    
                    start_pos = max(0, match.start() - 5)
                    preceding_text = text[start_pos:match.start()]
                    
                    has_negator = False
                    for negator in self.negators:
                        if negator in preceding_text:
                            has_negator = True
                            break
                    
                    if has_negator:
                        base_score = -0.5
                    else:
                        for degree_word, multiplier in self.degree_words.items():
                            if degree_word in preceding_text:
                                base_score *= multiplier
                                break
                    
                    scores[emotion] += max(0, base_score)
        
        return scores

    def _calculate_intensity(self, text: str) -> str:
        intensifier_count = 0
        for intensifier in self.intensifiers:
            intensifier_count += text.count(intensifier)
        
        for degree_word in self.degree_words.keys():
            if degree_word in text:
                intensifier_count += 1
        
        if intensifier_count >= 3:
            return "strong"
        elif intensifier_count >= 1:
            return "moderate"
        else:
            return "mild"

    def _extract_keywords(self, text: str) -> List[str]:
        keywords = []
        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    keywords.append(pattern)
        return list(set(keywords))[:10]

    def _categorize_emotions(self, emotions: List[Dict]) -> Dict[str, List[str]]:
        positive = ["happy"]
        negative = ["sad", "angry", "anxious", "fear", "lonely", "confused", "inferior"]
        
        positive_emotions = [e["label"] for e in emotions if e["type"] in positive]
        negative_emotions = [e["label"] for e in emotions if e["type"] in negative]
        
        return {
            "positive": positive_emotions,
            "negative": negative_emotions,
            "is_positive_dominant": len(positive_emotions) > len(negative_emotions)
        }

    async def get_emotion_trend(self, messages: List[Dict]) -> Dict:
        if not messages:
            return {"trend": "stable", "dominant_emotions": []}
        
        emotion_history = []
        for msg in messages[-10:]:
            if msg.get("role") == "user":
                result = await self.analyze(msg.get("content", ""))
                emotion_history.append(result["primary_emotion"])
        
        if len(emotion_history) < 2:
            return {"trend": "stable", "dominant_emotions": emotion_history}
        
        from collections import Counter
        emotion_counts = Counter(emotion_history)
        dominant = emotion_counts.most_common(3)
        
        first_half = emotion_history[:len(emotion_history)//2]
        second_half = emotion_history[len(emotion_history)//2:]
        
        first_negative = sum(1 for e in first_half if e in ["sad", "angry", "anxious", "fear", "lonely", "confused", "inferior"])
        second_negative = sum(1 for e in second_half if e in ["sad", "angry", "anxious", "fear", "lonely", "confused", "inferior"])
        
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
