import os
from ssh import connect, run

cli = connect()

# 1) 测试 acme challenge 目录是否可访问
run(cli, "mkdir -p /www/wwwroot/team.hunao.xin/acme/.well-known/acme-challenge && echo acme-test > /www/wwwroot/team.hunao.xin/acme/.well-known/acme-challenge/ping.txt")
code, o, e = run(cli, "curl -s -m 5 -H 'Host: team.hunao.xin' http://127.0.0.1/.well-known/acme-challenge/ping.txt; echo")
print("challenge:", repr(o.strip()), "exit", code)

# 2) 上传后端源码与前端 dist（覆盖）
sftp = cli.open_sftp()
LOCAL = r"E:\Project\trae_team"
REMOTE = "/www/wwwroot/team.hunao.xin/server"
files = ["main.py", "database.py", "models.py", "schemas.py", "auth.py",
         "routes_user.py", "routes_post.py", "routes_admin.py", "routes_stats.py",
         "requirements.txt", "run_tests.py", "_seed.py", "_clean.py"]
for f in files:
    lp = os.path.join(LOCAL, "backend", f)
    sftp.put(lp, REMOTE + "/" + f)
print("backend uploaded:", len(files))

# dist 全量同步
web = "/www/wwwroot/team.hunao.xin/web"
def mkdirs(path):
    cur = ""
    for p in path.strip("/").split("/"):
        cur += "/" + p
        try:
            sftp.stat(cur)
        except IOError:
            sftp.mkdir(cur)
count = 0
for root, dirs, fs in os.walk(os.path.join(LOCAL, "frontend", "dist")):
    rel = os.path.relpath(root, os.path.join(LOCAL, "frontend", "dist")).replace("\\", "/")
    rdir = web if rel == "." else web + "/" + rel
    mkdirs(rdir)
    for f in fs:
        sftp.put(os.path.join(root, f), rdir + "/" + f)
        count += 1
print("web uploaded:", count)
sftp.close()

# 3) 依赖 + 重启
code, o, e = run(cli, "cd /www/wwwroot/team.hunao.xin/server && ./venv/bin/pip install -q -i https://mirrors.cloud.tencent.com/pypi/simple -r requirements.txt 2>&1 | tail -3; ./venv/bin/python -c 'import fastapi,uvicorn,sqlalchemy,multipart,passlib,jose;print(\"deps ok\")'", timeout=600)
print("deps exit", code, o.strip()[-300:], e.strip()[-200:])

code, o, e = run(cli, "systemctl restart team-hunao && sleep 4 && systemctl is-active team-hunao && curl -s -m 5 http://127.0.0.1:8020/api/health; echo; tail -5 /www/wwwlogs/team.hunao.xin.api.log")
print("restart:", o.strip()[:600])
cli.close()
