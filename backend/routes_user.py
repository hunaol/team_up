from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from auth import get_optional_user, issue_token, require_user
from database import get_db
from models import Token, User
from schemas import LoginIn, RegisterIn

router = APIRouter()


def _user_out(user: User) -> dict:
    return {"student_id": user.student_id, "name": user.name}


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
