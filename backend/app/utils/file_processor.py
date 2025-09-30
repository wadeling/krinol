"""
文件处理工具
处理PDF转Markdown等功能
"""

import fitz  # PyMuPDF
import markdown
from typing import Optional, Dict, Any
import re
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FileProcessor:
    """文件处理器"""
    
    def __init__(self):
        self.markdown_converter = markdown.Markdown(extensions=['tables', 'codehilite'])
    
    async def pdf_to_markdown(self, file_path: str) -> str:
        """
        将PDF文件转换为Markdown格式
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            str: Markdown格式的文本内容
        """
        try:
            logger.info(f"开始转换PDF文件: {file_path}")
            
            # 打开PDF文件
            doc = fitz.open(file_path)
            markdown_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # 清理文本
                cleaned_text = self._clean_text(text)
                
                # 转换为Markdown格式
                markdown_text = self._text_to_markdown(cleaned_text)
                
                if markdown_text.strip():
                    markdown_content.append(f"## 第 {page_num + 1} 页\n\n{markdown_text}\n")
            
            doc.close()
            
            result = "\n".join(markdown_content)
            logger.info(f"PDF转换完成: {file_path}, 内容长度: {len(result)}")
            
            return result
            
        except Exception as e:
            logger.error(f"PDF转换失败: {file_path}, 错误: {str(e)}")
            raise Exception(f"PDF转换失败: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        清理文本内容
        
        Args:
            text: 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:!?()（）【】《》""''""''、，。；：！？]', '', text)
        
        # 清理行首行尾空白
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    
    def _text_to_markdown(self, text: str) -> str:
        """
        将文本转换为Markdown格式
        
        Args:
            text: 清理后的文本
            
        Returns:
            str: Markdown格式的文本
        """
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测标题（简单的启发式规则）
            if self._is_title(line):
                markdown_lines.append(f"### {line}")
            else:
                markdown_lines.append(line)
        
        return '\n'.join(markdown_lines)
    
    def _is_title(self, line: str) -> bool:
        """
        判断是否为标题
        
        Args:
            line: 文本行
            
        Returns:
            bool: 是否为标题
        """
        # 简单的标题检测规则
        title_keywords = [
            '个人信息', '基本信息', '个人简介', '联系方式',
            '教育背景', '教育经历', '学历', '教育',
            '工作经历', '工作经验', '职业经历', '工作',
            '项目经历', '项目经验', '项目',
            '技能', '专业技能', '技术技能', '能力',
            '获奖情况', '荣誉', '奖项',
            '自我评价', '个人评价', '自我描述'
        ]
        
        # 检查是否包含标题关键词
        for keyword in title_keywords:
            if keyword in line:
                return True
        
        # 检查长度和格式
        if len(line) < 20 and not line.endswith(('。', '，', '；', '：')):
            return True
        
        return False
    
    async def extract_resume_info(self, markdown_content: str) -> Dict[str, Any]:
        """
        使用AI从Markdown内容中提取简历信息
        
        Args:
            markdown_content: Markdown格式的简历内容
            
        Returns:
            Dict[str, Any]: 提取的简历信息
        """
        try:
            logger.info("开始使用AI提取简历信息")
            # 延迟导入避免循环导入
            from ..services.ai_service import AIService
            ai_service = AIService()
            return await ai_service.extract_resume_info(markdown_content)
        except Exception as e:
            logger.error(f"AI信息提取失败: {str(e)}")
            return self._get_default_resume_info()
    
    def _get_default_resume_info(self) -> Dict[str, Any]:
        """
        获取默认简历信息（当AI提取失败时）
        
        Returns:
            Dict[str, Any]: 默认信息
        """
        return {
            "name": None,
            "school_name": None,
            "school_city": None,
            "education_level": None,
            "major": None,
            "graduation_year": None,
            "phone": None,
            "email": None,
            "work_experience": [],
            "skills": [],
            "projects": [],
            "summary": None
        }