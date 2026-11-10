"""服务器端端到端自检：注册 → 登录 → 资料 → 发帖 → 报名 → 私信 → 管理后台，随后清理测试数据。

在本机用 _run_e2e.py 上传并执行。
"""

import json
import sqlite3
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8020"
DB = "/www/wwwroot/team.hunao.xin/server/app.db"
SID = "900000001"
NAME = "自检账号"
RESULTS = []


def req(path, data=None, token=None, method=None):
    url = BASE + path
    body = None
    headers = {}
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = "Bearer " + token
    r = urllib.request.Request(url, data=body, headers=headers, method=method or ("POST" if data else "GET"))
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def check(label, cond, detail=""):
    RESULTS.append((label, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + label + ("  " + str(detail) if detail and not cond else ""))


# 1) 注册 / 登录
s, d = req("/api/auth/register", {"student_id": SID, "name": NAME})
check("注册", s in (200, 400), (s, d))
s, d = req("/api/auth/login", {"student_id": SID, "name": NAME})
token = (d or {}).get("token") if isinstance(d, dict) else None
check("登录拿 token", s == 200 and token, (s, d))

# 2) 个人资料
s, d = req("/api/auth/me", token=token)
check("/auth/me", s == 200 and isinstance(d, dict), (s, d))
s, d = req(
    "/api/auth/profile",
    {
        "grade": "sophomore",
        "major": "计算机科学与技术",
        "skills": ["frontend", "backend"],
        "interests": ["中国国际大学生创新大赛"],
        "bio": "部署自检",
        "contact_type": "wechat",
        "contact": "selfcheck_wx",
        "open_to_match": True,
    },
    token=token,
    method="PUT",
)
check("PUT /auth/profile", s == 200, (s, d))
s, d = req("/api/auth/profile", token=token)
check("GET /auth/profile", s == 200 and isinstance(d, dict) and d.get("major"), (s, d.get("major") if isinstance(d, dict) else d))

# 3) 元数据（比赛库）
s, d = req("/api/meta/competitions")
check("/meta/competitions", s == 200 and isinstance(d, list) and len(d) > 0, (s, len(d) if isinstance(d, list) else d))
s, d = req("/api/meta/competition-counts")
check("/meta/competition-counts", s == 200, (s, d))

# 4) 发帖（带结构化字段）
s, d = req(
    "/api/posts",
    {
        "type": "team",
        "title": "部署自检招募",
        "description": "这是部署自检生成的临时帖子，用于验证发帖链路是否正常。",
        "need_num": 2,
        "contact_type": "wechat",
        "contact": "selfcheck_wx",
        "deadline": "2026-12-31",
        "competition": "互联网+",
        "roles": ["frontend"],
        "grade_req": ["sophomore"],
        "major_req": "计算机",
        "stage": "school",
    },
    token=token,
)
post_id = (d or {}).get("id") if isinstance(d, dict) else None
check("POST /posts", s == 200 and post_id, (s, d))

# 5) 列表 / 详情 / 推荐
s, d = req("/api/posts")
check("/posts 列表", s == 200 and isinstance(d, list), (s, type(d)))
s, d = req("/api/posts/%s" % post_id)
detail_ok = s == 200 and isinstance(d, dict) and d.get("competition")
check("帖子详情含结构化字段", detail_ok, (s, d.get("competition") if isinstance(d, dict) else d))
s, d = req("/api/recommended", token=token)
check("/recommended 智能推荐", s == 200 and "items" in (d or {}), (s, list(d)[:5] if isinstance(d, dict) else d))

# 6) 私信
s, d = req("/api/messages/threads", token=token)
check("/messages/threads", s == 200, (s, d))
s, d = req("/api/messages/unread", token=token)
check("/messages/unread", s == 200, (s, d))

# 7) 管理后台
s, d = req("/api/admin/login", {"username": "admin", "password": "admin123"})
atoken = (d or {}).get("token") if isinstance(d, dict) else None
check("管理员登录", s == 200 and atoken, (s, d))
for path in ("/api/admin/stats", "/api/admin/users", "/api/admin/posts"):
    s, d = req(path, token=atoken)
    check("admin " + path, s == 200, (s, d))

# 8) 清理：删掉自检账号产生的全部数据
con = sqlite3.connect(DB)
cur = con.cursor()
uid = cur.execute("select id from users where student_id=?", (SID,)).fetchone()
if uid:
    uid = uid[0]
    for sql in (
        "delete from applications where user_id=? or post_id in (select id from posts where user_id=?)",
        "delete from favorites where user_id=? or post_id in (select id from posts where user_id=?)",
        "delete from messages where from_id=? or to_id=?",
        "delete from tokens where user_id=?",
        "delete from posts where user_id=?",
        "delete from users where id=?",
    ):
        cur.execute(sql, (uid, uid) if sql.count("?") == 2 else (uid,))
    con.commit()
left = cur.execute("select count(*) from users where student_id=?", (SID,)).fetchone()[0]
posts_left = cur.execute("select count(*) from posts where title='部署自检招募'").fetchone()[0]
con.close()
check("清理测试数据", left == 0 and posts_left == 0, (left, posts_left))

bad = [r for r in RESULTS if not r[1]]
print("\n总计 %d 项，失败 %d 项" % (len(RESULTS), len(bad)))
