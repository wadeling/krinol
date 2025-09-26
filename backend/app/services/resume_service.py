"""
简历服务模块
处理简历相关的业务逻辑
"""

import os
import uuid
from typing import List, Optional
from datetime import datetime

from ..models.resume_models import ResumeData, AnalysisResult, ResumeFormat
from ..utils.file_processor import FileProcessor
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ResumeService:
    """简历处理服务"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        self.file_processor = FileProcessor()
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
    
    def get_resume(self, resume_id: str) -> Optional[ResumeData]:
        """
        获取简历数据
        
        Args:
            resume_id: 简历ID
            
        Returns:
            ResumeData: 简历数据，如果不存在返回None
        """
        # 这里应该从数据库获取
        # 为了演示，返回None
        return None
    
    def get_user_resumes(self, user_id: str) -> List[ResumeData]:
        """
        获取用户的所有简历
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[ResumeData]: 简历列表
        """
        # 这里应该从数据库获取
        # 为了演示，返回空列表
        return []
    
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
            # 这里应该从数据库删除记录
            # 删除文件
            file_path = os.path.join(self.upload_dir, f"{resume_id}.*")
            # 实际实现中需要根据文件格式删除对应文件
            
            logger.info(f"简历删除成功: {resume_id}")
            return True
            
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
