from ssh import connect, run
import json

cli = connect()
cmds = {
  "os": "cat /etc/os-release | head -3; uname -m; nproc",
  "www": "ls -la /www/wwwroot/team.hunao.xin 2>/dev/null || echo no-dir",
  "server_files": "ls -la /www/wwwroot/team.hunao.xin/server 2>/dev/null | head -30",
  "web_files": "ls -la /www/wwwroot/team.hunao.xin/web 2>/dev/null | head -20",
  "svc": "systemctl is-enabled team-hunao 2>&1; systemctl is-active team-hunao 2>&1; systemctl status team-hunao --no-pager -l 2>&1 | tail -20",
  "nginx_conf": "ls -la /www/server/panel/vhost/nginx/team.hunao.xin.conf 2>/dev/null && cat /www/server/panel/vhost/nginx/team.hunao.xin.conf",
  "cert": "ls -la /www/server/panel/vhost/cert/team.hunao.xin/ 2>/dev/null || echo no-cert",
  "ports": "ss -ltnp | grep -E ':(80|443|8020|8000) ' || echo none",
  "nginx_v": "nginx -v 2>&1; nginx -t 2>&1 | tail -3",
  "bt": "ls /www/server/panel/ >/dev/null 2>&1 && echo baota-present; which bt 2>/dev/null",
  "py": "python3 -V; ls /www/wwwroot/team.hunao.xin/server/venv/bin/python 2>/dev/null || echo no-venv",
  "dns": "getent hosts team.hunao.xin || echo no-getent",
  "curl_local": "curl -s -m 5 http://127.0.0.1:8020/api/health; echo",
  "site_list": "ls /www/server/panel/vhost/nginx/ 2>/dev/null | head -20",
}
for k, c in cmds.items():
    code, o, e = run(cli, c, timeout=60)
    print("=== " + k + " (exit " + str(code) + ")")
    print(o.strip()[:1500])
    if e.strip(): print("[err]", e.strip()[:300])
cli.close()
