from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import routes_admin
import routes_message
import routes_meta
import routes_post
import routes_stats
import routes_user
from auth import hash_password, make_salt
from database import Base, SessionLocal, engine
from models import Admin

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"


def seed_admin():
    db = SessionLocal()
    try:
        if not db.query(Admin).first():
            salt = make_salt()
            db.add(
                Admin(
                    username="admin",
                    salt=salt,
                    password_hash=hash_password("admin123", salt),
                )
            )
            db.commit()
    finally:
        db.close()


def _columns(conn, table: str) -> list:
    return [row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")]


def _add_columns(conn, table: str, specs: list) -> None:
    cols = _columns(conn, table)
    for name, ddl in specs:
        if name not in cols:
            conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def migrate():
    """轻量迁移：为旧库补上新增字段（SQLite 不支持一次加多列）。"""
    with engine.begin() as conn:
        _add_columns(
            conn,
            "posts",
            [
                ("contact_type", "contact_type VARCHAR(10) NOT NULL DEFAULT 'wechat'"),
                ("deadline", "deadline VARCHAR(10)"),
                ("image", "image VARCHAR(200)"),
                ("competition", "competition VARCHAR(80) NOT NULL DEFAULT ''"),
                ("roles", "roles VARCHAR(240) NOT NULL DEFAULT ''"),
                ("grade_req", "grade_req VARCHAR(60) NOT NULL DEFAULT ''"),
                ("major_req", "major_req VARCHAR(80) NOT NULL DEFAULT ''"),
                ("stage", "stage VARCHAR(20) NOT NULL DEFAULT ''"),
            ],
        )
        # 旧数据回填联系方式类型
        conn.exec_driver_sql(
            "UPDATE posts SET contact_type='qq' WHERE contact_type='wechat' AND (contact LIKE '%QQ%' OR contact LIKE '%qq%')"
        )
        conn.exec_driver_sql(
            "UPDATE posts SET contact_type='phone' WHERE contact_type='wechat' AND (contact LIKE '%手机%' OR contact LIKE '%电话%')"
        )
        _add_columns(
            conn,
            "users",
            [
                ("grade", "grade VARCHAR(10) NOT NULL DEFAULT ''"),
                ("major", "major VARCHAR(40) NOT NULL DEFAULT ''"),
                ("skills", "skills VARCHAR(240) NOT NULL DEFAULT ''"),
                ("interests", "interests VARCHAR(300) NOT NULL DEFAULT ''"),
                ("bio", "bio VARCHAR(300) NOT NULL DEFAULT ''"),
                ("resume", "resume VARCHAR(2000) NOT NULL DEFAULT ''"),
                ("contact_type", "contact_type VARCHAR(10) NOT NULL DEFAULT 'wechat'"),
                ("contact", "contact VARCHAR(100) NOT NULL DEFAULT ''"),
                ("open_to_match", "open_to_match BOOLEAN NOT NULL DEFAULT 1"),
            ],
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate()
    seed_admin()
    yield


app = FastAPI(title="比赛队友招募平台 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_user.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes_post.router, prefix="/api", tags=["posts"])
app.include_router(routes_message.router, prefix="/api", tags=["messages"])
app.include_router(routes_meta.router, prefix="/api", tags=["meta"])
app.include_router(routes_stats.router, prefix="/api", tags=["stats"])
app.include_router(routes_admin.router, prefix="/api/admin", tags=["admin"])

UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/api/health")
def health():
    return {"ok": True}
