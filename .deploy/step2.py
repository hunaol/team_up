from ssh import connect, run

UNIT = """[Unit]
Description=team.hunao.xin - campus recruit API (FastAPI)
After=network.target

[Service]
Type=simple
WorkingDirectory=/www/wwwroot/team.hunao.xin/server
ExecStart=/www/wwwroot/team.hunao.xin/server/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8020 --workers 1 --proxy-headers --forwarded-allow-ips 127.0.0.1
Restart=always
RestartSec=3
User=root
StandardOutput=append:/www/wwwlogs/team.hunao.xin.api.log
StandardError=append:/www/wwwlogs/team.hunao.xin.api.log

[Install]
WantedBy=multi-user.target
"""

cli = connect()
sftp = cli.open_sftp()
with sftp.file("/etc/systemd/system/team-hunao.service", "w") as f:
    f.write(UNIT)
sftp.close()

cmds = [
    "systemctl daemon-reload && systemctl enable team-hunao --now 2>&1 | tail -3",
    "sleep 4; systemctl is-active team-hunao",
    "curl -s -m 5 http://127.0.0.1:8020/api/health; echo",
    "curl -s -m 5 'http://127.0.0.1:8020/api/stats/overview' | head -c 300; echo",
    "tail -12 /www/wwwlogs/team.hunao.xin.api.log",
]
for c in cmds:
    code, o, e = run(cli, c, timeout=120)
    print("$ " + c[:70])
    print("  ", o.strip()[:400] or "(empty)")
    if e.strip():
        print("  [err]", e.strip()[:300])
cli.close()
