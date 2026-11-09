from ssh import connect, run

cli = connect()
sftp = cli.open_sftp()
sftp.put(r"E:\Project\trae_team\backend\reset_data.py",
         "/www/wwwroot/team.hunao.xin/server/reset_data.py")
sftp.close()

cmds = [
    "cd /www/wwwroot/team.hunao.xin/server && cp app.db app.db.dirty-backup-$(date +%Y%m%d-%H%M%S) && ls -la app.db*",
    "cd /www/wwwroot/team.hunao.xin/server && ./venv/bin/python reset_data.py",
    "systemctl restart team-hunao && sleep 3 && systemctl is-active team-hunao",
]
for c in cmds:
    code, o, e = run(cli, c, timeout=120)
    print("$ " + c[:60])
    print(o.strip()[:800])
    if e.strip():
        print("[err]", e.strip()[:300])
cli.close()
