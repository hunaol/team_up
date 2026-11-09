from ssh import connect, run
import json

cli = connect()
cmds = {
  "os": "cat /etc/os-release | head -2; uname -m",
  "pkg": "which dnf yum apt-get; dnf --version 2>/dev/null | head -1",
  "nginx": "nginx -v 2>&1; ls /etc/nginx/; cat /etc/nginx/nginx.conf | head -60",
  "node": "node -v 2>/dev/null; npm -v 2>/dev/null; ls /usr/local/bin | head -30",
  "py": "python3 -V; ls /www/server/panel/vhost/nginx 2>/dev/null | head; ls /www/server/panel/vhost/nginx 2>/dev/null | wc -l",
  "ports": "ss -ltnp | grep -E ':(3000|8000|5173|9000)' || echo none",
  "cert": "ls /etc/letsencrypt/live 2>/dev/null; ls /www/server/panel/vhost/cert 2>/dev/null | head -20",
}
for k, c in cmds.items():
    code, o, e = run(cli, c)
    print("=== " + k + " (exit " + str(code) + ")")
    print(o.strip())
    if e.strip(): print("[err]", e.strip()[:300])
cli.close()
