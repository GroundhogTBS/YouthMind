from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from models.database import get_db, init_db, ArticleModel, UserFavoriteModel
from routers.user import get_current_user, UserModel

logger = logging.getLogger(__name__)
router = APIRouter()

init_db()


class ArticleResponse(BaseModel):
    id: int
    category: str
    title: str
    summary: str
    coverImage: Optional[str]
    viewCount: int
    createdAt: str
    isFavorited: bool = False


class ArticleDetailResponse(BaseModel):
    id: int
    category: str
    title: str
    summary: str
    content: str
    coverImage: Optional[str]
    viewCount: int
    createdAt: str
    isFavorited: bool = False


CATEGORIES = [
    {"key": "emotion", "name": "情绪管理"},
    {"key": "stress", "name": "压力调节"},
    {"key": "relationship", "name": "人际关系"},
    {"key": "study", "name": "学习心理"},
    {"key": "growth", "name": "自我成长"}
]

DEFAULT_ARTICLES = [
    {
        "category": "emotion",
        "title": "如何应对考试焦虑",
        "summary": "考试焦虑是很多同学都会遇到的问题，本文将介绍几种有效的应对方法。",
        "content": "考试焦虑是很多同学都会遇到的问题。适度的焦虑可以帮助我们集中注意力，但过度的焦虑会影响发挥。\n\n## 认识考试焦虑\n\n考试焦虑主要表现为：心跳加速、手心出汗、大脑空白、注意力难以集中等。\n\n## 应对方法\n\n1. **充分准备**：提前复习，做好时间规划\n2. **放松训练**：深呼吸、肌肉放松法\n3. **积极暗示**：告诉自己\"我准备好了\"\n4. **合理作息**：保证充足睡眠\n\n记住，考试只是检验学习成果的一种方式，不是人生的全部。相信自己，你一定可以的！"
    },
    {
        "category": "stress",
        "title": "压力管理小技巧",
        "summary": "学会管理压力，让生活更轻松。这里有几个实用的小技巧分享给你。",
        "content": "压力是现代生活中不可避免的一部分，学会管理压力对身心健康都很重要。\n\n## 什么是压力？\n\n压力是身体对挑战或威胁的自然反应。适度的压力可以激发潜能，但过度的压力会影响健康。\n\n## 压力管理技巧\n\n1. **运动**：每天30分钟的有氧运动\n2. **冥想**：每天花10分钟静坐\n3. **社交**：与朋友家人交流\n4. **爱好**：培养一项兴趣爱好\n5. **睡眠**：保证7-8小时睡眠\n\n记住，寻求帮助是勇敢的表现，不是软弱。"
    },
    {
        "category": "relationship",
        "title": "如何与父母有效沟通",
        "summary": "与父母的沟通是很多青少年的困扰，本文教你几个实用的沟通技巧。",
        "content": "与父母的沟通是青少年成长过程中的重要课题。\n\n## 常见的沟通障碍\n\n- 代沟导致的理解差异\n- 表达方式不当\n- 情绪控制不好\n\n## 有效沟通技巧\n\n1. **选择合适的时机**：双方都平静时沟通\n2. **使用\"我\"的表达**：\"我感到...\"而不是\"你总是...\"\n3. **倾听**：认真听父母说话\n4. **表达感谢**：肯定父母的付出\n\n记住，父母也是普通人，他们也在学习如何与成长中的你相处。"
    },
    {
        "category": "study",
        "title": "提高学习效率的方法",
        "summary": "学习效率不高？试试这些科学的学习方法。",
        "content": "提高学习效率不仅能让你学得更好，还能腾出更多时间做自己喜欢的事。\n\n## 科学学习方法\n\n1. **番茄工作法**：25分钟专注+5分钟休息\n2. **间隔重复**：定期复习巩固记忆\n3. **主动学习**：做笔记、提问、讨论\n4. **环境管理**：减少干扰因素\n\n## 时间管理\n\n- 制定每日计划\n- 区分任务优先级\n- 避免拖延\n\n找到适合自己的学习方法，让学习变得更轻松！"
    },
    {
        "category": "growth",
        "title": "认识自我，接纳自我",
        "summary": "了解自己、接纳自己是成长的第一步。",
        "content": "自我认知是心理健康的基础。\n\n## 认识自我\n\n- 了解自己的性格特点\n- 认识自己的优势和不足\n- 明确自己的价值观和目标\n\n## 接纳自我\n\n1. **停止自我批评**：用友善的态度对待自己\n2. **接受不完美**：没有人是完美的\n3. **关注成长**：与过去的自己比较\n\n每个人都是独一无二的，学会欣赏自己的独特之处！"
    }
]


def init_default_articles(db: Session):
    count = db.query(ArticleModel).count()
    if count == 0:
        for article_data in DEFAULT_ARTICLES:
            article = ArticleModel(
                category=article_data["category"],
                title=article_data["title"],
                summary=article_data["summary"],
                content=article_data["content"],
                view_count=0,
                is_published=True,
                created_at=datetime.now()
            )
            db.add(article)
        db.commit()


@router.get("/categories", summary="获取文章分类")
async def get_categories():
    return CATEGORIES


@router.get("", response_model=List[ArticleResponse], summary="获取文章列表")
async def get_articles(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    init_default_articles(db)
    
    query = db.query(ArticleModel).filter(ArticleModel.is_published == True)
    
    if category:
        query = query.filter(ArticleModel.category == category)
    
    articles = query.order_by(ArticleModel.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        ArticleResponse(
            id=a.id,
            category=a.category,
            title=a.title,
            summary=a.summary,
            coverImage=a.cover_image,
            viewCount=a.view_count,
            createdAt=a.created_at.isoformat()
        )
        for a in articles
    ]


@router.get("/{article_id}", response_model=ArticleDetailResponse, summary="获取文章详情")
async def get_article(
    article_id: int,
    user: Optional[UserModel] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    article.view_count += 1
    db.commit()
    
    is_favorited = False
    if user:
        favorite = db.query(UserFavoriteModel).filter(
            UserFavoriteModel.user_id == user.id,
            UserFavoriteModel.article_id == article_id
        ).first()
        is_favorited = favorite is not None
    
    return ArticleDetailResponse(
        id=article.id,
        category=article.category,
        title=article.title,
        summary=article.summary,
        content=article.content,
        coverImage=article.cover_image,
        viewCount=article.view_count,
        createdAt=article.created_at.isoformat(),
        isFavorited=is_favorited
    )


@router.post("/{article_id}/favorite", summary="收藏文章")
async def favorite_article(
    article_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    article = db.query(ArticleModel).filter(ArticleModel.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    existing = db.query(UserFavoriteModel).filter(
        UserFavoriteModel.user_id == user.id,
        UserFavoriteModel.article_id == article_id
    ).first()
    
    if existing:
        return {"success": True, "message": "已收藏"}
    
    favorite = UserFavoriteModel(
        user_id=user.id,
        article_id=article_id,
        created_at=datetime.now()
    )
    db.add(favorite)
    db.commit()
    
    return {"success": True, "message": "收藏成功"}


@router.delete("/{article_id}/favorite", summary="取消收藏")
async def unfavorite_article(
    article_id: int,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    favorite = db.query(UserFavoriteModel).filter(
        UserFavoriteModel.user_id == user.id,
        UserFavoriteModel.article_id == article_id
    ).first()
    
    if favorite:
        db.delete(favorite)
        db.commit()
    
    return {"success": True, "message": "已取消收藏"}


@router.get("/user/favorites", response_model=List[ArticleResponse], summary="获取用户收藏")
async def get_user_favorites(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    favorites = db.query(UserFavoriteModel).filter(
        UserFavoriteModel.user_id == user.id
    ).order_by(UserFavoriteModel.created_at.desc()).all()
    
    articles = []
    for fav in favorites:
        article = db.query(ArticleModel).filter(ArticleModel.id == fav.article_id).first()
        if article:
            articles.append(ArticleResponse(
                id=article.id,
                category=article.category,
                title=article.title,
                summary=article.summary,
                coverImage=article.cover_image,
                viewCount=article.view_count,
                createdAt=article.created_at.isoformat(),
                isFavorited=True
            ))
    
    return articles
