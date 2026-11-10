from datetime import datetime, timedelta
from typing import Optional

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth import get_optional_user, is_admin_viewer, require_user
from competitions import GRADE_LABEL, ROLE_LABEL, canonical_name
from database import get_db
from matching import score_for_candidate, score_for_my_team
from models import EXPIRE_DAYS, Application, Favorite, Message, Post, User, effective_status
from schemas import ApplyIn, PostIn, PostUpdateIn, check_contact_format, description_text

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _split(value: Optional[str]) -> list:
    if not value:
        return []
    return [x.strip() for x in str(value).split(",") if x.strip()]


def _join(values) -> str:
    return ",".join([v for v in (values or []) if v])


def _profile_payload(user: Optional[User]) -> Optional[dict]:
    if not user:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "grade": user.grade or "",
        "major": user.major or "",
        "skills": _split(user.skills),
        "bio": user.bio or "",
        "open_to_match": bool(user.open_to_match),
    }


def _viewer_team_post(db: Session, user: Optional[User]) -> Optional[Post]:
    """当前用户最近一条还在招募中的「找队友」帖，用于反向匹配。"""
    if not user:
        return None
    return (
        db.query(Post)
        .filter(
            Post.user_id == user.id,
            Post.type == "team",
            Post.status == "open",
            Post.created_at > datetime.utcnow() - timedelta(days=EXPIRE_DAYS),
        )
        .order_by(Post.created_at.desc())
        .first()
    )


def compute_match(post: Post, viewer: Optional[User], my_team: Optional[Post]) -> Optional[dict]:
    if not viewer or post.user_id == viewer.id:
        return None
    if post.type == "team":
        result = score_for_candidate(viewer, post, ROLE_LABEL, GRADE_LABEL)
    else:
        result = score_for_my_team(post, my_team) if my_team else None
    if not result:
        return None
    result["direction"] = "candidate" if post.type == "team" else "team"
    return result


def post_out(
    p: Post,
    include_contact: bool,
    favorited: bool = False,
    viewer: Optional[User] = None,
    my_team: Optional[Post] = None,
    applied: Optional[bool] = None,
) -> dict:
    return {
        "id": p.id,
        "type": p.type,
        "title": p.title,
        "description": p.description,
        "description_text": description_text(p.description),
        "need_num": p.need_num,
        "contact_type": p.contact_type,
        "contact": p.contact if include_contact else None,
        "deadline": p.deadline,
        "image": p.image,
        "author_id": p.user_id,
        "author_name": p.author.name,
        "status": effective_status(p),
        "views": p.views or 0,
        "is_favorite": favorited,
        "competition": p.competition or "",
        "roles": _split(p.roles),
        "grade_req": _split(p.grade_req),
        "major_req": p.major_req or "",
        "stage": p.stage or "",
        "match": compute_match(p, viewer, my_team),
        "has_applied": applied,
        "created_at": p.created_at.isoformat(),
    }


def _favorite_ids(db: Session, user: Optional[User]) -> set:
    if not user:
        return set()
    rows = db.query(Favorite.post_id).filter(Favorite.user_id == user.id).all()
    return {r[0] for r in rows}


def _applied_ids(db: Session, user: Optional[User]) -> set:
    if not user:
        return set()
    rows = db.query(Application.post_id).filter(Application.user_id == user.id).all()
    return {r[0] for r in rows}


@router.get("/posts")
def list_posts(
    type: Optional[str] = None,
    q: Optional[str] = None,
    competition: Optional[str] = None,
    role: Optional[str] = None,
    grade: Optional[str] = None,
    stage: Optional[str] = None,
    major: Optional[str] = None,
    sort: Optional[str] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    query = db.query(Post).filter(Post.status.in_(["open", "full"]))
    query = query.filter(Post.created_at > datetime.utcnow() - timedelta(days=EXPIRE_DAYS))
    if type in ("team", "join"):
        query = query.filter(Post.type == type)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Post.title.like(like), Post.description.like(like)))
    if competition:
        query = query.filter(Post.competition == canonical_name(competition))
    if role:
        query = query.filter(Post.roles.like(f"%{role}%"))
    if stage:
        query = query.filter(Post.stage == stage)
    if grade:
        # 明确限定了年级的要命中；没写年级要求的视为「不限」
        query = query.filter(or_(Post.grade_req == "", Post.grade_req.like(f"%{grade}%")))
    if major:
        query = query.filter(or_(Post.major_req == "", Post.major_req.like(f"%{major}%")))

    posts = query.order_by(Post.created_at.desc()).all()
    favs = _favorite_ids(db, user)
    applied = _applied_ids(db, user)
    my_team = _viewer_team_post(db, user)
    out = [
        post_out(p, user is not None, p.id in favs, user, my_team, p.id in applied if user else None)
        for p in posts
    ]
    if sort == "match":
        out.sort(key=lambda x: (-((x.get("match") or {}).get("score") or 0), x["created_at"]))
    return out


@router.get("/recommended")
def recommended(
    limit: int = 12,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    """按个人资料排序的推荐池（不含自己发的帖）。"""
    posts = (
        db.query(Post)
        .filter(
            Post.status == "open",
            Post.created_at > datetime.utcnow() - timedelta(days=EXPIRE_DAYS),
            Post.user_id != user.id,
        )
        .order_by(Post.created_at.desc())
        .limit(120)
        .all()
    )
    my_team = _viewer_team_post(db, user)
    favs = _favorite_ids(db, user)
    out = [post_out(p, True, p.id in favs, user, my_team) for p in posts]
    out = [x for x in out if x.get("match")]
    out.sort(key=lambda x: -x["match"]["score"])
    return out[: max(1, min(limit, 50))]


@router.get("/my/posts")
def my_posts(user: User = Depends(require_user), db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .filter(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    favs = _favorite_ids(db, user)
    return [post_out(p, True, p.id in favs, user) for p in posts]


@router.get("/my/favorites")
def my_favorites(user: User = Depends(require_user), db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .join(Favorite, Favorite.post_id == Post.id)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    visible = [
        p for p in posts if p.status != "down" and effective_status(p) != "expired"
    ]
    return [post_out(p, True, True, user) for p in visible]


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    user: Optional[User] = Depends(get_optional_user),
    admin_viewer: bool = Depends(is_admin_viewer),
    db: Session = Depends(get_db),
):
    p = db.get(Post, post_id)
    if not p:
        raise HTTPException(status_code=404, detail="帖子不存在")
    # 已下架的帖子仅发布者本人可见（便于在我的发布中查看/编辑）
    if p.status == "down" and (not user or user.id != p.user_id):
        raise HTTPException(status_code=404, detail="帖子不存在")
    st = effective_status(p)
    if st == "expired" and (not user or user.id != p.user_id):
        raise HTTPException(status_code=404, detail="帖子不存在")
    p.views = (p.views or 0) + 1
    db.commit()
    favorited = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.post_id == p.id)
        .first()
        is not None
        if user
        else False
    )
    applied = (
        db.query(Application)
        .filter(Application.user_id == user.id, Application.post_id == p.id)
        .first()
        is not None
        if user
        else None
    )
    data = post_out(
        p,
        user is not None or admin_viewer,
        favorited,
        user,
        _viewer_team_post(db, user),
        applied,
    )
    data["author"] = _profile_payload(p.author)
    if user and user.id == p.user_id:
        data["applicant_count"] = (
            db.query(Application)
            .filter(Application.post_id == p.id, Application.status == "pending")
            .count()
        )
    return data


@router.post("/posts")
def create_post(body: PostIn, user: User = Depends(require_user), db: Session = Depends(get_db)):
    p = Post(
        user_id=user.id,
        type=body.type,
        title=body.title,
        description=body.description,
        need_num=body.need_num,
        contact_type=body.contact_type,
        contact=body.contact,
        deadline=body.deadline,
        image=body.image or None,
        competition=canonical_name(body.competition or ""),
        roles=_join(body.roles),
        grade_req=_join(body.grade_req),
        major_req=(body.major_req or "").strip(),
        stage=body.stage or "",
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return post_out(p, True)


@router.post("/uploads")
async def upload_image(file: UploadFile = File(...), user: User = Depends(require_user)):
    ext = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if not ext:
        raise HTTPException(status_code=400, detail="仅支持 jpg / png / webp / gif 图片")
    data = await file.read()
    if len(data) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片不能超过 2MB")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    name = uuid.uuid4().hex + ext
    with open(os.path.join(UPLOAD_DIR, name), "wb") as f:
        f.write(data)
    return {"url": "/api/uploads/" + name}


@router.patch("/posts/{post_id}")
def update_post(
    post_id: int,
    body: PostUpdateIn,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    p = db.get(Post, post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if effective_status(p) != "open":
        raise HTTPException(status_code=400, detail="仅招募中的帖子可编辑")
    try:
        if body.contact is not None:
            ct = body.contact_type or p.contact_type
            p.contact = check_contact_format(ct, body.contact)
            p.contact_type = ct
        elif body.contact_type is not None:
            p.contact = check_contact_format(body.contact_type, p.contact)
            p.contact_type = body.contact_type
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if body.title is not None:
        p.title = body.title.strip()
    if body.description is not None:
        p.description = body.description.strip()
    if body.need_num is not None:
        p.need_num = body.need_num
    if body.deadline is not None:
        p.deadline = body.deadline
    if body.image is not None:
        p.image = body.image or None
    if body.competition is not None:
        p.competition = canonical_name(body.competition)
    if body.roles is not None:
        p.roles = _join(body.roles)
    if body.grade_req is not None:
        p.grade_req = _join(body.grade_req)
    if body.major_req is not None:
        p.major_req = body.major_req.strip()
    if body.stage is not None:
        p.stage = body.stage
    db.commit()
    return post_out(p, True)


@router.post("/posts/{post_id}/down")
def down_post(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    p = db.get(Post, post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if effective_status(p) != "open":
        raise HTTPException(status_code=400, detail="仅招募中的帖子可下架")
    p.status = "down"
    db.commit()
    return post_out(p, True)


@router.post("/posts/{post_id}/reopen")
def reopen_post(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    p = db.get(Post, post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if p.status != "down":
        raise HTTPException(status_code=400, detail="仅已下架的帖子可重新发布")
    if datetime.utcnow() - p.created_at > timedelta(days=EXPIRE_DAYS):
        raise HTTPException(status_code=400, detail="帖子已超过 30 天有效期，不可重新发布")
    p.status = "open"
    db.commit()
    return post_out(p, True)


@router.post("/posts/{post_id}/favorite")
def add_favorite(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    p = db.get(Post, post_id)
    if not p or p.status == "down" or effective_status(p) == "expired":
        raise HTTPException(status_code=404, detail="帖子不存在")
    exists = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.post_id == post_id)
        .first()
    )
    if not exists:
        db.add(Favorite(user_id=user.id, post_id=post_id))
        db.commit()
    return {"ok": True}


@router.delete("/posts/{post_id}/favorite")
def remove_favorite(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    row = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id, Favorite.post_id == post_id)
        .first()
    )
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True}


@router.post("/posts/{post_id}/close")
def close_post(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    p = db.get(Post, post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if effective_status(p) != "open":
        raise HTTPException(status_code=400, detail="当前状态不可关闭")
    p.status = "full"
    db.commit()
    return post_out(p, True)


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    p = db.get(Post, post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="帖子不存在")
    if effective_status(p) not in ("open", "full"):
        raise HTTPException(status_code=400, detail="当前状态不可删除")
    db.query(Favorite).filter(Favorite.post_id == p.id).delete()
    db.query(Application).filter(Application.post_id == p.id).delete()
    db.delete(p)
    db.commit()
    return {"ok": True}


# ------------------------------ 申请加入 ------------------------------


def _application_out(a: Application) -> dict:
    u = a.applicant
    return {
        "id": a.id,
        "post_id": a.post_id,
        "status": a.status,
        "message": a.message,
        "resume": a.resume,
        "match_score": a.match_score,
        "created_at": a.created_at.isoformat(),
        "applicant": {
            "id": u.id,
            "name": u.name,
            "grade": u.grade or "",
            "major": u.major or "",
            "skills": _split(u.skills),
            "bio": u.bio or "",
        },
    }


@router.post("/posts/{post_id}/apply")
def apply_post(
    post_id: int,
    body: ApplyIn,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    p = db.get(Post, post_id)
    if not p or p.status == "down" or effective_status(p) != "open":
        raise HTTPException(status_code=404, detail="该招募已结束")
    if p.user_id == user.id:
        raise HTTPException(status_code=400, detail="不能申请自己发布的招募")
    exists = (
        db.query(Application)
        .filter(Application.user_id == user.id, Application.post_id == post_id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="你已经申请过了")
    m = compute_match(p, user, None)
    a = Application(
        post_id=post_id,
        user_id=user.id,
        message=(body.message or "").strip(),
        resume=(body.resume if body.resume is not None else user.resume) or "",
        match_score=(m or {}).get("score"),
    )
    db.add(a)
    db.add(
        Message(
            from_id=user.id,
            to_id=p.user_id,
            post_id=p.id,
            body=f"我申请加入《{p.title}》" + (f"：{a.message}" if a.message else ""),
        )
    )
    db.commit()
    db.refresh(a)
    return _application_out(a)


@router.get("/posts/{post_id}/applications")
def list_applications(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    p = db.get(Post, post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="帖子不存在")
    rows = (
        db.query(Application)
        .filter(Application.post_id == post_id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return [_application_out(a) for a in rows]


@router.get("/my/applications")
def my_applications(user: User = Depends(require_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Application)
        .filter(Application.user_id == user.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    out = []
    for a in rows:
        p = a.post
        out.append(
            {
                "id": a.id,
                "status": a.status,
                "message": a.message,
                "match_score": a.match_score,
                "created_at": a.created_at.isoformat(),
                "post": {
                    "id": p.id,
                    "title": p.title,
                    "type": p.type,
                    "competition": p.competition or "",
                    "author_name": p.author.name,
                    "status": effective_status(p),
                },
            }
        )
    return out


@router.post("/applications/{app_id}/accept")
def accept_application(app_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    a = db.get(Application, app_id)
    if not a:
        raise HTTPException(status_code=404, detail="申请不存在")
    p = db.get(Post, a.post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="申请不存在")
    a.status = "accepted"
    a.updated_at = datetime.utcnow()
    db.add(
        Message(
            from_id=user.id,
            to_id=a.user_id,
            post_id=p.id,
            body=f"队长已通过你的申请：《{p.title}》，可以聊聊下一步安排了。",
        )
    )
    db.commit()
    return _application_out(a)


@router.post("/applications/{app_id}/reject")
def reject_application(app_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    a = db.get(Application, app_id)
    if not a:
        raise HTTPException(status_code=404, detail="申请不存在")
    p = db.get(Post, a.post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="申请不存在")
    a.status = "rejected"
    a.updated_at = datetime.utcnow()
    db.commit()
    return _application_out(a)


@router.delete("/applications/{app_id}")
def withdraw_application(app_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    a = db.get(Application, app_id)
    if not a or a.user_id != user.id:
        raise HTTPException(status_code=404, detail="申请不存在")
    db.delete(a)
    db.commit()
    return {"ok": True}


@router.get("/posts/{post_id}/candidates")
def candidate_posts(post_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    """队长视角：自动匹配「找队伍」帖，看看谁在找队、能补哪个位置。"""
    p = db.get(Post, post_id)
    if not p or p.user_id != user.id:
        raise HTTPException(status_code=404, detail="帖子不存在")
    posts = (
        db.query(Post)
        .filter(
            Post.type == "join",
            Post.status == "open",
            Post.user_id != user.id,
            Post.created_at > datetime.utcnow() - timedelta(days=EXPIRE_DAYS),
        )
        .order_by(Post.created_at.desc())
        .limit(120)
        .all()
    )
    out = []
    for q in posts:
        m = score_for_my_team(q, p)
        if not m:
            continue
        item = post_out(q, True, False, user)
        item["match"] = m
        out.append(item)
    out.sort(key=lambda x: -x["match"]["score"])
    return out[:20]
