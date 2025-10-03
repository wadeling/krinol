"""
数据库模型定义
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class ResumeFormatEnum(str, enum.Enum):
    """简历格式枚举"""
    PDF = "PDF"
    DOCX = "DOCX"
    TXT = "TXT"


class ResumeDB(Base):
    """简历数据库模型"""
    __tablename__ = "resume_data"
    
    id = Column(String(36), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    format = Column(Enum(ResumeFormatEnum), nullable=False)
    content = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(36), nullable=True)
    file_path = Column(String(500), nullable=True)
    processing_status = Column(String(20), default="pending", nullable=False)
    extracted_info = Column(JSON, nullable=True)
    processing_error = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # AI提取的字段
    name = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    school_name = Column(String(200), nullable=True)
    school_city = Column(String(100), nullable=True)
    education_level = Column(String(50), nullable=True)
    major = Column(String(100), nullable=True)
    graduation_year = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    position = Column(String(200), nullable=True, comment='求职岗位')
    work_experience = Column(JSON, nullable=True)
    projects = Column(JSON, nullable=True)
    
    # 评分相关字段
    score = Column(Integer, nullable=True, comment="简历总分")
    score_detail = Column(JSON, nullable=True, comment="各维度详细得分")


class AnalysisResultDB(Base):
    """分析结果数据库模型"""
    __tablename__ = "analysis_results"
    
    id = Column(String(36), primary_key=True, index=True)
    resume_id = Column(String(36), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    
    # 分析结果字段
    overall_score = Column(String(10), nullable=True)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # 详细分析
    experience_analysis = Column(JSON, nullable=True)
    skills_analysis = Column(JSON, nullable=True)
    education_analysis = Column(JSON, nullable=True)
    
    # 元数据
    analysis_time = Column(DateTime, nullable=True)
    processing_duration = Column(String(20), nullable=True)
    ai_model_used = Column(String(100), nullable=True)
    raw_response = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
