from ssh import connect, run

CONF_HTTP = """server {
    listen 80;
    listen [::]:80;
    server_name team.hunao.xin;

    root /www/wwwroot/team.hunao.xin/web;

    location ^~ /.well-known/acme-challenge/ {
        root /www/wwwroot/team.hunao.xin/acme;
        default_type text/plain;
        try_files $uri =404;
    }

    location ~ /\\.(?!well-known(?:/|$)) {
        return 404;
    }

    location / {
        return 301 https://$host$request_uri;
    }

    access_log /www/wwwlogs/team.hunao.xin.log;
    error_log  /www/wwwlogs/team.hunao.xin.error.log;
}
"""
# 注意：上面是转义后的反斜杠，写入前需要还原成单个 \.
CONF_HTTP = CONF_HTTP.replace("\\\\.", "\\\\.")

cli = connect()
sftp = cli.open_sftp()
with sftp.file("/www/server/panel/vhost/nginx/team.hunao.xin.conf", "w") as f:
    f.write(CONF_HTTP)
sftp.close()

cmds = [
    "mkdir -p /www/wwwroot/team.hunao.xin/acme/.well-known/acme-challenge && echo ok",
    "nginx -t 2>&1 | tail -3",
    "nginx -s reload && sleep 1 && echo reloaded",
    "curl -s -o /dev/null -w '%{http_code}\\n' -H 'Host: team.hunao.xin' http://127.0.0.1/",
]
for c in cmds:
    code, o, e = run(cli, c, timeout=120)
    print("$ " + c[:70])
    print("  ", o.strip()[:500] or "(empty)")
    if e.strip():
        print("  [err]", e.strip()[:400])
print(open(__file__, encoding="utf-8").name)
print(CONF_HTTP)
cli.close()
