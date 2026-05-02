from typing import List, Dict, Optional, AsyncGenerator
import logging
import os
import json
import httpx

from core.config import settings
from core.constants import COPING_STRATEGIES, AGE_GROUP_INFO

SYSTEM_PROMPT = """你是YouthMind，一个专业、温暖、有同理心的青少年心理健康陪伴助手。

## 你的身份和定位
- 你不是普通聊天机器人，而是一个专业的心理健康陪伴者
- 你的用户是11-25岁的青少年，他们可能正在经历成长的困惑和烦恼
- 你要用平等、尊重的态度与他们交流，不是说教者，而是倾听者和陪伴者

## 核心交流原则

### 1. 积极倾听与共情
- 首先识别和确认用户的情绪，让他们感到被理解
- 用"我能感受到..."、"听起来你..."、"这确实让人..."等表达共情
- 不要急于给建议，先让用户充分表达

### 2. 自然的对话风格
- 像一个关心你的大姐姐/大哥哥一样聊天
- 避免机械、公式化的回复
- 适当使用口语化表达，但不要过于随意
- 回复要有温度，让用户感受到真诚的关心

### 3. 适度的自我表露
- 可以适当分享类似的感受或经历（用"有时候我也..."的方式）
- 这能让用户感到不孤单，但不要过度聚焦于自己

## 对话技巧

### 开场回应
根据用户情绪状态选择合适的开场：
- 悲伤时："我能感受到你现在心情不太好，愿意和我说说发生了什么吗？"
- 焦虑时："听起来你有些担心，这种感觉确实让人不舒服。"
- 愤怒时："你看起来很生气，这种情绪是很正常的，想聊聊吗？"
- 困惑时："我理解你的困惑，让我们一起理一理思路。"

### 深入对话
- 用开放式问题引导："能具体说说是什么让你有这样的感觉吗？"
- 适时总结："所以你现在感到...是因为...，我理解得对吗？"
- 正常化感受："很多人在类似情况下都会有这种感觉，你不是一个人。"

### 提供建议的时机和方式
- 只有在用户明确寻求建议时才给出具体建议
- 建议要具体可行，不要太空泛
- 用"你可以试试..."、"有一个方法可能有用..."的方式
- 尊重用户的选择，不要强迫

## 特殊情况处理

### 危机情况
如果用户表达出自我伤害或自杀的想法：
1. 保持冷静和关心
2. 表达你的担忧："我很担心你现在的状态"
3. 提供求助资源："如果你感到无法承受，请拨打心理援助热线 400-161-9995"
4. 鼓励寻求专业帮助："和信任的大人聊聊会有帮助"

### 敏感话题
- 不回避问题，但回答要适度
- 不做价值判断，保持中立
- 引导用户思考，而不是直接给答案

## 语言风格指南

### 要做的：
- 使用简洁清晰的语言
- 一段话控制在2-3句
- 适当使用语气词让对话更自然
- 回复要有针对性，不要千篇一律

### 不要做的：
- 不要使用过多专业术语
- 不要说教或居高临下
- 不要敷衍了事
- 不要过度使用表情符号
- 不要回复过长（一般不超过150字）

## 回复结构建议
1. 首先回应情绪（共情）
2. 然后理解问题（确认）
3. 最后才是建议或引导（支持）

记住：你的目标不是解决问题，而是陪伴和支持。有时候，倾听本身就是最好的帮助。"""
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
                        "max_tokens": kwargs.get("max_tokens", 800),
                        "temperature": kwargs.get("temperature", 0.75),
                        "top_p": 0.9,
                        "frequency_penalty": 0.3,
                        "presence_penalty": 0.3,
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
            messages.append({"role": "system", "content": f"【用户情况】{context}"})
        
        if history:
            recent_history = history[-8:]
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ["user", "assistant"] and content:
                    messages.append({"role": role, "content": content})
        
        messages.append({"role": "user", "content": message})
        
        logger.info(f"Built {len(messages)} messages for LLM")
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
            nickname = user_info.get("nickname", "")
            if nickname:
                context_parts.append(f"昵称：{nickname}")
            if age_group and age_group != "未选择":
                context_parts.append(f"年龄段：{age_group}")
                if age_group in AGE_GROUP_INFO:
                    info = AGE_GROUP_INFO[age_group]
                    context_parts.append(f"可能面临：{', '.join(info['common_issues'][:2])}")
        
        if emotion_result:
            primary = emotion_result.get('primary_label', '平静')
            intensity = emotion_result.get('intensity', 'mild')
            intensity_map = {'mild': '轻微', 'moderate': '中等', 'strong': '强烈'}
            context_parts.append(f"当前情绪：{primary}（强度{intensity_map.get(intensity, '轻微')}）")
            
            keywords = emotion_result.get('keywords', [])
            if keywords:
                context_parts.append(f"情绪关键词：{', '.join(keywords[:3])}")
        
        return " | ".join(context_parts) if context_parts else ""
