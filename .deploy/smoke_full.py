"""部署后冒烟：逐个接口打状态码，并检查数据库迁移结果。"""
from srun import connect

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REMOTE = r"""
B=http://127.0.0.1:8020
for p in /api/health /api/meta /api/competitions /api/posts /api/stats/overview; do
  code=$(curl -s -o /tmp/body -w '%{http_code}' "$B$p")
  echo "$p -> $code  $(head -c 160 /tmp/body)"
done
echo '--- admin login ---'
curl -s -o /tmp/body -w '%{http_code}\n' -X POST "$B/api/admin/login" -H 'Content-Type: application/json' -d '{"username":"admin","password":"admin123"}'
head -c 120 /tmp/body
echo
echo '--- db columns ---'
cd /www/wwwroot/team.hunao.xin/server
./venv/bin/python - <<'PY'
import sqlite3
c = sqlite3.connect('/www/wwwroot/team.hunao.xin/server/app.db')
for t in ('posts', 'users'):
    print(t, [r[1] for r in c.execute('PRAGMA table_info(%s)' % t)])
print('counts', {t: c.execute('select count(*) from %s' % t).fetchone()[0]
                 for t in ('users', 'posts', 'admins')})
PY
"""

cli = connect()
_, out, err = cli.exec_command(REMOTE, timeout=180)
print(out.read().decode("utf-8", "replace"))
e = err.read().decode("utf-8", "replace")
if e.strip():
    print("--- stderr ---")
    print(e)
cli.close()
