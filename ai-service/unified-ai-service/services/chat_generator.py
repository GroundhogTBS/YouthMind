from typing import List, Dict, Optional, AsyncGenerator
import logging
import os
import json
import httpx

from core.config import settings
from core.constants import SYSTEM_PROMPT, COPING_STRATEGIES, AGE_GROUP_INFO
from services.emotion_analyzer import EmotionAnalyzer
from services.crisis_detector import CrisisDetector

logger = logging.getLogger(__name__)


class LLMProvider:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_client = None
        self._init_providers()
    
    def _init_providers(self):
        if settings.OPENAI_API_KEY:
            try:
                import openai
                self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI provider initialized")
            except ImportError:
                logger.warning("OpenAI库未安装")
        
        if settings.DEEPSEEK_API_KEY:
            logger.info("DeepSeek provider configured")
    
    async def generate(self, messages: List[Dict], **kwargs) -> str:
        logger.info(f"Provider: {self.provider}, DEEPSEEK_API_KEY: {settings.DEEPSEEK_API_KEY[:20] if settings.DEEPSEEK_API_KEY else 'None'}...")
        if self.provider == "deepseek" and settings.DEEPSEEK_API_KEY:
            logger.info("Calling _generate_deepseek")
            return await self._generate_deepseek(messages, **kwargs)
        elif self.provider == "openai" and self.openai_client:
            logger.info("Calling _generate_openai")
            return await self._generate_openai(messages, **kwargs)
        else:
            logger.info("Calling _generate_fallback")
            return await self._generate_fallback(messages)
    
    async def generate_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        if self.provider == "deepseek" and settings.DEEPSEEK_API_KEY:
            async for chunk in self._stream_deepseek(messages, **kwargs):
                yield chunk
        elif self.provider == "openai" and self.openai_client:
            async for chunk in self._stream_openai(messages, **kwargs):
                yield chunk
        else:
            response = await self._generate_fallback(messages)
            yield f"data: {json.dumps({'content': response, 'done': True})}\n\n"
    
    async def _generate_deepseek(self, messages: List[Dict], **kwargs) -> str:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.DEEPSEEK_MODEL,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", 500),
                        "temperature": kwargs.get("temperature", 0.7),
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return "抱歉，我现在无法回应。请稍后再试，或者拨打心理援助热线 400-161-9995。"
    
    async def _stream_deepseek(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.DEEPSEEK_MODEL,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", 500),
                        "temperature": kwargs.get("temperature", 0.7),
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
                                break
                            try:
                                chunk = json.loads(data)
                                content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"DeepSeek流式API调用失败: {e}")
            yield f"data: {json.dumps({'content': '抱歉，我现在无法回应。', 'done': True})}\n\n"
    
    async def _generate_openai(self, messages: List[Dict], **kwargs) -> str:
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 500),
                temperature=kwargs.get("temperature", 0.7),
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return "抱歉，我现在无法回应。请稍后再试，或者拨打心理援助热线 400-161-9995。"
    
    async def _stream_openai(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        try:
            stream = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 500),
                temperature=kwargs.get("temperature", 0.7),
                top_p=0.9,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    data = json.dumps({
                        "content": chunk.choices[0].delta.content,
                        "done": False
                    })
                    yield f"data: {data}\n\n"
            
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
        except Exception as e:
            logger.error(f"OpenAI流式API调用失败: {e}")
            yield f"data: {json.dumps({'content': '抱歉，我现在无法回应。', 'done': True})}\n\n"
    
    async def _generate_fallback(self, messages: List[Dict]) -> str:
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break
        
        responses = [
            "我理解你的感受，想和我多聊聊吗？",
            "听起来你有些烦恼，我在这里陪你。",
            "每个人都会有情绪波动的时候，这很正常。",
            "谢谢你愿意和我分享，我会认真倾听的。",
            "我在这里，随时准备倾听你的心声。"
        ]
        
        import random
        return random.choice(responses)


class ChatGenerator:
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.crisis_detector = CrisisDetector()
        self.llm = LLMProvider()

    async def generate(
        self, 
        message: str, 
        history: Optional[List[Dict]] = None,
        user_info: Optional[Dict] = None
    ) -> Dict:
        emotion_result = await self.emotion_analyzer.analyze(message)
        
        crisis_result = await self.crisis_detector.detect(message)
        
        if crisis_result["risk_level"] in ["red", "orange"]:
            crisis_response = self.crisis_detector.generate_crisis_response(
                crisis_result["risk_level"], 
                message
            )
            return {
                "content": crisis_response,
                "emotion": {
                    "primary": emotion_result["primary_emotion"],
                    "score": emotion_result["confidence"]
                },
                "crisis": crisis_result,
                "alert": crisis_result["should_alert"],
                "source": "crisis_intervention"
            }
        
        context = self._build_context(history, user_info, emotion_result)
        messages = self._build_messages(message, context, history)
        
        response = await self.llm.generate(messages)
        
        return {
            "content": response,
            "emotion": {
                "primary": emotion_result["primary_emotion"],
                "score": emotion_result["confidence"]
            },
            "crisis": crisis_result,
            "alert": False,
            "source": settings.LLM_PROVIDER
        }

    async def generate_stream(
        self, 
        message: str, 
        history: Optional[List[Dict]] = None,
        user_info: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        emotion_result = await self.emotion_analyzer.analyze(message)
        crisis_result = await self.crisis_detector.detect(message)
        
        if crisis_result["risk_level"] in ["red", "orange"]:
            crisis_response = self.crisis_detector.generate_crisis_response(
                crisis_result["risk_level"], 
                message
            )
            yield f"data: {json.dumps({'content': crisis_response, 'done': True})}\n\n"
            return
        
        context = self._build_context(history, user_info, emotion_result)
        messages = self._build_messages(message, context, history)
        
        async for chunk in self.llm.generate_stream(messages):
            yield chunk

    def _build_messages(
        self, 
        message: str, 
        context: str,
        history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if context:
            messages.append({"role": "system", "content": f"上下文信息：{context}"})
        
        if history:
            for msg in history[-10:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"]:
                    messages.append({"role": role, "content": content})
        
        messages.append({"role": "user", "content": message})
        return messages

    def _build_context(
        self, 
        history: Optional[List[Dict]], 
        user_info: Optional[Dict],
        emotion_result: Dict
    ) -> str:
        context_parts = []
        
        if user_info:
            age_group = user_info.get("age_group", "")
            if age_group and age_group in AGE_GROUP_INFO:
                info = AGE_GROUP_INFO[age_group]
                context_parts.append(f"用户年龄段：{info['age_range']}")
                context_parts.append(f"特点：{', '.join(info['characteristics'])}")
                context_parts.append(f"常见问题：{', '.join(info['common_issues'])}")
        
        if emotion_result:
            context_parts.append(f"当前主要情绪：{emotion_result.get('primary_label', '平静')}")
            context_parts.append(f"情绪强度：{emotion_result.get('intensity', 'mild')}")
        
        return " | ".join(context_parts) if context_parts else ""
