"""
AI服务
处理大模型调用和信息提取
"""

import openai
import json
import asyncio
import os
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
        
        # 加载评分数据
        self._load_scoring_data()
    
    def _load_scoring_data(self):
        """加载评分相关数据"""
        try:
            # 获取数据文件路径
            data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
            
            # 加载985院校数据
            with open(os.path.join(data_dir, "985.json"), "r", encoding="utf-8") as f:
                self.universities_985 = json.load(f)
            
            # 加载211院校数据
            with open(os.path.join(data_dir, "211.json"), "r", encoding="utf-8") as f:
                self.universities_211 = json.load(f)
            
            # 加载专业匹配数据
            with open(os.path.join(data_dir, "major.json"), "r", encoding="utf-8") as f:
                self.major_rules = json.load(f)
            
            logger.info("评分数据加载成功")
            
        except Exception as e:
            logger.error(f"评分数据加载失败: {str(e)}")
            # 设置默认数据
            self.universities_985 = []
            self.universities_211 = []
            self.major_rules = {}
    
    async def score_resume(self, markdown_content: str, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        对简历进行评分
        
        Args:
            markdown_content: Markdown格式的简历内容
            extracted_info: AI提取的简历信息
            
        Returns:
            Dict[str, Any]: 评分结果
        """
        try:
            logger.info("开始对简历进行评分")
            
            prompt = self._build_scoring_prompt(markdown_content, extracted_info)
            
            response = await self._call_openai(prompt)
            
            # 解析AI返回的JSON
            scoring_result = self._parse_scoring_response(response)
            
            logger.info(f"简历评分完成: {scoring_result}")
            
            return scoring_result
            
        except Exception as e:
            logger.error(f"简历评分失败: {str(e)}")
            return self._get_default_scoring_result()
    
    def _build_scoring_prompt(self, content: str, extracted_info: Dict[str, Any]) -> str:
        """
        构建评分提示词
        
        Args:
            content: 简历内容
            extracted_info: 提取的信息
            
        Returns:
            str: 提示词
        """
        # 构建985院校列表
        universities_985_list = [uni["school_name"] for uni in self.universities_985]
        universities_211_list = [uni["school_name"] for uni in self.universities_211]
        
        # 构建专业匹配规则
        computer_majors = self.major_rules.get("专业分类规则", {}).get("计算机类专业", {}).get("核心关键词", []) + \
                         self.major_rules.get("专业分类规则", {}).get("计算机类专业", {}).get("扩展关键词", [])
        related_majors = self.major_rules.get("专业分类规则", {}).get("相关理工科专业", {}).get("核心关键词", []) + \
                        self.major_rules.get("专业分类规则", {}).get("相关理工科专业", {}).get("扩展关键词", [])
        
        prompt = f"""
请根据以下评分规则对简历进行量化评分：

## 评分规则

### 一、地域筛选（基础项 | 最高+5分）
+5分：四川省内高校
+3分：四川省外重点高校
+0分：其他

### 二、学校选择（核心项 | 最高+10分）
+10分：985院校
+8分：211院校
+5分：普通本科院校
+2分：专科院校

### 三、专业匹配（分级项 | 最高+8分）
+8分：计算机科学、软件工程、人工智能等计算机相关专业
+5分：通信、电气、电子信息等其他理工科专业
+2分：其他专业

### 四、个人亮点（差异化项 | 最高+10分，取单项最高分，不累计）
+10分：ACM等权威编程竞赛获奖
+8分：持有Kubernetes等专业领域权威证书
+6分：拥有活跃的GitHub/Gitee个人项目（Star数 ≥ 50）
+4分：维护有高质量的技术博客（如CSDN）

### 五、项目经历（实践项 | 最高+10分）
+10分：有知名互联网大厂（如字节跳动、腾讯）实习经历
+7分：有其他公司的完整项目实习经历

### 六、简历质量（形式项 | 最高+3分，可累计）
+2分：成果量化（如："性能提升30%"）
+1分：使用主动性动词（如："主导"、"独立完成"）

## 参考数据

### 985院校名单：
{', '.join(universities_985_list)}

### 211院校名单：
{', '.join(universities_211_list)}

### 计算机相关专业关键词：
{', '.join(computer_majors)}

### 其他理工科专业关键词：
{', '.join(related_majors)}

## 简历信息
姓名：{extracted_info.get('name', '未知')}
学校：{extracted_info.get('school_name', '未知')}
专业：{extracted_info.get('major', '未知')}
学历：{extracted_info.get('education_level', '未知')}

## 简历内容
{content}

请严格按照评分规则进行评分，并以JSON格式返回结果：

{{
    "total_score": 总分,
    "score_details": {{
        "region_score": {{
            "score": 地域筛选得分,
            "reason": "评分原因"
        }},
        "school_score": {{
            "score": 学校选择得分,
            "reason": "评分原因"
        }},
        "major_score": {{
            "score": 专业匹配得分,
            "reason": "评分原因"
        }},
        "highlight_score": {{
            "score": 个人亮点得分,
            "reason": "评分原因"
        }},
        "experience_score": {{
            "score": 项目经历得分,
            "reason": "评分原因"
        }},
        "quality_score": {{
            "score": 简历质量得分,
            "reason": "评分原因"
        }}
    }}
}}

注意：
1. 总分应该是各维度得分的总和
2. 每个维度的得分不能超过其最高分
3. 个人亮点只取最高的一项得分，不累计
4. 简历质量可以累计得分
5. 请确保JSON格式正确

请只返回JSON格式的结果，不要包含其他内容。
"""
        return prompt
    
    def _parse_scoring_response(self, response: str) -> Dict[str, Any]:
        """
        解析评分响应
        
        Args:
            response: AI原始响应
            
        Returns:
            Dict[str, Any]: 解析后的评分结果
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
            scoring_result = json.loads(response)
            
            # 验证必要字段
            if not isinstance(scoring_result, dict):
                raise ValueError("AI响应不是有效的JSON对象")
            
            if "total_score" not in scoring_result or "score_details" not in scoring_result:
                raise ValueError("AI响应缺少必要字段")
            
            return scoring_result
            
        except json.JSONDecodeError as e:
            logger.error(f"评分响应JSON解析失败: {str(e)}")
            logger.error(f"原始响应: {response}")
            return self._get_default_scoring_result()
        except Exception as e:
            logger.error(f"评分响应解析失败: {str(e)}")
            return self._get_default_scoring_result()
    
    def _get_default_scoring_result(self) -> Dict[str, Any]:
        """
        获取默认评分结果（当AI评分失败时）
        
        Returns:
            Dict[str, Any]: 默认评分结果
        """
        return {
            "total_score": 0,
            "score_details": {
                "region_score": {"score": 0, "reason": "评分失败"},
                "school_score": {"score": 0, "reason": "评分失败"},
                "major_score": {"score": 0, "reason": "评分失败"},
                "highlight_score": {"score": 0, "reason": "评分失败"},
                "experience_score": {"score": 0, "reason": "评分失败"},
                "quality_score": {"score": 0, "reason": "评分失败"}
            }
        }
    
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
5. 城市名称要准确,
6. 城市提取规则如下: 
- 如果学校名称在 {self.universities_985} 和 {self.universities_211} 中，则提取学校所在城市
- 如果学校名称中包含城市名称，则提取城市名称.比如: 成都理工大学, 则提取城市为成都
- 如果上诉规则都未匹配到，则提取城市为null

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