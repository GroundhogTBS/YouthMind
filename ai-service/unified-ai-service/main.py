from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routers import emotion, chat, crisis, user, emotion_record, assessment, article
from core.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouthMind AI Service",
    description="青少年心理健康AI服务平台",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(user.router, prefix="/ai/user", tags=["用户服务"])
app.include_router(emotion.router, prefix="/ai/emotion", tags=["情绪分析"])
app.include_router(emotion_record.router, prefix="/ai/emotions", tags=["情绪记录"])
app.include_router(chat.router, prefix="/ai/chat", tags=["智能对话"])
app.include_router(crisis.router, prefix="/ai/crisis", tags=["危机检测"])
app.include_router(assessment.router, prefix="/ai/assessment", tags=["心理测评"])
app.include_router(article.router, prefix="/ai/articles", tags=["内容服务"])


@app.get("/")
async def root():
    return {
        "service": "YouthMind AI Service",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("YouthMind AI Service Starting...")
    print("API Docs: http://localhost:9000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=9000)
