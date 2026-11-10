import hashlib
import os
import uuid
from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Token, User


def make_salt() -> str:
    return os.urandom(16).hex()


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def issue_token(db: Session, user_id: Optional[int] = None, is_admin: bool = False) -> str:
    t = Token(token=uuid.uuid4().hex, user_id=user_id, is_admin=is_admin)
    db.add(t)
    db.commit()
    return t.token


def _parse_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:].strip() or None


def get_optional_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """解析登录态；未登录或账号被停用时返回 None（按游客处理）。"""
    raw = _parse_bearer(authorization)
    if not raw:
        return None
    row = db.query(Token).filter(Token.token == raw, Token.is_admin == False).first()  # noqa: E712
    if not row or not row.user_id:
        return None
    user = db.get(User, row.user_id)
    if not user or not user.active:
        return None
    return user


def require_user(user: Optional[User] = Depends(get_optional_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return user


def require_admin(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    raw = _parse_bearer(authorization)
    if not raw:
        raise HTTPException(status_code=401, detail="请先登录管理平台")
    row = db.query(Token).filter(Token.token == raw, Token.is_admin == True).first()  # noqa: E712
    if not row:
        raise HTTPException(status_code=401, detail="请先登录管理平台")
    return row


def is_admin_viewer(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> bool:
    """管理员以只读身份浏览前台时返回 True。

    管理员审核内容时需要看到联系方式等信息，不该被「请先登录学生账号」挡住；
    但管理员没有学生身份，不能发帖、申请、收藏、私信，所以这里只用于放宽读权限。
    """
    raw = _parse_bearer(authorization)
    if not raw:
        return False
    row = db.query(Token).filter(Token.token == raw, Token.is_admin == True).first()  # noqa: E712
    return row is not None
