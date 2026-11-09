from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import routes_admin
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


def migrate():
    """轻量迁移：为旧库补上 posts 的新字段。"""
    with engine.begin() as conn:
        cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(posts)")]
        if "contact_type" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE posts ADD COLUMN contact_type VARCHAR(10) NOT NULL DEFAULT 'wechat'"
            )
            conn.exec_driver_sql(
                "UPDATE posts SET contact_type='qq' WHERE contact LIKE '%QQ%' OR contact LIKE '%qq%'"
            )
            conn.exec_driver_sql(
                "UPDATE posts SET contact_type='phone' WHERE contact LIKE '%手机%' OR contact LIKE '%电话%'"
            )
        if "deadline" not in cols:
            conn.exec_driver_sql("ALTER TABLE posts ADD COLUMN deadline VARCHAR(10)")
        if "image" not in cols:
            conn.exec_driver_sql("ALTER TABLE posts ADD COLUMN image VARCHAR(200)")


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
app.include_router(routes_stats.router, prefix="/api", tags=["stats"])
app.include_router(routes_admin.router, prefix="/api/admin", tags=["admin"])

UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/api/health")
def health():
    return {"ok": True}
