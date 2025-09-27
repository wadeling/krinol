"""
AI服务模块
处理大模型相关的业务逻辑
"""

import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from ..models.resume_models import AnalysisResult, AnalysisStatus, ResumeData
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AIService:
    """AI分析服务"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.openai.com/v1"
    
    async def analyze_resume(
        self, 
        resume_data: ResumeData, 
        analysis_type: str = "comprehensive",
        custom_prompt: Optional[str] = None,
        job_requirements: Optional[str] = None
    ) -> AnalysisResult:
        """
        分析简历
        
        Args:
            resume_data: 简历数据
            analysis_type: 分析类型
            custom_prompt: 自定义提示词
            job_requirements: 职位要求
            
        Returns:
            AnalysisResult: 分析结果
        """
        start_time = datetime.now()
        
        try:
            # 构建分析提示词
            prompt = self._build_analysis_prompt(
                resume_data, analysis_type, custom_prompt, job_requirements
            )
            
            # 调用AI模型
            raw_response = await self._call_ai_model(prompt)
            
            # 解析响应
            analysis_result = self._parse_ai_response(raw_response, resume_data.id)
            
            # 计算处理时间
            processing_duration = (datetime.now() - start_time).total_seconds()
            analysis_result.processing_duration = processing_duration
            analysis_result.ai_model_used = self.model_name
            analysis_result.raw_response = raw_response
            analysis_result.status = AnalysisStatus.COMPLETED
            analysis_result.analysis_time = datetime.now()
            
            logger.info(f"简历分析完成，耗时: {processing_duration:.2f}秒")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"简历分析失败: {str(e)}")
            return AnalysisResult(
                resume_id=resume_data.id or "",
                analysis_type=analysis_type,
                status=AnalysisStatus.FAILED,
                processing_duration=(datetime.now() - start_time).total_seconds()
            )
    
    def _build_analysis_prompt(
        self, 
        resume_data: ResumeData, 
        analysis_type: str,
        custom_prompt: Optional[str],
        job_requirements: Optional[str]
    ) -> str:
        """构建分析提示词"""
        
        base_prompt = f"""
请分析以下简历，并提供详细的分析报告。

简历内容：
{resume_data.content}

分析要求：
1. 总体评分（0-100分）
2. 优势点（至少3个）
3. 待改进点（至少3个）
4. 改进建议（至少3个）
5. 工作经验分析
6. 技能分析
7. 教育背景分析

请以JSON格式返回结果，格式如下：
{{
    "overall_score": 85,
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["待改进1", "待改进2", "待改进3"],
    "recommendations": ["建议1", "建议2", "建议3"],
    "experience_analysis": {{
        "years_of_experience": 5,
        "relevant_experience": "相关经验描述",
        "career_progression": "职业发展轨迹"
    }},
    "skills_analysis": {{
        "technical_skills": ["技能1", "技能2"],
        "soft_skills": ["软技能1", "软技能2"],
        "skill_gaps": ["技能缺口1", "技能缺口2"]
    }},
    "education_analysis": {{
        "education_level": "本科",
        "relevant_education": "相关教育背景",
        "certifications": ["证书1", "证书2"]
    }}
}}
"""
        
        if custom_prompt:
            base_prompt += f"\n\n自定义分析要求：\n{custom_prompt}"
        
        if job_requirements:
            base_prompt += f"\n\n职位要求：\n{job_requirements}"
        
        return base_prompt
    
    async def _call_ai_model(self, prompt: str) -> Dict[str, Any]:
        """调用AI模型"""
        # 这里应该实现实际的API调用
        # 为了演示，返回模拟数据
        await asyncio.sleep(1)  # 模拟API调用延迟
        
        return {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "overall_score": 85,
                        "strengths": [
                            "具有5年相关工作经验",
                            "掌握多种编程语言",
                            "有团队管理经验"
                        ],
                        "weaknesses": [
                            "缺乏云计算经验",
                            "英语水平有待提高",
                            "项目管理证书不足"
                        ],
                        "recommendations": [
                            "学习AWS或Azure云平台",
                            "参加英语培训课程",
                            "考取PMP项目管理证书"
                        ],
                        "experience_analysis": {
                            "years_of_experience": 5,
                            "relevant_experience": "在软件开发领域有丰富经验",
                            "career_progression": "从初级开发到技术主管"
                        },
                        "skills_analysis": {
                            "technical_skills": ["Python", "Java", "React", "MySQL"],
                            "soft_skills": ["团队协作", "问题解决", "沟通能力"],
                            "skill_gaps": ["云计算", "DevOps", "微服务架构"]
                        },
                        "education_analysis": {
                            "education_level": "本科",
                            "relevant_education": "计算机科学与技术专业",
                            "certifications": ["Oracle认证", "Scrum Master"]
                        }
                    }, ensure_ascii=False)
                }
            }]
        }
    
    def _parse_ai_response(self, response: Dict[str, Any], resume_id: str) -> AnalysisResult:
        """解析AI响应"""
        try:
            content = response["choices"][0]["message"]["content"]
            data = json.loads(content)
            
            return AnalysisResult(
                resume_id=resume_id,
                analysis_type="comprehensive",
                overall_score=data.get("overall_score"),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                recommendations=data.get("recommendations", []),
                experience_analysis=data.get("experience_analysis", {}),
                skills_analysis=data.get("skills_analysis", {}),
                education_analysis=data.get("education_analysis", {}),
                status=AnalysisStatus.COMPLETED
            )
        except Exception as e:
            logger.error(f"解析AI响应失败: {str(e)}")
            raise
