import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.database import OperationLogModel

logger = logging.getLogger(__name__)


class OperationLogService:
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_SEND_MESSAGE = "send_message"
    ACTION_CREATE_SESSION = "create_session"
    ACTION_DELETE_SESSION = "delete_session"
    ACTION_SUBMIT_ASSESSMENT = "submit_assessment"
    ACTION_CREATE_EMOTION = "create_emotion"
    ACTION_HANDLE_CRISIS = "handle_crisis"
    ACTION_UPLOAD_FILE = "upload_file"
    ACTION_UPDATE_PROFILE = "update_profile"
    ACTION_ADMIN_LOGIN = "admin_login"
    ACTION_ADMIN_VIEW = "admin_view"
    ACTION_ADMIN_EXPORT = "admin_export"

    @staticmethod
    def log(
        db: Session,
        user_id: str,
        action: str,
        resource_type: str = "",
        resource_id: str = "",
        details: Optional[Dict[str, Any]] = None,
        ip_address: str = "",
        user_agent: str = ""
    ) -> OperationLogModel:
        log_entry = OperationLogModel(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details, ensure_ascii=False) if details else None,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        
        logger.info(f"Operation log: user={user_id}, action={action}, resource={resource_type}/{resource_id}")
        
        return log_entry

    @staticmethod
    def get_user_logs(
        db: Session,
        user_id: str,
        limit: int = 50
    ) -> List[OperationLogModel]:
        return db.query(OperationLogModel).filter(
            OperationLogModel.user_id == user_id
        ).order_by(desc(OperationLogModel.created_at)).limit(limit).all()

    @staticmethod
    def get_logs_by_action(
        db: Session,
        action: str,
        limit: int = 100
    ) -> List[OperationLogModel]:
        return db.query(OperationLogModel).filter(
            OperationLogModel.action == action
        ).order_by(desc(OperationLogModel.created_at)).limit(limit).all()

    @staticmethod
    def get_recent_logs(
        db: Session,
        limit: int = 100
    ) -> List[OperationLogModel]:
        return db.query(OperationLogModel).order_by(
            desc(OperationLogModel.created_at)
        ).limit(limit).all()

    @staticmethod
    def get_logs_by_date_range(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None
    ) -> List[OperationLogModel]:
        query = db.query(OperationLogModel).filter(
            OperationLogModel.created_at >= start_date,
            OperationLogModel.created_at <= end_date
        )
        if user_id:
            query = query.filter(OperationLogModel.user_id == user_id)
        return query.order_by(desc(OperationLogModel.created_at)).all()

    @staticmethod
    def format_log(log: OperationLogModel) -> Dict[str, Any]:
        return {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": json.loads(log.details) if log.details else None,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "created_at": log.created_at.isoformat() if log.created_at else ""
        }


operation_log_service = OperationLogService()
