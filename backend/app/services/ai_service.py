"""
AI服务
处理大模型调用和信息提取
"""

import openai
import json
import asyncio
from typing import Dict, Any, Optional
from ..config.settings import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AIService:
    """AI服务类"""
    
    def __init__(self):
        # 配置OpenAI客户端
        openai.api_key = settings.openai_api_key
        self.client = openai.OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    
    async def extract_resume_info(self, markdown_content: str) -> Dict[str, Any]:
        """
        从Markdown内容中提取简历信息
        
        Args:
            markdown_content: Markdown格式的简历内容
            
        Returns:
            Dict[str, Any]: 提取的信息
        """
        try:
            logger.info("开始使用AI提取简历信息")
            
            prompt = self._build_extraction_prompt(markdown_content)
            
            response = await self._call_openai(prompt)
            
            # 解析AI返回的JSON
            extracted_info = self._parse_ai_response(response)
            
            logger.info(f"AI信息提取完成: {extracted_info}")
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"AI信息提取失败: {str(e)}")
            return self._get_default_info()
    
    def _build_extraction_prompt(self, content: str) -> str:
        """
        构建AI提取信息的提示词
        
        Args:
            content: 简历内容
            
        Returns:
            str: 提示词
        """
        prompt = f"""
请从以下简历内容中提取关键信息，并以JSON格式返回。请确保提取的信息准确且完整。

简历内容：
{content}

请提取以下信息并以JSON格式返回：
{{
    "name": "姓名",
    "school_name": "学校名称",
    "school_city": "学校所在城市",
    "education_level": "学历层次（本科/硕士/博士等）",
    "major": "专业",
    "graduation_year": "毕业年份",
    "phone": "手机号",
    "email": "邮箱",
    "work_experience": [
        {{
            "company": "公司名称",
            "position": "职位",
            "duration": "工作时长",
            "description": "工作描述"
        }}
    ],
    "skills": ["技能1", "技能2", "技能3"],
    "projects": [
        {{
            "name": "项目名称",
            "description": "项目描述",
            "technologies": ["技术栈"]
        }}
    ],
    "summary": "个人简介或自我评价"
}}

注意：
1. 如果某些信息在简历中没有找到，请设置为null
2. 确保JSON格式正确
3. 提取的信息要准确，不要编造
4. 学校名称要完整，不要缩写
5. 城市名称要准确

请只返回JSON格式的结果，不要包含其他内容。
"""
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """
        调用OpenAI API
        
        Args:
            prompt: 提示词
            
        Returns:
            str: AI响应
        """
        try:
            # 使用 asyncio.to_thread 在单独线程中执行同步调用，避免阻塞事件循环
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的简历信息提取助手，能够准确从简历中提取关键信息。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20000,
                temperature=0.1
            )
            logger.info(f"llm响应: {response}")

            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            raise Exception(f"AI服务调用失败: {str(e)}")
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应
        
        Args:
            response: AI原始响应
            
        Returns:
            Dict[str, Any]: 解析后的信息
        """
        try:
            # 清理响应内容
            response = response.strip()
            
            # 移除可能的markdown代码块标记
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            # 解析JSON
            extracted_info = json.loads(response)
            
            # 验证必要字段
            if not isinstance(extracted_info, dict):
                raise ValueError("AI响应不是有效的JSON对象")
            
            return extracted_info
            
        except json.JSONDecodeError as e:
            logger.error(f"AI响应JSON解析失败: {str(e)}")
            logger.error(f"原始响应: {response}")
            return self._get_default_info()
        except Exception as e:
            logger.error(f"AI响应解析失败: {str(e)}")
            return self._get_default_info()
    
    def _get_default_info(self) -> Dict[str, Any]:
        """
        获取默认信息（当AI提取失败时）
        
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
    
    async def analyze_resume(self, resume_content: str, job_requirements: str = None) -> Dict[str, Any]:
        """
        分析简历（可选功能）
        
        Args:
            resume_content: 简历内容
            job_requirements: 职位要求
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        try:
            prompt = f"""
请分析以下简历内容，并给出评分和建议。

简历内容：
{resume_content}

{f"职位要求：{job_requirements}" if job_requirements else ""}

请以JSON格式返回分析结果：
{{
    "overall_score": 85,
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["不足1", "不足2"],
    "recommendations": ["建议1", "建议2"],
    "match_score": 90,
    "analysis": "详细分析内容"
}}

请只返回JSON格式的结果。
"""
            
            response = await self._call_openai(prompt)
            return self._parse_ai_response(response)
            
        except Exception as e:
            logger.error(f"简历分析失败: {str(e)}")
            return {
                "overall_score": 0,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "match_score": 0,
                "analysis": "分析失败"
            }