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
    
    # 新增字段
    file_path: Optional[str] = Field(None, description="文件存储路径")
    processing_status: str = Field(default="pending", description="处理状态")
    extracted_info: Optional[Dict[str, Any]] = Field(None, description="AI提取的信息")
    processing_error: Optional[str] = Field(None, description="处理错误信息")
    processed_at: Optional[datetime] = Field(None, description="处理完成时间")
    
    # AI提取的字段
    name: Optional[str] = Field(None, description="姓名")
    age: Optional[int] = Field(None, description="年龄")
    school_name: Optional[str] = Field(None, description="学校名称")
    school_city: Optional[str] = Field(None, description="学校所在城市")
    education_level: Optional[str] = Field(None, description="学历层次")
    major: Optional[str] = Field(None, description="专业")
    graduation_year: Optional[str] = Field(None, description="毕业年份")
    phone: Optional[str] = Field(None, description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    position: Optional[str] = Field(None, description="求职岗位")
    work_experience: Optional[List[Dict[str, Any]]] = Field(None, description="工作经历")
    projects: Optional[List[Dict[str, Any]]] = Field(None, description="项目经验")
    
    # 评分相关字段
    score: Optional[int] = Field(None, description="简历总分")
    score_detail: Optional[Dict[str, Any]] = Field(None, description="各维度详细得分")


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


class BatchUploadItem(BaseModel):
    """批量上传单项结果"""
    filename: str = Field(..., description="文件名")
    resume_id: Optional[str] = Field(None, description="简历ID")
    status: str = Field(..., description="上传状态")
    message: str = Field(..., description="状态消息")
    error: Optional[str] = Field(None, description="错误信息")


class BatchUploadResponse(BaseModel):
    """批量上传响应模型"""
    total_files: int = Field(..., description="总文件数")
    successful: int = Field(..., description="成功上传数")
    failed: int = Field(..., description="失败数")
    results: List[BatchUploadItem] = Field(..., description="详细结果")
    message: str = Field(..., description="总体消息")


class PaginatedResumeResponse(BaseModel):
    """分页简历响应模型"""
    items: List[ResumeData] = Field(..., description="简历列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")
