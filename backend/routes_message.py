from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from auth import require_user
from database import get_db
from models import Message, Post, User
from schemas import MessageIn

router = APIRouter()


def _msg_out(m: Message) -> dict:
    return {
        "id": m.id,
        "from_id": m.from_id,
        "to_id": m.to_id,
        "post_id": m.post_id,
        "body": m.body,
        "is_read": bool(m.is_read),
        "created_at": m.created_at.isoformat(),
    }


@router.get("/messages/threads")
def threads(user: User = Depends(require_user), db: Session = Depends(get_db)):
    """会话列表：按对方聚合，带最后一条消息与未读数。"""
    rows = (
        db.query(Message)
        .filter(or_(Message.from_id == user.id, Message.to_id == user.id))
        .order_by(Message.created_at.desc())
        .limit(600)
        .all()
    )
    seen = {}
    order = []
    for m in rows:
        peer_id = m.to_id if m.from_id == user.id else m.from_id
        if peer_id not in seen:
            peer = db.get(User, peer_id)
            seen[peer_id] = {
                "peer": {
                    "id": peer_id,
                    "name": peer.name if peer else "已注销用户",
                },
                "last": _msg_out(m),
                "unread": 0,
                "post_title": "",
            }
            order.append(peer_id)
        if m.to_id == user.id and not m.is_read:
            seen[peer_id]["unread"] += 1
    # 补上帖子标题，让会话有上下文
    for peer_id in order:
        pid = seen[peer_id]["last"].get("post_id")
        if pid:
            p = db.get(Post, pid)
            if p:
                seen[peer_id]["post_title"] = p.title
    return [seen[pid] for pid in order]


@router.get("/messages/with/{peer_id}")
def conversation(peer_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    peer = db.get(User, peer_id)
    if not peer:
        raise HTTPException(status_code=404, detail="用户不存在")
    rows = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.from_id == user.id, Message.to_id == peer_id),
                and_(Message.from_id == peer_id, Message.to_id == user.id),
            )
        )
        .order_by(Message.created_at.asc())
        .limit(500)
        .all()
    )
    # 打开会话即标记已读
    changed = False
    for m in rows:
        if m.to_id == user.id and not m.is_read:
            m.is_read = True
            changed = True
    if changed:
        db.commit()
    return {
        "peer": {"id": peer.id, "name": peer.name},
        "messages": [_msg_out(m) for m in rows],
    }


@router.post("/messages")
def send_message(body: MessageIn, user: User = Depends(require_user), db: Session = Depends(get_db)):
    if body.to_id == user.id:
        raise HTTPException(status_code=400, detail="不能给自己发私信")
    peer = db.get(User, body.to_id)
    if not peer or not peer.active:
        raise HTTPException(status_code=404, detail="用户不存在")
    m = Message(
        from_id=user.id,
        to_id=body.to_id,
        post_id=body.post_id,
        body=body.body.strip(),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return _msg_out(m)


@router.get("/messages/unread")
def unread(user: User = Depends(require_user), db: Session = Depends(get_db)):
    count = (
        db.query(Message)
        .filter(Message.to_id == user.id, Message.is_read == False)  # noqa: E712
        .count()
    )
    return {"count": count}
