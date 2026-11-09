import json
import urllib.request
import urllib.error

BASE = "https://team.hunao.xin"

def req(path, data=None, token=None, method=None):
    url = BASE + path
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method=method or ("POST" if body else "GET"))
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw[:200])
    except urllib.error.HTTPError as ex:
        return ex.code, ex.read().decode()[:300]

print("student login:", req("/api/auth/login", {"student_id": "2024413435", "name": "韩涛"}))
st = req("/api/auth/login", {"student_id": "2024413435", "name": "韩涛"})
tok = st[1].get("token") if isinstance(st[1], dict) else None
print("token ok:", bool(tok))
print("me:", req("/api/auth/me", token=tok))
code, posts = req("/api/posts?page=1&page_size=3", token=tok)
print("posts:", code, (len(posts.get("items", [])) if isinstance(posts, dict) else posts))
print("admin login:", req("/api/admin/login", {"username": "admin", "password": "admin123"}))
ac = req("/api/admin/login", {"username": "admin", "password": "admin123"})
atok = ac[1].get("token") if isinstance(ac[1], dict) else None
code, stats = req("/api/admin/stats?range=7", token=atok)
print("admin stats:", code, str(stats)[:200])

# 静态资源
for p in ["/assets/index-DTzQ8XV7.css", "/hero-campus.svg", "/admin/login"]:
    try:
        with urllib.request.urlopen(BASE + p, timeout=20) as resp:
            print(p, resp.status, resp.headers.get("content-type"), resp.headers.get("cache-control"))
    except urllib.error.HTTPError as ex:
        print(p, "ERR", ex.code)
