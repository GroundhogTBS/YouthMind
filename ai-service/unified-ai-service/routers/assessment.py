from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
import json
from datetime import datetime

from models.database import get_db, init_db, AssessmentModel
from routers.user import get_current_user, UserModel
from core.constants import ASSESSMENT_SCALES

logger = logging.getLogger(__name__)
router = APIRouter()

init_db()


class SubmitAssessmentRequest(BaseModel):
    scaleType: str
    answers: List[int]


class AssessmentResponse(BaseModel):
    id: int
    scaleType: str
    scaleName: str
    totalScore: int
    resultLevel: str
    resultDescription: str
    createdAt: str


class ScaleQuestion(BaseModel):
    id: int
    text: str
    options: List[str]


class ScaleResponse(BaseModel):
    type: str
    name: str
    description: str
    questions: List[ScaleQuestion]


@router.get("/scales", summary="获取可用量表列表")
async def get_scales():
    scales = [
        {
            "type": "phq9",
            "name": "抑郁自评量表(PHQ-9)",
            "description": "评估抑郁症状严重程度",
            "questionCount": 9,
            "estimatedTime": "3-5分钟"
        },
        {
            "type": "gad7",
            "name": "焦虑自评量表(GAD-7)",
            "description": "评估焦虑症状严重程度",
            "questionCount": 7,
            "estimatedTime": "2-3分钟"
        },
        {
            "type": "pss10",
            "name": "压力感知量表(PSS-10)",
            "description": "评估心理压力水平",
            "questionCount": 10,
            "estimatedTime": "3-5分钟"
        },
        {
            "type": "swls",
            "name": "生活满意度量表(SWLS)",
            "description": "评估生活满意度",
            "questionCount": 5,
            "estimatedTime": "2分钟"
        }
    ]
    return scales


@router.get("/scales/{scale_type}", response_model=ScaleResponse, summary="获取量表详情")
async def get_scale(scale_type: str):
    scales_data = {
        "phq9": {
            "name": "抑郁自评量表(PHQ-9)",
            "description": "请根据过去两周的实际感受作答",
            "questions": [
                {"id": 1, "text": "做事时提不起劲或没有兴趣", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 2, "text": "感到心情低落、沮丧或绝望", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 3, "text": "入睡困难、易醒或睡眠过多", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 4, "text": "感觉疲倦或没有活力", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 5, "text": "食欲不振或吃得太多", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 6, "text": "觉得自己很糟，或觉得自己很失败", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 7, "text": "对事物专注有困难", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 8, "text": "动作、说话速度缓慢，或相反", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 9, "text": "有不如死掉或用某种方式伤害自己的念头", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]}
            ]
        },
        "gad7": {
            "name": "焦虑自评量表(GAD-7)",
            "description": "请根据过去两周的实际感受作答",
            "questions": [
                {"id": 1, "text": "感到紧张、焦虑或急切", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 2, "text": "不能停止或控制担忧", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 3, "text": "对各种各样的事情担忧过多", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 4, "text": "难以放松", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 5, "text": "由于不安而无法静坐", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 6, "text": "变得容易烦恼或急躁", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]},
                {"id": 7, "text": "感到似乎将有可怕的事情发生而害怕", "options": ["完全不会", "好几天", "一半以上的天数", "几乎每天"]}
            ]
        },
        "pss10": {
            "name": "压力感知量表(PSS-10)",
            "description": "请根据过去一个月的情况作答",
            "questions": [
                {"id": 1, "text": "因为发生了意外之事而感到心烦意乱", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 2, "text": "感觉无法控制生活中重要的事情", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 3, "text": "感到紧张和压力", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 4, "text": "对处理个人问题没有信心", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 5, "text": "感觉事情发展对自己不利", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 6, "text": "发现无法应付自己必须做的事情", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 7, "text": "无法控制生活中的烦恼", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 8, "text": "感觉经常被困难堆得喘不过气", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 9, "text": "对自己处理问题的方式感到满意", "options": ["从不", "偶尔", "有时", "经常", "总是"]},
                {"id": 10, "text": "感觉事情都在自己的掌控之中", "options": ["从不", "偶尔", "有时", "经常", "总是"]}
            ]
        },
        "swls": {
            "name": "生活满意度量表(SWLS)",
            "description": "请根据您对生活的总体感受作答",
            "questions": [
                {"id": 1, "text": "在大多数方面，我的生活接近我的理想", "options": ["非常不同意", "不同意", "有点不同意", "中立", "有点同意", "同意", "非常同意"]},
                {"id": 2, "text": "我的生活条件非常好", "options": ["非常不同意", "不同意", "有点不同意", "中立", "有点同意", "同意", "非常同意"]},
                {"id": 3, "text": "我对我的生活感到满意", "options": ["非常不同意", "不同意", "有点不同意", "中立", "有点同意", "同意", "非常同意"]},
                {"id": 4, "text": "到目前为止，我已经得到了我想要的东西", "options": ["非常不同意", "不同意", "有点不同意", "中立", "有点同意", "同意", "非常同意"]},
                {"id": 5, "text": "如果可以重新来过，我几乎不会改变任何东西", "options": ["非常不同意", "不同意", "有点不同意", "中立", "有点同意", "同意", "非常同意"]}
            ]
        }
    }
    
    if scale_type not in scales_data:
        raise HTTPException(status_code=404, detail="量表不存在")
    
    scale = scales_data[scale_type]
    return ScaleResponse(
        type=scale_type,
        name=scale["name"],
        description=scale["description"],
        questions=[ScaleQuestion(**q) for q in scale["questions"]]
    )


def calculate_result(scale_type: str, answers: List[int]) -> Dict[str, Any]:
    total_score = sum(answers)
    
    if scale_type == "phq9":
        if total_score <= 4:
            level, desc = "正常", "您的情绪状态良好，继续保持积极的生活方式。"
        elif total_score <= 9:
            level, desc = "轻度", "您可能有轻微的抑郁症状，建议多与朋友交流，适当运动。"
        elif total_score <= 14:
            level, desc = "中度", "您可能有中度抑郁症状，建议寻求专业心理咨询帮助。"
        elif total_score <= 19:
            level, desc = "中重度", "您可能有较严重的抑郁症状，强烈建议尽快咨询心理医生。"
        else:
            level, desc = "重度", "您的抑郁症状较严重，请尽快寻求专业帮助。如有需要，请拨打心理援助热线：400-161-9995"
    
    elif scale_type == "gad7":
        if total_score <= 4:
            level, desc = "正常", "您的焦虑水平正常，继续保持放松的心态。"
        elif total_score <= 9:
            level, desc = "轻度", "您可能有轻微的焦虑症状，建议学习放松技巧。"
        elif total_score <= 14:
            level, desc = "中度", "您可能有中度焦虑症状，建议寻求专业帮助。"
        else:
            level, desc = "重度", "您的焦虑症状较严重，请尽快咨询专业人士。"
    
    elif scale_type == "pss10":
        if total_score <= 13:
            level, desc = "低压力", "您的压力水平较低，心理状态良好。"
        elif total_score <= 26:
            level, desc = "中等压力", "您承受着一定压力，建议适当休息和放松。"
        else:
            level, desc = "高压力", "您承受着较大压力，建议寻求支持和帮助。"
    
    elif scale_type == "swls":
        if total_score <= 9:
            level, desc = "非常不满意", "您对生活不太满意，建议寻求改变或专业帮助。"
        elif total_score <= 14:
            level, desc = "不满意", "您对生活有些不满意，可以尝试设定小目标改善生活。"
        elif total_score <= 19:
            level, desc = "一般满意", "您对生活基本满意，还有提升空间。"
        else:
            level, desc = "非常满意", "您对生活很满意，请继续保持积极态度。"
    
    else:
        level, desc = "未知", "无法评估结果"
    
    return {"total_score": total_score, "level": level, "description": desc}


@router.post("/submit", response_model=AssessmentResponse, summary="提交测评")
async def submit_assessment(
    request: SubmitAssessmentRequest,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scale_names = {
        "phq9": "抑郁自评量表(PHQ-9)",
        "gad7": "焦虑自评量表(GAD-7)",
        "pss10": "压力感知量表(PSS-10)",
        "swls": "生活满意度量表(SWLS)"
    }
    
    if request.scaleType not in scale_names:
        raise HTTPException(status_code=400, detail="无效的量表类型")
    
    result = calculate_result(request.scaleType, request.answers)
    
    assessment = AssessmentModel(
        user_id=user.id,
        scale_type=request.scaleType,
        scale_name=scale_names[request.scaleType],
        total_score=result["total_score"],
        result_level=result["level"],
        result_description=result["description"],
        answers=json.dumps(request.answers),
        created_at=datetime.now()
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    return AssessmentResponse(
        id=assessment.id,
        scaleType=assessment.scale_type,
        scaleName=assessment.scale_name,
        totalScore=assessment.total_score,
        resultLevel=assessment.result_level,
        resultDescription=assessment.result_description,
        createdAt=assessment.created_at.isoformat()
    )


@router.get("/history", response_model=List[AssessmentResponse], summary="获取测评历史")
async def get_assessment_history(
    limit: int = 10,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessments = db.query(AssessmentModel).filter(
        AssessmentModel.user_id == user.id
    ).order_by(AssessmentModel.created_at.desc()).limit(limit).all()
    
    return [
        AssessmentResponse(
            id=a.id,
            scaleType=a.scale_type,
            scaleName=a.scale_name,
            totalScore=a.total_score,
            resultLevel=a.result_level,
            resultDescription=a.result_description,
            createdAt=a.created_at.isoformat()
        )
        for a in assessments
    ]


@router.get("/{assessment_id}", summary="获取测评详情")
async def get_assessment(
    assessment_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(AssessmentModel).filter(
        AssessmentModel.id == assessment_id,
        AssessmentModel.user_id == user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="测评记录不存在")
    
    return {
        "id": assessment.id,
        "scaleType": assessment.scale_type,
        "scaleName": assessment.scale_name,
        "totalScore": assessment.total_score,
        "resultLevel": assessment.result_level,
        "resultDescription": assessment.result_description,
        "answers": json.loads(assessment.answers),
        "createdAt": assessment.created_at.isoformat()
    }
