from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'youthmind.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    phone = Column(String, unique=True, index=True)
    nickname = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    signature = Column(String, nullable=True)
    age_group = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login_at = Column(DateTime, nullable=True)


class SessionModel(Base):
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)
    title = Column(String, default='新对话')
    user_id = Column(String, nullable=True, index=True)
    message_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class MessageModel(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    emotion = Column(String, nullable=True)
    emotion_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class CrisisEventModel(Base):
    __tablename__ = 'crisis_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True)
    user_id = Column(String, nullable=True)
    message_id = Column(Integer, nullable=True)
    risk_level = Column(String)
    risk_score = Column(Integer)
    matched_keywords = Column(Text)
    handled = Column(Integer, default=0)
    handler_id = Column(String, nullable=True)
    handled_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class EmotionRecordModel(Base):
    __tablename__ = 'emotion_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    emotion_type = Column(String)
    intensity = Column(Integer)
    triggers = Column(Text, nullable=True)
    thoughts = Column(Text, nullable=True)
    coping_methods = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class AssessmentModel(Base):
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    scale_type = Column(String)
    scale_name = Column(String)
    total_score = Column(Integer)
    result_level = Column(String)
    result_description = Column(Text)
    answers = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class ArticleModel(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, index=True)
    title = Column(String)
    summary = Column(Text)
    content = Column(Text)
    cover_image = Column(String, nullable=True)
    view_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class UserFavoriteModel(Base):
    __tablename__ = 'user_favorites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    article_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.now)


class OperationLogModel(Base):
    __tablename__ = 'operation_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    action = Column(String)
    resource_type = Column(String)
    resource_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class FileUploadModel(Base):
    __tablename__ = 'file_uploads'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    file_type = Column(String)
    file_name = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    mime_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class DiaryModel(Base):
    __tablename__ = 'diaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    title = Column(String, nullable=True)
    content = Column(Text)
    mood = Column(String, nullable=True)
    weather = Column(String, nullable=True)
    is_private = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
