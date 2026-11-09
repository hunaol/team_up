from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Post, User, effective_status

router = APIRouter()


def summarize(posts) -> Dict:
    """统计帖子状态分布、参与人数与招募成功率。"""
    dist = {"open": 0, "full": 0, "down": 0, "expired": 0}
    for p in posts:
        dist[effective_status(p)] += 1
    denom = dist["full"] + dist["open"]
    return {
        "dist": dist,
        "participants": sum((p.need_num or 0) for p in posts),
        "success_rate": round(dist["full"] * 100 / denom) if denom else 0,
        "active_count": dist["open"],
    }


@router.get("/stats/overview")
def overview(db: Session = Depends(get_db)):
    """首页数据卡片（无需登录）。"""
    posts = db.query(Post).all()
    stat = summarize(posts)
    return {
        "total_posts": len(posts),
        "participants": stat["participants"],
        "active_posts": stat["active_count"],
        "success_rate": stat["success_rate"],
        "user_count": db.query(User).count(),
        "updated_at": datetime.utcnow().isoformat(),
    }
