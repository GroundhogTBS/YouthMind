from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import logging

from models.database import get_db, FileUploadModel
from routers.user import get_current_user, UserModel
from services.file_upload import file_upload_service
from services.operation_log import operation_log_service

logger = logging.getLogger(__name__)
router = APIRouter()


class UploadResponse(BaseModel):
    file_id: int
    file_type: str
    file_name: str
    file_path: str
    file_size: int


@router.post("/avatar", response_model=UploadResponse, summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        file_path, filename = await file_upload_service.upload_avatar(user.id, file)
        
        upload_record = FileUploadModel(
            user_id=user.id,
            file_type="avatar",
            file_name=filename,
            file_path=file_path,
            file_size=0,
            mime_type=file.content_type
        )
        db.add(upload_record)
        db.commit()
        db.refresh(upload_record)
        
        operation_log_service.log(
            db=db,
            user_id=user.id,
            action=operation_log_service.ACTION_UPLOAD_FILE,
            resource_type="avatar",
            resource_id=str(upload_record.id),
            details={"file_name": filename, "file_path": file_path}
        )
        
        return UploadResponse(
            file_id=upload_record.id,
            file_type="avatar",
            file_name=filename,
            file_path=file_path,
            file_size=0
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload avatar failed: {e}")
        raise HTTPException(status_code=500, detail="上传失败")


@router.post("/voice", response_model=UploadResponse, summary="上传语音消息")
async def upload_voice(
    file: UploadFile = File(...),
    session_id: str = Form(""),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        file_path, filename, file_size = await file_upload_service.upload_voice(user.id, file)
        
        upload_record = FileUploadModel(
            user_id=user.id,
            file_type="voice",
            file_name=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type
        )
        db.add(upload_record)
        db.commit()
        db.refresh(upload_record)
        
        operation_log_service.log(
            db=db,
            user_id=user.id,
            action=operation_log_service.ACTION_UPLOAD_FILE,
            resource_type="voice",
            resource_id=str(upload_record.id),
            details={
                "file_name": filename, 
                "file_path": file_path,
                "session_id": session_id
            }
        )
        
        return UploadResponse(
            file_id=upload_record.id,
            file_type="voice",
            file_name=filename,
            file_path=file_path,
            file_size=file_size
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload voice failed: {e}")
        raise HTTPException(status_code=500, detail="上传失败")


@router.delete("/{file_id}", summary="删除文件")
async def delete_file(
    file_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    upload_record = db.query(FileUploadModel).filter(
        FileUploadModel.id == file_id,
        FileUploadModel.user_id == user.id
    ).first()
    
    if not upload_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_upload_service.delete_file(upload_record.file_path)
    
    db.delete(upload_record)
    db.commit()
    
    return {"success": True}
