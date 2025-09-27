"""
简历相关路由
处理简历上传、获取、删除等操作
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List

from ..models.resume_models import ResumeData, ResumeUploadResponse
from ..models.user_models import UserResponse, User
from ..services.resume_service import ResumeService
from ..utils.auth import get_current_user
from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/resumes", tags=["简历管理"])
resume_service = ResumeService()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    上传简历文件
    
    Args:
        file: 上传的文件
        current_user: 当前用户
        
    Returns:
        ResumeUploadResponse: 上传响应
    """
    try:
        # 验证文件类型
        allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="不支持的文件类型，请上传PDF、DOCX或TXT文件"
            )
        
        # 验证文件大小（限制为10MB）
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="文件大小不能超过10MB"
            )
        
        # 上传简历
        resume_data = await resume_service.upload_resume(
            file_content=file_content,
            filename=file.filename,
            user_id=current_user.id
        )
        
        logger.info(f"简历上传成功: {file.filename}, 用户: {current_user.email}")
        
        return ResumeUploadResponse(
            resume_id=resume_data.id,
            filename=resume_data.filename,
            status="success",
            message="简历上传成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"简历上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail="简历上传失败")


@router.get("/", response_model=List[ResumeData])
async def get_user_resumes(current_user: User = Depends(get_current_user)):
    """
    获取用户的所有简历
    
    Args:
        current_user: 当前用户
        
    Returns:
        List[ResumeData]: 简历列表
    """
    try:
        resumes = resume_service.get_user_resumes(current_user.id)
        return resumes
    except Exception as e:
        logger.error(f"获取简历列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取简历列表失败")


@router.get("/{resume_id}", response_model=ResumeData)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取指定简历
    
    Args:
        resume_id: 简历ID
        current_user: 当前用户
        
    Returns:
        ResumeData: 简历数据
    """
    try:
        resume = resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 验证简历属于当前用户
        if resume.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权访问此简历")
        
        return resume
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取简历失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取简历失败")


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    删除简历
    
    Args:
        resume_id: 简历ID
        current_user: 当前用户
        
    Returns:
        dict: 删除结果
    """
    try:
        # 先验证简历是否存在且属于当前用户
        resume = resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        if resume.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权删除此简历")
        
        # 删除简历
        success = resume_service.delete_resume(resume_id, current_user.id)
        if not success:
            raise HTTPException(status_code=500, detail="删除简历失败")
        
        logger.info(f"简历删除成功: {resume_id}, 用户: {current_user.email}")
        
        return {"message": "简历删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除简历失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除简历失败")
