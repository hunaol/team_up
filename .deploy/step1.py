from ssh import connect, run
import sys

cli = connect()
cmds = [
    "mkdir -p /www/wwwroot/team.hunao.xin/server /www/wwwroot/team.hunao.xin/web /www/wwwroot/team.hunao.xin/acme && echo dirs-ok",
    "python3 -m venv /www/wwwroot/team.hunao.xin/server/venv && echo venv-ok",
    "/www/wwwroot/team.hunao.xin/server/venv/bin/pip -V",
    "/www/wwwroot/team.hunao.xin/server/venv/bin/pip install -i https://mirrors.cloud.tencent.com/pypi/simple --upgrade pip -q 2>&1 | tail -2; echo pip-upgraded",
]
for c in cmds:
    code, o, e = run(cli, c, timeout=600)
    print("$ " + c[:80])
    print("  exit", code, o.strip()[:400])
    if e.strip():
        print("  [err]", e.strip()[:400])
cli.close()
