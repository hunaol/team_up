from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from auth import get_optional_user, issue_token, require_user
from competitions import canonical_name, resolve_list
from database import get_db
from models import Token, User
from schemas import LoginIn, ProfileIn, RegisterIn

router = APIRouter()


def _split(value: Optional[str]) -> list:
    if not value:
        return []
    return [x.strip() for x in str(value).split(",") if x.strip()]


def _join(values) -> str:
    out = []
    for v in values or []:
        v = (v or "").strip()
        if v and v not in out:
            out.append(v)
    return ",".join(out)


def _profile_out(user: User, include_contact: bool = True) -> dict:
    return {
        "id": user.id,
        "student_id": user.student_id,
        "name": user.name,
        "grade": user.grade or "",
        "major": user.major or "",
        "skills": _split(user.skills),
        "interests": _split(user.interests),
        "bio": user.bio or "",
        "resume": user.resume or "",
        "contact_type": user.contact_type or "wechat",
        "contact": (user.contact or "") if include_contact else "",
        "open_to_match": bool(user.open_to_match),
        "active": bool(user.active),
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def _user_out(user: User) -> dict:
    return {"student_id": user.student_id, "name": user.name, "id": user.id}


@router.post("/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.student_id == body.student_id).first()
    if exists:
        raise HTTPException(status_code=400, detail="该学号已注册")
    user = User(student_id=body.student_id, name=body.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = issue_token(db, user_id=user.id)
    return {"token": token, "user": _user_out(user)}


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == body.student_id).first()
    if not user or user.name != body.name:
        raise HTTPException(status_code=401, detail="学号或姓名不正确")
    if not user.active:
        raise HTTPException(status_code=403, detail="账号已被停用，请联系管理员")
    token = issue_token(db, user_id=user.id)
    return {"token": token, "user": _user_out(user)}


@router.get("/me")
def me(user: User = Depends(require_user)):
    return _user_out(user)


@router.get("/profile")
def get_profile(
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if not user:
        raise HTTPException(status_code=401, detail="请先登录")
    return _profile_out(user)


@router.put("/profile")
def update_profile(body: ProfileIn, user: User = Depends(require_user), db: Session = Depends(get_db)):
    if body.grade is not None:
        user.grade = body.grade
    if body.major is not None:
        user.major = body.major.strip()
    if body.skills is not None:
        user.skills = _join(body.skills)
    if body.interests is not None:
        # 意向比赛统一成名录标准名，避免「正大杯」「市调」各写各的
        names = []
        for item in body.interests:
            name = canonical_name(item)
            if name and name not in names:
                names.append(name)
        user.interests = ",".join(names)
    if body.bio is not None:
        user.bio = body.bio.strip()
    if body.resume is not None:
        user.resume = body.resume.strip()
    if body.contact_type is not None:
        user.contact_type = body.contact_type
    if body.contact is not None:
        user.contact = body.contact.strip()
    if body.open_to_match is not None:
        user.open_to_match = bool(body.open_to_match)
    db.commit()
    return _profile_out(user)


@router.get("/users/{user_id}/profile")
def public_profile(user_id: int, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u or not u.active:
        raise HTTPException(status_code=404, detail="用户不存在")
    return _profile_out(u, include_contact=False)


@router.post("/logout")
def logout(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    if authorization and authorization.startswith("Bearer "):
        raw = authorization[7:].strip()
        row = db.query(Token).filter(Token.token == raw).first()
        if row:
            db.delete(row)
            db.commit()
    return {"ok": True}
