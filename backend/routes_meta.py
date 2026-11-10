from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from competitions import canonical_name, match_competition, meta
from database import get_db
from models import EXPIRE_DAYS, Post

router = APIRouter()


@router.get("/meta")
def get_meta():
    """前端选项字典：比赛名录、角色标签、年级、阶段。"""
    return meta()


@router.get("/meta/competition-counts")
def competition_counts(db: Session = Depends(get_db)):
    """每场比赛当前有多少条在招的招募，给名录页显示「几队在招」。"""
    since = datetime.utcnow() - timedelta(days=EXPIRE_DAYS)
    rows = (
        db.query(Post.competition, func.count(Post.id))
        .filter(
            Post.status == "open",
            Post.competition.isnot(None),
            Post.competition != "",
            Post.created_at >= since,
        )
        .group_by(Post.competition)
        .all()
    )
    return {name: count for name, count in rows}


@router.get("/meta/competitions")
def search_competitions(q: Optional[str] = None, limit: int = Query(default=20, ge=1, le=100)):
    """按「市调」「正大杯」这类别名也能搜到同一场比赛。"""
    items = match_competition(q or "")
    return items[:limit]


@router.get("/meta/canonical")
def canonical(name: str):
    return {"name": canonical_name(name)}
