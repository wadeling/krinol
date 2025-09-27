"""
简历相关数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ResumeFormat(str, Enum):
    """简历格式枚举"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class AnalysisStatus(str, Enum):
    """分析状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResumeData(BaseModel):
    """简历数据模型"""
    id: Optional[str] = None
    filename: str = Field(..., description="简历文件名")
    format: ResumeFormat = Field(..., description="简历格式")
    content: str = Field(..., description="简历文本内容")
    file_size: int = Field(..., description="文件大小（字节）")
    upload_time: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = Field(None, description="上传用户ID")


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    resume_id: str = Field(..., description="简历ID")
    analysis_type: str = Field(..., description="分析类型")
    custom_prompt: Optional[str] = Field(None, description="自定义分析提示词")
    job_requirements: Optional[str] = Field(None, description="职位要求")


class AnalysisResult(BaseModel):
    """分析结果模型"""
    id: Optional[str] = None
    resume_id: str = Field(..., description="简历ID")
    analysis_type: str = Field(..., description="分析类型")
    status: AnalysisStatus = Field(default=AnalysisStatus.PENDING)
    
    # 分析结果字段
    overall_score: Optional[float] = Field(None, description="总体评分（0-100）")
    strengths: Optional[List[str]] = Field(None, description="优势点")
    weaknesses: Optional[List[str]] = Field(None, description="待改进点")
    recommendations: Optional[List[str]] = Field(None, description="改进建议")
    
    # 详细分析
    experience_analysis: Optional[Dict[str, Any]] = Field(None, description="工作经验分析")
    skills_analysis: Optional[Dict[str, Any]] = Field(None, description="技能分析")
    education_analysis: Optional[Dict[str, Any]] = Field(None, description="教育背景分析")
    
    # 元数据
    analysis_time: Optional[datetime] = Field(None, description="分析完成时间")
    processing_duration: Optional[float] = Field(None, description="处理耗时（秒）")
    ai_model_used: Optional[str] = Field(None, description="使用的AI模型")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="原始模型响应")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ResumeUploadResponse(BaseModel):
    """简历上传响应模型"""
    resume_id: str = Field(..., description="简历ID")
    filename: str = Field(..., description="文件名")
    status: str = Field(..., description="上传状态")
    message: str = Field(..., description="响应消息")


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    analysis_id: str = Field(..., description="分析ID")
    status: AnalysisStatus = Field(..., description="分析状态")
    result: Optional[AnalysisResult] = Field(None, description="分析结果")
    message: str = Field(..., description="响应消息")
