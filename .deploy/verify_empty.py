import json
import urllib.request
import urllib.error

BASE = "https://team.hunao.xin"

def req(path, data=None, token=None):
    url = BASE + path
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, method="POST" if body else "GET")
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw[:200])
    except urllib.error.HTTPError as ex:
        return ex.code, ex.read().decode()[:200]

print("stats:", req("/api/stats/overview"))
print("posts:", req("/api/posts?page=1&page_size=5"))
code, login = req("/api/admin/login", {"username": "admin", "password": "admin123"})
print("admin login:", code)
tok = login.get("token") if isinstance(login, dict) else None
print("admin users:", req("/api/admin/users?page=1&page_size=5", token=tok))
print("admin posts:", req("/api/admin/posts?page=1&page_size=5", token=tok))
print("admin stats:", req("/api/admin/stats?range=7", token=tok))
print("wrong pwd:", req("/api/admin/login", {"username": "admin", "password": "bad"}))
