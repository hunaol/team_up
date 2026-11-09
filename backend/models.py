from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base

EXPIRE_DAYS = 30


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(20), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(10), nullable=False)  # team=找队友, join=找队伍
    title = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    need_num = Column(Integer, nullable=True)
    contact_type = Column(String(10), nullable=False, default="wechat")  # wechat/qq/phone
    contact = Column(String(100), nullable=False)
    deadline = Column(String(10), nullable=True)  # YYYY-MM-DD 截止日期
    image = Column(String(200), nullable=True)  # 封面图 URL
    status = Column(String(10), nullable=False, default="open")  # open/full/down
    views = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    author = relationship("User")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True, nullable=False)
    salt = Column(String(32), nullable=False)
    password_hash = Column(String(128), nullable=False)


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_fav_user_post"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


def effective_status(post: Post, now: datetime | None = None) -> str:
    """计算帖子的有效状态：超过 30 天的 open 帖子视为已过期（读取时计算）。"""
    now = now or datetime.utcnow()
    if post.status == "open" and now - post.created_at > timedelta(days=EXPIRE_DAYS):
        return "expired"
    return post.status
