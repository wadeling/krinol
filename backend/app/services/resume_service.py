"""
简历服务模块
处理简历相关的业务逻辑
"""

import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.resume_models import ResumeData, AnalysisResult, ResumeFormat
from ..models.db_models import ResumeDB, AnalysisResultDB, ResumeFormatEnum
from ..utils.file_processor import FileProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ResumeService:
    """简历处理服务"""
    
    def __init__(self, upload_dir: str = "/app/data", db: Optional[Session] = None):
        self.upload_dir = upload_dir
        self.file_processor = FileProcessor()
        self.db = db
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """确保上传目录存在"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    async def upload_resume(
        self, 
        file_content: bytes, 
        filename: str, 
        user_id: Optional[str] = None
    ) -> ResumeData:
        """
        上传简历文件
        
        Args:
            file_content: 文件内容
            filename: 文件名
            user_id: 用户ID
            
        Returns:
            ResumeData: 简历数据
        """
        try:
            # 生成唯一ID
            resume_id = str(uuid.uuid4())
            
            # 确定文件格式
            file_format = self._get_file_format(filename)
            
            # 保存文件
            file_path = os.path.join(self.upload_dir, f"{resume_id}.{file_format}")
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # 提取文本内容
            text_content = await self.file_processor.extract_text(file_path, file_format)
            
            # 创建简历数据对象
            resume_data = ResumeData(
                id=resume_id,
                filename=filename,
                format=file_format,
                content=text_content,
                file_size=len(file_content),
                user_id=user_id
            )
            
            logger.info(f"简历上传成功: {filename}, ID: {resume_id}")
            return resume_data
            
        except Exception as e:
            logger.error(f"简历上传失败: {str(e)}")
            raise
    
    def create_resume(self, resume_data: ResumeData) -> ResumeData:
        """
        创建简历记录
        
        Args:
            resume_data: 简历数据
            
        Returns:
            ResumeData: 创建的简历数据
        """
        if self.db:
            # 使用数据库
            db_resume = ResumeDB(
                id=resume_data.id,
                filename=resume_data.filename,
                format=ResumeFormatEnum(resume_data.format.value.upper()),
                content=resume_data.content,
                file_size=resume_data.file_size,
                upload_time=resume_data.upload_time,
                user_id=resume_data.user_id,
                file_path=resume_data.file_path,
                processing_status=resume_data.processing_status,
                extracted_info=resume_data.extracted_info,
                processing_error=resume_data.processing_error,
                processed_at=resume_data.processed_at
            )
            self.db.add(db_resume)
            self.db.commit()
            self.db.refresh(db_resume)
            logger.info(f"简历记录创建成功: {resume_data.id}")
        else:
            # 回退到内存存储
            logger.warning("数据库连接不可用，使用内存存储")
        
        return resume_data
    
    def get_resume(self, resume_id: str) -> Optional[ResumeData]:
        """
        获取简历数据
        
        Args:
            resume_id: 简历ID
            
        Returns:
            ResumeData: 简历数据，如果不存在返回None
        """
        if self.db:
            # 使用数据库
            db_resume = self.db.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
            if db_resume:
                return ResumeData(
                    id=db_resume.id,
                    filename=db_resume.filename,
                    format=ResumeFormat(db_resume.format.value.lower()),
                    content=db_resume.content,
                    file_size=db_resume.file_size,
                    upload_time=db_resume.upload_time,
                    user_id=db_resume.user_id,
                    file_path=db_resume.file_path,
                    processing_status=db_resume.processing_status,
                    extracted_info=db_resume.extracted_info,
                    processing_error=db_resume.processing_error,
                    processed_at=db_resume.processed_at,
                    # AI提取的字段
                    name=db_resume.name,
                    age=db_resume.age,
                    school_name=db_resume.school_name,
                    school_city=db_resume.school_city,
                    education_level=db_resume.education_level,
                    major=db_resume.major,
                    graduation_year=db_resume.graduation_year,
                    phone=db_resume.phone,
                    email=db_resume.email,
                    work_experience=db_resume.work_experience,
                    projects=db_resume.projects,
                    # 评分字段
                    score=db_resume.score,
                    score_detail=db_resume.score_detail
                )
            return None
        else:
            # 回退到内存存储
            return self._resumes.get(resume_id)
    
    def get_user_resumes(self, user_id: str) -> List[ResumeData]:
        """
        获取用户的所有简历
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[ResumeData]: 简历列表
        """
        if self.db:
            # 使用数据库
            db_resumes = self.db.query(ResumeDB).filter(ResumeDB.user_id == user_id).all()
            return [
                ResumeData(
                    id=db_resume.id,
                    filename=db_resume.filename,
                    format=ResumeFormat(db_resume.format.value.lower()),
                    content=db_resume.content,
                    file_size=db_resume.file_size,
                    upload_time=db_resume.upload_time,
                    user_id=db_resume.user_id,
                    file_path=db_resume.file_path,
                    processing_status=db_resume.processing_status,
                    extracted_info=db_resume.extracted_info,
                    processing_error=db_resume.processing_error,
                    processed_at=db_resume.processed_at,
                    # AI提取的字段
                    name=db_resume.name,
                    age=db_resume.age,
                    school_name=db_resume.school_name,
                    school_city=db_resume.school_city,
                    education_level=db_resume.education_level,
                    major=db_resume.major,
                    graduation_year=db_resume.graduation_year,
                    phone=db_resume.phone,
                    email=db_resume.email,
                    work_experience=db_resume.work_experience,
                    projects=db_resume.projects,
                    # 评分字段
                    score=db_resume.score,
                    score_detail=db_resume.score_detail
                )
                for db_resume in db_resumes
            ]
        else:
            # 回退到内存存储
            return [resume for resume in self._resumes.values() if resume.user_id == user_id]
    
    def update_resume_content(self, resume_id: str, content: str, extracted_info: Dict[str, Any], score: int = None, score_detail: Dict[str, Any] = None) -> bool:
        """
        更新简历内容和提取的信息
        
        Args:
            resume_id: 简历ID
            content: 简历内容
            extracted_info: 提取的信息
            score: 简历总分
            score_detail: 各维度详细得分
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if self.db:
                # 使用数据库
                db_resume = self.db.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                if db_resume:
                    db_resume.content = content
                    db_resume.extracted_info = extracted_info
                    db_resume.processing_status = "completed"
                    db_resume.processed_at = datetime.now()
                    
                    # 更新评分字段
                    if score is not None:
                        db_resume.score = score
                    if score_detail is not None:
                        db_resume.score_detail = score_detail
                    
                    # 从AI提取的信息中提取字段并写入对应列
                    logger.info(f"开始处理AI提取信息: {resume_id}, extracted_info类型: {type(extracted_info)}")
                    logger.info(f"extracted_info内容: {extracted_info}")
                    
                    if extracted_info:
                        logger.info(f"extracted_info不为空，开始提取字段")
                        db_resume.name = extracted_info.get('name')
                        db_resume.age = extracted_info.get('age')
                        db_resume.school_name = extracted_info.get('school_name')
                        db_resume.school_city = extracted_info.get('school_city')
                        db_resume.education_level = extracted_info.get('education_level')
                        db_resume.major = extracted_info.get('major')
                        db_resume.graduation_year = extracted_info.get('graduation_year')
                        db_resume.phone = extracted_info.get('phone')
                        db_resume.email = extracted_info.get('email')
                        db_resume.work_experience = extracted_info.get('work_experience', [])
                        db_resume.projects = extracted_info.get('projects', [])
                        
                        logger.info(f"AI提取信息已写入数据库: {resume_id}")
                        logger.info(f"提取的姓名: {db_resume.name}, 学校: {db_resume.school_name}, 专业: {db_resume.major}")
                    else:
                        logger.warning(f"extracted_info为空，跳过字段提取: {resume_id}")
                    
                    self.db.commit()
                    logger.info(f"简历内容更新成功: {resume_id}")
                    return True
                else:
                    logger.error(f"简历不存在: {resume_id}")
                    return False
            else:
                # 回退到内存存储
                logger.warning("数据库连接不可用，无法更新简历内容")
                return False
        except Exception as e:
            logger.error(f"简历内容更新失败: {str(e)}")
            return False
    
    def update_resume_status(self, resume_id: str, status: str, error: str = None) -> bool:
        """
        更新简历处理状态
        
        Args:
            resume_id: 简历ID
            status: 处理状态
            error: 错误信息
            
        Returns:
            bool: 更新是否成功
        """
        try:
            if self.db:
                # 使用数据库
                db_resume = self.db.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                if db_resume:
                    db_resume.processing_status = status
                    if error:
                        db_resume.processing_error = error
                    self.db.commit()
                    logger.info(f"简历状态更新成功: {resume_id}, 状态: {status}")
                    return True
                else:
                    logger.error(f"简历不存在: {resume_id}")
                    return False
            else:
                # 回退到内存存储
                logger.warning("数据库连接不可用，无法更新简历状态")
                return False
        except Exception as e:
            logger.error(f"简历状态更新失败: {str(e)}")
            return False
    
    def delete_resume(self, resume_id: str, user_id: str) -> bool:
        """
        删除简历
        
        Args:
            resume_id: 简历ID
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if self.db:
                # 使用数据库
                db_resume = self.db.query(ResumeDB).filter(ResumeDB.id == resume_id).first()
                if db_resume:
                    # 删除文件
                    if db_resume.file_path and os.path.exists(db_resume.file_path):
                        os.remove(db_resume.file_path)
                    
                    # 删除数据库记录
                    self.db.delete(db_resume)
                    self.db.commit()
                    logger.info(f"简历删除成功: {resume_id}")
                    return True
                else:
                    logger.error(f"简历不存在: {resume_id}")
                    return False
            else:
                # 回退到内存存储
                logger.warning("数据库连接不可用，无法删除简历")
                return False
            
        except Exception as e:
            logger.error(f"简历删除失败: {str(e)}")
            return False
    
    def _get_file_format(self, filename: str) -> ResumeFormat:
        """根据文件名确定文件格式"""
        ext = filename.lower().split('.')[-1]
        
        if ext == 'pdf':
            return ResumeFormat.PDF
        elif ext in ['doc', 'docx']:
            return ResumeFormat.DOCX
        elif ext == 'txt':
            return ResumeFormat.TXT
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    async def analyze_resume(
        self, 
        resume_id: str, 
        analysis_type: str = "comprehensive",
        custom_prompt: Optional[str] = None,
        job_requirements: Optional[str] = None
    ) -> AnalysisResult:
        """
        分析简历
        
        Args:
            resume_id: 简历ID
            analysis_type: 分析类型
            custom_prompt: 自定义提示词
            job_requirements: 职位要求
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 获取简历数据
        resume_data = self.get_resume(resume_id)
        if not resume_data:
            raise ValueError(f"简历不存在: {resume_id}")
        
        # 这里应该调用AI服务进行分析
        # 为了演示，返回模拟结果
        return AnalysisResult(
            resume_id=resume_id,
            analysis_type=analysis_type,
            status="completed",
            overall_score=85.0,
            strengths=["经验丰富", "技能全面"],
            weaknesses=["缺乏证书", "英语水平一般"],
            recommendations=["考取相关证书", "提高英语水平"]
        )
