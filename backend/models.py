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

    # 个人资料（用于匹配与推送）
    grade = Column(String(10), nullable=False, default="")  # freshman / sophomore / ...
    major = Column(String(40), nullable=False, default="")
    skills = Column(String(240), nullable=False, default="")  # 逗号分隔的角色 code
    interests = Column(String(300), nullable=False, default="")  # 意向比赛（标准名，逗号分隔）
    bio = Column(String(300), nullable=False, default="")
    resume = Column(String(2000), nullable=False, default="")  # 简历正文
    contact_type = Column(String(10), nullable=False, default="wechat")
    contact = Column(String(100), nullable=False, default="")
    open_to_match = Column(Boolean, nullable=False, default=True)


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

    # 结构化字段：让帖子可被精确检索与匹配
    competition = Column(String(80), nullable=False, default="", index=True)  # 比赛标准名
    roles = Column(String(240), nullable=False, default="")  # team=缺什么位置 / join=我会什么
    grade_req = Column(String(60), nullable=False, default="")  # 逗号分隔年级 code
    major_req = Column(String(80), nullable=False, default="")
    stage = Column(String(20), nullable=False, default="")  # forming/school/province/national

    author = relationship("User")


class Application(Base):
    """申请加入队伍：附带一句自荐 + 简历快照，队长可从中筛选。"""

    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("post_id", "user_id", name="uq_apply_post_user"),)

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(String(500), nullable=False, default="")
    resume = Column(String(2000), nullable=False, default="")
    match_score = Column(Integer, nullable=True)
    status = Column(String(12), nullable=False, default="pending")  # pending/accepted/rejected
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    applicant = relationship("User")
    post = relationship("Post")


class Message(Base):
    """站内私信。thread = (user_lo, user_hi)。"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    from_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    to_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(Integer, nullable=True)
    body = Column(String(1000), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


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
