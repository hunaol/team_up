from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

import os
import uuid

from auth import get_optional_user, require_user
from database import get_db
from models import EXPIRE_DAYS, Favorite, Post, User, effective_status
from schemas import PostIn, PostUpdateIn, check_contact_format, description_text

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def post_out(p: Post, include_contact: bool, favorited: bool = False) -> dict:
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
        "author_name": p.author.name,
        "status": effective_status(p),
        "views": p.views or 0,
        "is_favorite": favorited,
        "created_at": p.created_at.isoformat(),
    }


def _favorite_ids(db: Session, user: Optional[User]) -> set:
    if not user:
        return set()
    rows = db.query(Favorite.post_id).filter(Favorite.user_id == user.id).all()
    return {r[0] for r in rows}


@router.get("/posts")
def list_posts(
    type: Optional[str] = None,
    q: Optional[str] = None,
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
    posts = query.order_by(Post.created_at.desc()).all()
    favs = _favorite_ids(db, user)
    return [post_out(p, user is not None, p.id in favs) for p in posts]


@router.get("/my/posts")
def my_posts(user: User = Depends(require_user), db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .filter(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    favs = _favorite_ids(db, user)
    return [post_out(p, True, p.id in favs) for p in posts]


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
    return [post_out(p, True, True) for p in visible]


@router.get("/posts/{post_id}")
def get_post(
    post_id: int,
    user: Optional[User] = Depends(get_optional_user),
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
    return post_out(p, user is not None, favorited)


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
    db.delete(p)
    db.commit()
    return {"ok": True}
