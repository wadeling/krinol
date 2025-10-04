"""
简历相关路由
处理简历上传、获取、删除等操作
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks, Query
from typing import List, Optional
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.resume_models import ResumeData, ResumeUploadResponse, PaginatedResumeResponse
from ..models.user_models import UserResponse
from ..services.user_service import User
from ..services.resume_service import ResumeService
from ..services.ai_service import AIService
from ..utils.auth import get_current_user
from ..utils.logger import get_logger
from ..utils.file_processor import FileProcessor
from ..database import get_db

logger = get_logger(__name__)
logger.info("简历路由模块加载完成")

router = APIRouter(prefix="/resumes", tags=["简历管理"])


@router.post("/upload", response_model=List[ResumeUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传简历文件并启动异步处理（支持多文件）
    
    Args:
        background_tasks: FastAPI后台任务
        files: 上传的文件列表
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        List[ResumeUploadResponse]: 上传响应列表
    """
    try:
        logger.info(f"开始上传简历文件，文件数量: {len(files)}")
        logger.info(f"当前用户: {current_user.username if current_user else 'None'}")

        results = []
        
        for file in files:
            try:
                # 验证文件类型（只支持PDF）
                if file.content_type != "application/pdf":
                    results.append(ResumeUploadResponse(
                        resume_id="",
                        filename=file.filename,
                        status="failed",
                        message="只支持PDF格式的文件"
                    ))
                    continue
                
                # 验证文件大小（限制为10MB）
                file_content = await file.read()
                if len(file_content) > 10 * 1024 * 1024:
                    results.append(ResumeUploadResponse(
                        resume_id="",
                        filename=file.filename,
                        status="failed",
                        message="文件大小不能超过10MB"
                    ))
                    continue
                
                # 生成唯一文件名
                file_id = str(uuid.uuid4())
                file_extension = os.path.splitext(file.filename)[1]
                safe_filename = f"{file_id}{file_extension}"
                
                # 确保数据目录存在
                data_dir = "/app/data"
                os.makedirs(data_dir, exist_ok=True)
                
                # 保存文件到磁盘
                file_path = os.path.join(data_dir, safe_filename)
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                logger.info(f"文件保存成功: {file_path}")

                # 创建简历记录
                resume_data = ResumeData(
                    id=file_id,
                    filename=file.filename,
                    format="pdf",
                    content="",  # 将在异步任务中填充
                    file_size=len(file_content),
                    user_id=str(current_user.id)
                )
                
                # 保存到数据库
                resume_service = ResumeService(db=db)
                resume_service.create_resume(resume_data)
                
                # 启动异步处理任务
                background_tasks.add_task(
                    process_resume_async,
                    file_id=file_id,
                    file_path=file_path,
                    user_id=str(current_user.id)
                )
                
                results.append(ResumeUploadResponse(
                    resume_id=file_id,
                    filename=file.filename,
                    status="uploaded",
                    message="文件上传成功，正在处理中..."
                ))
                
                logger.info(f"简历上传成功: {file.filename}, 用户: {current_user.email}, 文件ID: {file_id}")
                
            except Exception as e:
                logger.error(f"处理文件 {file.filename} 时出错: {str(e)}")
                results.append(ResumeUploadResponse(
                    resume_id="",
                    filename=file.filename,
                    status="failed",
                    message=f"文件处理失败: {str(e)}"
                ))
        
        return results
        
    except Exception as e:
        logger.error(f"简历上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail="简历上传失败")


async def process_resume_async(file_id: str, file_path: str, user_id: str):
    """
    异步处理简历文件
    
    Args:
        file_id: 文件ID
        file_path: 文件路径
        user_id: 用户ID
    """
    try:
        logger.info(f"开始处理简历文件: {file_id}")
        
        # 获取数据库会话
        from ..database import SessionLocal
        db = SessionLocal()
        resume_service = ResumeService(db=db)
        
        try:
            # 1. 转换PDF为Markdown
            file_processor = FileProcessor()
            markdown_content = await file_processor.pdf_to_markdown(file_path)
            logger.info(f"PDF转换为Markdown完成: {markdown_content}")
            
            # 2. 使用AI提取信息
            try:
                ai_service = AIService()
                extracted_info = await ai_service.extract_resume_info(markdown_content)
            except Exception as e:
                logger.warning(f"AI服务调用失败，使用默认信息: {str(e)}")
                # 使用默认信息
                extracted_info = {
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
            
            # 3. 使用AI进行简历评分
            try:
                scoring_result = await ai_service.score_resume(markdown_content, extracted_info)
                logger.info(f"简历评分完成: {scoring_result}")
            except Exception as e:
                logger.warning(f"AI评分失败，使用默认评分: {str(e)}")
                # 使用默认评分
                scoring_result = {
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
            
            # 4. 更新数据库记录
            resume_service.update_resume_content(
                resume_id=file_id,
                content=markdown_content,
                extracted_info=extracted_info,
                score=scoring_result.get("total_score", 0),
                score_detail=scoring_result.get("score_details", {})
            )
            
            logger.info(f"简历处理完成: {file_id}")
            
        except Exception as e:
            logger.error(f"简历处理失败: {file_id}, 错误: {str(e)}")
            # 更新状态为失败
            resume_service.update_resume_status(file_id, "failed", str(e))
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"简历处理失败: {file_id}, 错误: {str(e)}")


@router.get("/", response_model=PaginatedResumeResponse)
async def get_user_resumes(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=100, description="每页记录数，最大100"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的所有简历（支持分页）
    
    Args:
        page: 页码（从1开始）
        page_size: 每页记录数（1-100）
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        PaginatedResumeResponse: 分页简历响应
    """
    try:
        resume_service = ResumeService(db=db)
        resumes, total_count = resume_service.get_user_resumes(
            str(current_user.id), 
            page=page, 
            page_size=page_size
        )
        
        # 计算分页信息
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        return PaginatedResumeResponse(
            items=resumes,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
    except Exception as e:
        logger.error(f"获取简历列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取简历列表失败")


@router.get("/{resume_id}", response_model=ResumeData)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定简历
    
    Args:
        resume_id: 简历ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        ResumeData: 简历数据
    """
    try:
        resume_service = ResumeService(db=db)
        resume = resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        # 验证简历属于当前用户
        if resume.user_id != str(current_user.id):
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除简历
    
    Args:
        resume_id: 简历ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        dict: 删除结果
    """
    try:
        resume_service = ResumeService(db=db)
        
        # 先验证简历是否存在且属于当前用户
        resume = resume_service.get_resume(resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="简历不存在")
        
        if resume.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="无权删除此简历")
        
        # 删除简历
        success = resume_service.delete_resume(resume_id, str(current_user.id))
        if not success:
            raise HTTPException(status_code=500, detail="删除简历失败")
        
        logger.info(f"简历删除成功: {resume_id}, 用户: {current_user.email}")
        
        return {"message": "简历删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除简历失败: {str(e)}")
        raise HTTPException(status_code=500, detail="删除简历失败")
