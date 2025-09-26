"""
分析相关路由
处理简历分析请求和结果获取
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import List

from ..models.resume_models import AnalysisRequest, AnalysisResponse, AnalysisResult
from ..models.user_models import UserResponse
from ..services.resume_service import ResumeService
from ..services.ai_service import AIService
from ..utils.auth import get_current_user
from ..utils.logger import get_logger
from ..config.settings import get_settings

logger = get_logger(__name__)

router = APIRouter(prefix="/analysis", tags=["简历分析"])
resume_service = ResumeService()
settings = get_settings()


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def analyze_resume(
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    分析简历
    
    Args:
        analysis_request: 分析请求数据
        background_tasks: 后台任务
        current_user: 当前用户
        
    Returns:
        AnalysisResponse: 分析响应
    """
    try:
        # 验证简历是否存在且属于当前用户
        resume = resume_service.get_resume(analysis_request.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        if resume.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权分析此简历")
        
        # 创建分析任务
        analysis_id = f"analysis_{analysis_request.resume_id}_{analysis_request.analysis_type}"
        
        # 添加后台任务
        background_tasks.add_task(
            _perform_analysis,
            analysis_id,
            analysis_request,
            current_user.id
        )
        
        logger.info(f"简历分析任务已创建: {analysis_id}, 用户: {current_user.email}")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="processing",
            message="分析任务已开始，请稍后查询结果"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建分析任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="创建分析任务失败")


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_result(
    analysis_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取分析结果
    
    Args:
        analysis_id: 分析ID
        current_user: 当前用户
        
    Returns:
        AnalysisResponse: 分析结果
    """
    try:
        # 这里应该从数据库获取分析结果
        # 为了演示，返回模拟结果
        result = AnalysisResult(
            resume_id=analysis_id.split("_")[1],
            analysis_type="comprehensive",
            status="completed",
            overall_score=85.0,
            strengths=["经验丰富", "技能全面", "项目经验丰富"],
            weaknesses=["缺乏证书", "英语水平一般", "管理经验不足"],
            recommendations=["考取相关证书", "提高英语水平", "参与管理项目"]
        )
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="completed",
            result=result,
            message="分析完成"
        )
        
    except Exception as e:
        logger.error(f"获取分析结果失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取分析结果失败")


@router.get("/", response_model=List[AnalysisResult])
async def get_user_analyses(current_user: UserResponse = Depends(get_current_user)):
    """
    获取用户的所有分析结果
    
    Args:
        current_user: 当前用户
        
    Returns:
        List[AnalysisResult]: 分析结果列表
    """
    try:
        # 这里应该从数据库获取用户的所有分析结果
        # 为了演示，返回空列表
        return []
        
    except Exception as e:
        logger.error(f"获取分析列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取分析列表失败")


async def _perform_analysis(analysis_id: str, analysis_request: AnalysisRequest, user_id: str):
    """
    执行分析任务（后台任务）
    
    Args:
        analysis_id: 分析ID
        analysis_request: 分析请求
        user_id: 用户ID
    """
    try:
        logger.info(f"开始执行分析任务: {analysis_id}")
        
        # 获取简历数据
        resume = resume_service.get_resume(analysis_request.resume_id)
        if not resume:
            logger.error(f"简历不存在: {analysis_request.resume_id}")
            return
        
        # 初始化AI服务
        ai_service = AIService(
            api_key=settings.openai_api_key,
            model_name=settings.openai_model
        )
        
        # 执行分析
        result = await ai_service.analyze_resume(
            resume_data=resume,
            analysis_type=analysis_request.analysis_type,
            custom_prompt=analysis_request.custom_prompt,
            job_requirements=analysis_request.job_requirements
        )
        
        # 保存分析结果到数据库
        # 这里应该保存到数据库
        logger.info(f"分析任务完成: {analysis_id}")
        
    except Exception as e:
        logger.error(f"分析任务执行失败: {analysis_id}, 错误: {str(e)}")
