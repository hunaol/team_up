from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from auth import hash_password, issue_token, require_admin
from database import get_db
from models import EXPIRE_DAYS, Admin, Post, Token, User, effective_status
from routes_post import post_out
from routes_stats import summarize
from schemas import AdminLoginIn, UserUpdateIn

router = APIRouter()


def _pct(cur: int, prev: int) -> int:
    """环比增长率（%），上一周期为空时按 100% 处理。"""
    if prev <= 0:
        return 100 if cur > 0 else 0
    return round((cur - prev) * 100 / prev)


def _window_rate(posts) -> int:
    full = sum(1 for p in posts if effective_status(p) == "full")
    open_count = sum(1 for p in posts if effective_status(p) == "open")
    denom = full + open_count
    return round(full * 100 / denom) if denom else 0


@router.post("/login")
def admin_login(body: AdminLoginIn, db: Session = Depends(get_db)):
    a = db.query(Admin).filter(Admin.username == body.username).first()
    if not a or hash_password(body.password, a.salt) != a.password_hash:
        raise HTTPException(status_code=401, detail="账号或密码不正确")
    return {"token": issue_token(db, is_admin=True)}


@router.get("/stats")
def stats(
    range_days: int = Query(default=30, alias="range"),
    _: Token = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if range_days not in (7, 30, 90):
        range_days = 30
    now = datetime.utcnow()
    start = (now - timedelta(days=range_days - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    prev_start = start - timedelta(days=range_days)

    expire_before = now - timedelta(days=EXPIRE_DAYS)
    user_count = db.query(func.count(User.id)).scalar()
    post_total = db.query(func.count(Post.id)).scalar()
    team_count = db.query(func.count(Post.id)).filter(Post.type == "team").scalar()
    join_count = db.query(func.count(Post.id)).filter(Post.type == "join").scalar()
    open_count = (
        db.query(func.count(Post.id))
        .filter(Post.status == "open", Post.created_at > expire_before)
        .scalar()
    )

    posts_all = db.query(Post).all()
    summary = summarize(posts_all)
    dist = summary["dist"]

    cur_posts = [p for p in posts_all if p.created_at >= start]
    prev_posts = [p for p in posts_all if prev_start <= p.created_at < start]
    cur_users = (
        db.query(func.count(User.id)).filter(User.created_at >= start).scalar() or 0
    )
    prev_users = (
        db.query(func.count(User.id))
        .filter(User.created_at >= prev_start, User.created_at < start)
        .scalar()
        or 0
    )
    cur_participants = sum((p.need_num or 0) for p in cur_posts)
    prev_participants = sum((p.need_num or 0) for p in prev_posts)

    trend = []
    for i in range(range_days):
        day = start + timedelta(days=i)
        day_posts = [p for p in posts_all if day <= p.created_at < day + timedelta(days=1)]
        trend.append(
            {
                "date": day.strftime("%m-%d"),
                "posts": len(day_posts),
                "participants": sum(x.need_num or 0 for x in day_posts),
            }
        )

    return {
        "range": range_days,
        "user_count": user_count,
        "users_new": cur_users,
        "post_total": post_total,
        "posts_in_range": len(cur_posts),
        "team_count": team_count,
        "join_count": join_count,
        "open_count": open_count,
        "participants_total": summary["participants"],
        "participants_in_range": cur_participants,
        "success_rate": summary["success_rate"],
        "status_distribution": dist,
        "growth": {
            "users": _pct(cur_users, prev_users),
            "posts": _pct(len(cur_posts), len(prev_posts)),
            "participants": _pct(cur_participants, prev_participants),
            "success_rate": _window_rate(cur_posts) - _window_rate(prev_posts),
        },
        "trend": trend,
    }


@router.get("/users")
def list_users(
    q: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    _: Token = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if status == "active":
        query = query.filter(User.active == True)  # noqa: E712
    elif status == "disabled":
        query = query.filter(User.active == False)  # noqa: E712
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.student_id.like(like), User.name.like(like)))
    total = query.count()
    page = max(1, page)
    page_size = min(50, max(1, page_size))
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    counts = dict(
        db.query(Post.user_id, func.count(Post.id)).group_by(Post.user_id).all()
    )
    active_total = db.query(func.count(User.id)).filter(User.active == True).scalar()  # noqa: E712
    all_total = db.query(func.count(User.id)).scalar()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "counts": {"all": all_total, "active": active_total, "disabled": all_total - active_total},
        "items": [
            {
                "id": u.id,
                "student_id": u.student_id,
                "name": u.name,
                "role": "学生",
                "active": u.active,
                "post_count": counts.get(u.id, 0),
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ],
    }


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    body: UserUpdateIn,
    _: Token = Depends(require_admin),
    db: Session = Depends(get_db),
):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    u.name = body.name.strip()
    db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, _: Token = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    u.active = False
    db.query(Token).filter(Token.user_id == u.id, Token.is_admin == False).delete()  # noqa: E712
    db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/activate")
def activate_user(user_id: int, _: Token = Depends(require_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    u.active = True
    db.commit()
    return {"ok": True}


@router.get("/posts")
def list_posts(
    type: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
    _: Token = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Post)
    if type in ("team", "join"):
        query = query.filter(Post.type == type)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Post.title.like(like), Post.description.like(like)))
    posts = query.order_by(Post.created_at.desc()).all()
    result = [post_out(p, True) for p in posts]
    if status in ("open", "full", "down", "expired"):
        result = [r for r in result if r["status"] == status]
    return result


@router.post("/posts/{post_id}/takedown")
def takedown_post(post_id: int, _: Token = Depends(require_admin), db: Session = Depends(get_db)):
    p = db.get(Post, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if effective_status(p) not in ("open", "full"):
        raise HTTPException(status_code=400, detail="当前状态不可下架")
    p.status = "down"
    db.commit()
    return post_out(p, True)
