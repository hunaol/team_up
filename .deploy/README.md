# 部署说明（已在服务器上完成）

## 访问地址

| 项目 | 地址 |
| --- | --- |
| 站点 | https://team.hunao.xin |
| 管理后台 | https://team.hunao.xin/admin/login |
| 后端健康检查 | https://team.hunao.xin/api/health |
| 服务器 | 122.51.48.109（root，22 端口） |

学生登录：学号 + 姓名（演示账号 `2024413435 / 韩涛`）；管理员 `admin / admin123`。

## 服务器结构

```
/www/wwwroot/team.hunao.xin/
  server/                     FastAPI 代码 + venv + app.db + uploads/
  web/                        前端 dist（Vue 3 构建产物）
  acme/                       Let's Encrypt / ZeroSSL 的 webroot 验证目录
/etc/systemd/system/team-hunao.service       后端服务（uvicorn 127.0.0.1:8020）
/www/server/panel/vhost/nginx/team.hunao.xin.conf   Nginx 站点配置（宝塔目录）
/www/server/panel/vhost/cert/team.hunao.xin/        证书 fullchain.pem / privkey.pem
/www/wwwlogs/team.hunao.xin.log                     访问日志
/www/wwwlogs/team.hunao.xin.api.log                 后端日志
```

Nginx：80 端口只保留 ACME 验证并 301 到 HTTPS；443 端口静态指向 `web/`，
`/api/` 反代到 `127.0.0.1:8020`，其余路径 `try_files ... /index.html`（SPA 回退）。

## 证书

ZeroSSL ECC（ACME 账号 `admin@hunao.xin`），有效期至 2027-02-07，
`acme.sh` 已带 `--reloadcmd "nginx -s reload"` 安装钩子，每天 16:11 的 cron 会自动续期并重载 Nginx。

手动续期 / 重装：

```bash
~/.acme.sh/acme.sh --renew -d team.hunao.xin --ecc --force
~/.acme.sh/acme.sh --install-cert -d team.hunao.xin --keylength ec-256 \
  --key-file /www/server/panel/vhost/cert/team.hunao.xin/privkey.pem \
  --fullchain-file /www/server/panel/vhost/cert/team.hunao.xin/fullchain.pem \
  --reloadcmd "nginx -s reload"
```

## 更新发布

前端改完后本地构建，再把 `dist` 和后端代码推上去：

```powershell
cd E:\Project\trae_team\frontend
npm run build
cd E:\Project\trae_team\.deploy
python deploy1.py          # 上传 backend 代码 + dist，装依赖，重启服务
```

只改后端时，可直接 `python deploy1.py`（会一并重传 dist，无副作用）。
改 Nginx / 证书用 `deploy3_site.py`、`deploy2_cert.py`。

常用运维命令：

```bash
systemctl status team-hunao          # 后端状态
systemctl restart team-hunao         # 重启后端
tail -f /www/wwwlogs/team.hunao.xin.api.log
nginx -t && nginx -s reload
```

## 数据

线上 `app.db` 目前是**空库**：`users / posts / favorites / tokens` 全部为 0，
只保留一个管理员账号 `admin / admin123`（`admins` 表 1 条）。上传目录也已清空。

清空业务数据（保留管理员）：
`cd /www/wwwroot/team.hunao.xin/server && ./venv/bin/python reset_data.py`

重新灌演示数据（4 用户 / 6 招募，仅用于测试环境）：
`cd /www/wwwroot/team.hunao.xin/server && ./venv/bin/python _seed.py`

备份：`cp app.db app.db.$(date +%F-%H%M)`
本次清空前的脏数据备份在服务器：`/www/wwwroot/team.hunao.xin/server/app.db.dirty-backup-20261109-225511`
