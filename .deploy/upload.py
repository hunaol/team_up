import os, sys
from ssh import connect, run, put_dir

cli = connect()
LOCAL = r"E:\Project\trae_team"
REMOTE = "/www/wwwroot/team.hunao.xin/server"

# 只上传运行所需文件，跳过 pycache / 本地 uploads 大文件
files = ["main.py", "database.py", "models.py", "schemas.py", "auth.py",
         "routes_user.py", "routes_post.py", "routes_admin.py", "routes_stats.py",
         "requirements.txt", "run_tests.py", "_seed.py", "_clean.py", "app.db"]

sftp = cli.open_sftp()
for f in files:
    lp = os.path.join(LOCAL, "backend", f)
    if os.path.exists(lp):
        sftp.put(lp, REMOTE + "/" + f)
        print("put", f, os.path.getsize(lp))
sftp.close()

# 前端静态资源
n = put_dir(cli, os.path.join(LOCAL, "frontend", "dist"), "/www/wwwroot/team.hunao.xin/web")
print("web files:", n)

code, o, e = run(cli, "ls -la /www/wwwroot/team.hunao.xin/server | head -20; ls /www/wwwroot/team.hunao.xin/web")
print(o)
cli.close()
