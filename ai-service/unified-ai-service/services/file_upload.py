import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException

from core.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'uploads')
AVATAR_DIR = os.path.join(UPLOAD_DIR, 'avatars')
VOICE_DIR = os.path.join(UPLOAD_DIR, 'voices')

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_AUDIO_TYPES = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a']

MAX_AVATAR_SIZE = 5 * 1024 * 1024
MAX_VOICE_SIZE = 10 * 1024 * 1024


def ensure_dirs():
    for d in [UPLOAD_DIR, AVATAR_DIR, VOICE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)


ensure_dirs()


class FileUploadService:
    @staticmethod
    async def upload_avatar(
        user_id: str, 
        file: UploadFile
    ) -> Tuple[str, str]:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的图片格式: {file.content_type}"
            )
        
        content = await file.read()
        if len(content) > MAX_AVATAR_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"图片大小超过限制 (最大 {MAX_AVATAR_SIZE // 1024 // 1024}MB)"
            )
        
        ext = file.filename.split('.')[-1] if file.filename else 'jpg'
        filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(AVATAR_DIR, filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        relative_path = f"/uploads/avatars/{filename}"
        logger.info(f"Avatar uploaded: {relative_path}")
        
        return relative_path, filename

    @staticmethod
    async def upload_voice(
        user_id: str, 
        file: UploadFile
    ) -> Tuple[str, str, int]:
        if file.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的音频格式: {file.content_type}"
            )
        
        content = await file.read()
        if len(content) > MAX_VOICE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"音频大小超过限制 (最大 {MAX_VOICE_SIZE // 1024 // 1024}MB)"
            )
        
        ext = file.filename.split('.')[-1] if file.filename else 'mp3'
        filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
        file_path = os.path.join(VOICE_DIR, filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        relative_path = f"/uploads/voices/{filename}"
        file_size = len(content)
        
        logger.info(f"Voice uploaded: {relative_path}, size: {file_size}")
        
        return relative_path, filename, file_size

    @staticmethod
    def get_file_path(relative_path: str) -> Optional[str]:
        if relative_path.startswith('/uploads/'):
            relative_path = relative_path[9:]
        full_path = os.path.join(UPLOAD_DIR, relative_path)
        if os.path.exists(full_path):
            return full_path
        return None

    @staticmethod
    def delete_file(relative_path: str) -> bool:
        full_path = FileUploadService.get_file_path(relative_path)
        if full_path and os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"File deleted: {relative_path}")
            return True
        return False


file_upload_service = FileUploadService()
