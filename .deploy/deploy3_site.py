CONF = r"""
server {
    listen 80;
    listen [::]:80;
    server_name team.hunao.xin;

    location ^~ /.well-known/acme-challenge/ {
        root /www/wwwroot/team.hunao.xin/acme;
        default_type text/plain;
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;
    }

    access_log /www/wwwlogs/team.hunao.xin.log;
    error_log  /www/wwwlogs/team.hunao.xin.error.log;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name team.hunao.xin;

    root /www/wwwroot/team.hunao.xin/web;
    index index.html;

    ssl_certificate     /www/server/panel/vhost/cert/team.hunao.xin/fullchain.pem;
    ssl_certificate_key /www/server/panel/vhost/cert/team.hunao.xin/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    error_page 497 https://$host$request_uri;

    client_max_body_size 10m;

    location ^~ /api/ {
        proxy_pass http://127.0.0.1:8020;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Real-Port $remote_port;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    location ^~ /assets/ {
        expires 30d;
        add_header Cache-Control "public";
        try_files $uri =404;
    }

    location ~* \.(svg|png|jpg|jpeg|webp|gif|ico|woff2?|ttf)$ {
        expires 7d;
        add_header Cache-Control "public";
        try_files $uri =404;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~ /\.(?!well-known) {
        return 404;
    }

    access_log /www/wwwlogs/team.hunao.xin.log;
    error_log  /www/wwwlogs/team.hunao.xin.error.log;
}
"""

from ssh import connect, run

cli = connect()
sftp = cli.open_sftp()
with sftp.file("/www/server/panel/vhost/nginx/team.hunao.xin.conf", "w") as f:
    f.write(CONF)
sftp.close()
print("conf written")

code, o, e = run(cli, "~/.acme.sh/acme.sh --install-cert -d team.hunao.xin --keylength ec-256 "
                      "--key-file /www/server/panel/vhost/cert/team.hunao.xin/privkey.pem "
                      "--fullchain-file /www/server/panel/vhost/cert/team.hunao.xin/fullchain.pem "
                      "--reloadcmd 'nginx -s reload' 2>&1 | tail -8", timeout=120)
print("install-cert exit", code)
print(o.strip())

code, o, e = run(cli, "nginx -t 2>&1 | tail -4", timeout=60)
print("nginx -t:", o.strip()[-400:])
code, o, e = run(cli, "nginx -s reload && sleep 2 && echo reloaded", timeout=60)
print(o.strip()[:200], e.strip()[:300])
