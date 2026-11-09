"""完整接口测试（仅标准库）。运行前提：后端已在 127.0.0.1:8000 启动。
在 backend 目录下执行：python run_tests.py
"""
import json
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

BASE = "http://127.0.0.1:8000/api"
passed = 0
failed = 0


def call(method, path, body=None, token=None):
    req = urllib.request.Request(BASE + urllib.parse.quote(path, safe="/?=&%"), method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            detail = json.loads(raw)
        except Exception:
            detail = None
        return e.code, detail


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


print("== 健康检查 ==")
s, d = call("GET", "/health")
check("GET /health", s == 200 and d["ok"] is True)

print("== 注册 / 登录 ==")
s, a = call("POST", "/auth/register", {"student_id": "20990001", "name": "测试甲"})
check("注册用户甲", s == 200 and a["token"])
s, d = call("POST", "/auth/register", {"student_id": "20990001", "name": "测试甲"})
check("重复学号注册被拒绝(400)", s == 400)
s, d = call("POST", "/auth/register", {"student_id": "123", "name": "测试"})
check("非法学号被拒绝(422)", s == 422)
s, d = call("POST", "/auth/login", {"student_id": "20990001", "name": "错误姓名"})
check("登录姓名不匹配(401)", s == 401)
s, d = call("POST", "/auth/login", {"student_id": "20990001", "name": "测试甲"})
check("正确登录", s == 200 and d["token"])
ta = a["token"]
s, b = call("POST", "/auth/register", {"student_id": "20990002", "name": "测试乙"})
tb = b["token"]
check("注册用户乙", s == 200)
s, d = call("GET", "/auth/me", token=ta)
check("GET /me 返回当前用户", s == 200 and d["student_id"] == "20990001")

print("== 发布帖子 ==")
post1 = {"type": "team", "title": "数学建模竞赛", "description": "找一名会 Python 的同学负责数据处理工作。", "need_num": 2, "contact_type": "wechat", "contact": "abc12345", "deadline": "2026-12-31"}
s, p1 = call("POST", "/posts", post1, ta)
check("用户甲发布帖子", s == 200 and p1["status"] == "open" and p1["deadline"] == "2026-12-31")
s, d = call("POST", "/posts", {**post1, "deadline": "2026/12/31"}, ta)
check("截止日期格式错误被拒绝(422)", s == 422)
s, d = call("POST", "/posts", {**post1, "contact": "abc"}, ta)
check("联系方式过短被拒绝(422)", s == 422)
s, d = call("POST", "/posts", {**post1, "contact_type": "phone", "contact": "12345"}, ta)
check("手机号格式错误被拒绝(422)", s == 422)
s, d = call("POST", "/posts", {**post1, "contact_type": "qq", "contact": "abcde"}, ta)
check("QQ 号格式错误被拒绝(422)", s == 422)
s, d = call("POST", "/posts", {**post1, "contact_type": "email", "contact": "abc@x.com"}, ta)
check("非法联系方式类型被拒绝(422)", s == 422)
s, d = call("POST", "/posts", post1)
check("未登录发布被拒绝(401)", s == 401)
s, p2 = call("POST", "/posts", {"type": "join", "title": "互联网加大赛", "description": "本人擅长前端，想加入一支做校园项目的队伍。", "contact_type": "qq", "contact": "88991234"}, tb)
check("用户乙发布找队伍帖子", s == 200)

print("== 列表 / 联系方式门槛 ==")
s, lst = call("GET", "/posts")
check("游客列表不含联系方式", s == 200 and all(x["contact"] is None for x in lst))
s, lst = call("GET", "/posts", token=ta)
check("登录用户列表含联系方式", s == 200 and all(x["contact"] for x in lst))
s, lst = call("GET", "/posts?type=join")
check(
    "类型筛选(找队伍)",
    s == 200
    and any(x["id"] == p2["id"] for x in lst)
    and all(x["type"] == "join" for x in lst)
    and all(x["id"] != p1["id"] for x in lst),
)
s, lst = call("GET", "/posts?q=Python")
check(
    "关键词搜索(描述命中)",
    s == 200
    and any(x["id"] == p1["id"] for x in lst)
    and all("Python".lower() in (x["description_text"] or "").lower() for x in lst),
)
s, lst = call("GET", "/posts?q=互联网")
check(
    "关键词搜索(标题命中)",
    s == 200
    and any(x["id"] == p2["id"] for x in lst)
    and all("互联网" in x["title"] for x in lst),
)
s, d = call("GET", f"/posts/{p1['id']}")
check("游客详情不含联系方式", s == 200 and d["contact"] is None)
s, d = call("GET", f"/posts/{p1['id']}", token=ta)
check("登录详情含联系方式", s == 200 and d["contact"] == "abc12345" and d["contact_type"] == "wechat")

print("== 关闭 / 删除 ==")
s, d = call("POST", f"/posts/{p1['id']}/close", token=tb)
check("非本人关闭被拒绝(404)", s == 404)
s, d = call("POST", f"/posts/{p1['id']}/close", token=ta)
check("本人关闭招募 -> 已招满", s == 200 and d["status"] == "full")
s, d = call("POST", f"/posts/{p1['id']}/close", token=ta)
check("已招满不可再关闭(400)", s == 400)
s, d = call("DELETE", f"/posts/{p1['id']}", token=ta)
check("本人删除已招满帖子", s == 200)
s, lst = call("GET", "/posts")
check("删除后列表不再包含该帖", all(x["id"] != p1["id"] for x in lst))

print("== 编辑 / 下架 / 重新发布 ==")
s, pe = call("POST", "/posts", {**post1, "title": "化学实验竞赛", "image": "/api/uploads/demo.png"}, ta)
check("发布带封面图帖子", s == 200 and pe["image"] == "/api/uploads/demo.png")
s, d = call("PATCH", f"/posts/{pe['id']}", {"title": "化学实验竞赛（修订）"}, ta)
check("本人编辑标题", s == 200 and d["title"] == "化学实验竞赛（修订）")
s, d = call("PATCH", f"/posts/{pe['id']}", {"title": "他人修改"}, tb)
check("非本人编辑被拒绝(404)", s == 404)
s, d = call("PATCH", f"/posts/{pe['id']}", {"contact_type": "phone", "contact": "12345"}, ta)
check("编辑时非法联系方式被拒绝(422)", s == 422)
s, d = call("POST", f"/posts/{pe['id']}/down", token=tb)
check("非本人下架被拒绝(404)", s == 404)
s, d = call("POST", f"/posts/{pe['id']}/down", token=ta)
check("本人下架帖子", s == 200 and d["status"] == "down")
s, lst = call("GET", "/posts")
check("下架后前台列表不可见", all(x["id"] != pe["id"] for x in lst))
s, d = call("POST", f"/posts/{pe['id']}/reopen", token=ta)
check("重新发布恢复招募中", s == 200 and d["status"] == "open")
s, d = call("POST", f"/posts/{pe['id']}/reopen", token=ta)
check("非下架帖重新发布被拒绝(400)", s == 400)
s, d = call("POST", f"/posts/{pe['id']}/close", token=ta)
s, d = call("PATCH", f"/posts/{pe['id']}", {"title": "招满后编辑"}, ta)
check("已招满帖子编辑被拒绝(400)", s == 400)
s, d = call("DELETE", f"/posts/{pe['id']}", token=ta)
check("删除测试帖子", s == 200)

print("== 管理员 ==")
s, d = call("POST", "/admin/login", {"username": "admin", "password": "wrong"})
check("管理员密码错误(401)", s == 401)
s, adm = call("POST", "/admin/login", {"username": "admin", "password": "admin123"})
check("管理员登录", s == 200 and adm["token"])
tadm = adm["token"]
s, d = call("GET", "/admin/stats", token=tadm)
check("数据概览", s == 200 and d["user_count"] >= 2 and d["post_total"] >= 1)
check("概览含趋势与状态分布", len(d["trend"]) == 30 and "open" in d["status_distribution"] and "success_rate" in d and "participants_total" in d)
s, d = call("GET", "/admin/stats?range=7", token=tadm)
check("概览按 7 天筛选", s == 200 and len(d["trend"]) == 7)
s, d = call("GET", "/admin/users?q=20990001", token=tadm)
check("用户搜索", s == 200 and len(d["items"]) == 1 and d["items"][0]["student_id"] == "20990001")
s, d = call("GET", "/admin/users?page=1&page_size=1", token=tadm)
check("用户分页", s == 200 and len(d["items"]) == 1 and d["total"] >= 2)
s, d = call("GET", "/admin/stats")
check("未登录访问后台被拒绝(401)", s == 401)

print("== 停用 / 启用 ==")
uid_b = None
s, users = call("GET", "/admin/users", token=tadm)
uid_b = [u for u in users["items"] if u["student_id"] == "20990002"][0]["id"]
s, d = call("POST", f"/admin/users/{uid_b}/deactivate", token=tadm)
check("停用用户乙", s == 200)
s, d = call("POST", "/auth/login", {"student_id": "20990002", "name": "测试乙"})
check("被停用用户登录被拒绝(403)", s == 403)
s, lst = call("GET", "/posts")
check("停用用户的历史帖子仍展示", any(x["id"] == p2["id"] for x in lst))
s, d = call("POST", f"/admin/users/{uid_b}/activate", token=tadm)
check("启用用户乙", s == 200)
s, d = call("POST", "/auth/login", {"student_id": "20990002", "name": "测试乙"})
check("启用后可重新登录", s == 200)
tb = d["token"]
s, d = call("PATCH", f"/admin/users/{uid_b}", {"name": "测试丙"}, token=tadm)
check("管理员修改用户姓名", s == 200)
s, d = call("POST", "/auth/login", {"student_id": "20990002", "name": "测试丙"})
check("新姓名可登录", s == 200)
s, d = call("PATCH", f"/admin/users/{uid_b}", {"name": "测试乙"}, token=tadm)
check("恢复用户姓名", s == 200)

print("== 下架 ==")
s, d = call("POST", f"/admin/posts/{p2['id']}/takedown", token=tadm)
check("管理员下架帖子", s == 200 and d["status"] == "down")
s, lst = call("GET", "/posts")
check("下架后前台列表不可见", all(x["id"] != p2["id"] for x in lst))
s, d = call("GET", f"/posts/{p2['id']}")
check("下架后详情不可访问(404)", s == 404)
s, mine = call("GET", "/my/posts", token=tb)
check("发布者在我的发布可见已下架", any(x["id"] == p2["id"] and x["status"] == "down" for x in mine))
s, d = call("POST", f"/admin/posts/{p2['id']}/takedown", token=tadm)
check("已下架不可重复下架(400)", s == 400)

print("== 30 天过期 ==")
s, p3 = call("POST", "/posts", {"type": "team", "title": "电子设计竞赛", "description": "找一名嵌入式方向同学，要求会 STM32 开发。", "contact_type": "phone", "contact": "13800001111"}, ta)
old = (datetime.utcnow() - timedelta(days=31)).isoformat()
conn = sqlite3.connect("app.db")
conn.execute("UPDATE posts SET created_at=? WHERE id=?", (old, p3["id"]))
conn.commit()
conn.close()
s, lst = call("GET", "/posts")
check("过期帖子不出现在前台列表", all(x["id"] != p3["id"] for x in lst))
s, mine = call("GET", "/my/posts", token=ta)
check("我的发布显示已过期", any(x["id"] == p3["id"] and x["status"] == "expired" for x in mine))
s, d = call("POST", f"/posts/{p3['id']}/close", token=ta)
check("过期帖子不可关闭(400)", s == 400)
s, admin_posts = call("GET", "/admin/posts?status=expired", token=tadm)
check("后台可按已过期筛选", any(x["id"] == p3["id"] for x in admin_posts))

print("== 浏览量 / 收藏 ==")
s, p4 = call("POST", "/posts", {"type": "team", "title": "软件测试大赛", "description": "找两名同学组队参加软件测试大赛，方向不限。", "contact_type": "qq", "contact": "12345678"}, ta)
check("发布测试用帖子", s == 200)
call("GET", f"/posts/{p4['id']}")
s, d = call("GET", f"/posts/{p4['id']}")
check("浏览量累计", s == 200 and d["views"] >= 2)
s, d = call("POST", f"/posts/{p4['id']}/favorite")
check("未登录收藏被拒绝(401)", s == 401)
s, d = call("POST", f"/posts/{p4['id']}/favorite", token=tb)
check("用户乙收藏帖子", s == 200)
s, d = call("POST", f"/posts/{p4['id']}/favorite", token=tb)
check("重复收藏幂等", s == 200)
s, lst = call("GET", "/posts", token=tb)
check("列表中 is_favorite=true", any(x["id"] == p4["id"] and x["is_favorite"] for x in lst))
s, favs = call("GET", "/my/favorites", token=tb)
check("我的收藏包含该帖", s == 200 and any(x["id"] == p4["id"] for x in favs))
s, d = call("DELETE", f"/posts/{p4['id']}/favorite", token=tb)
check("取消收藏", s == 200)
s, favs = call("GET", "/my/favorites", token=tb)
check("取消后我的收藏不再包含", all(x["id"] != p4["id"] for x in favs))

print("== 图片上传 ==")


def upload(token, ctype="image/png", content=None):
    content = content if content is not None else b"\x89PNG\r\n\x1a\n" + b"0" * 64
    boundary = "----traetestboundary"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.png\"\r\n"
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/uploads", data=body, method="POST")
    req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None


s, up = upload(ta)
check("上传图片返回 URL", s == 200 and up["url"].startswith("/api/uploads/"))
req = urllib.request.Request("http://127.0.0.1:8000" + up["url"])
with urllib.request.urlopen(req) as r:
    check("上传的图片可访问", r.status == 200)
s, up = upload(ta, ctype="text/plain", content=b"hello")
check("非图片上传被拒绝(400)", s == 400)
s, up = upload(None)
check("未登录上传被拒绝(401)", s == 401)

print("== 退出登录 ==")
s, d = call("POST", "/auth/logout", token=ta)
check("退出登录", s == 200)
s, d = call("GET", "/auth/me", token=ta)
check("退出后令牌失效(401)", s == 401)

print()
print(f"结果：{passed} 通过 / {failed} 失败（共 {passed + failed} 项）")
exit(1 if failed else 0)
