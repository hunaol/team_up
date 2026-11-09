from ssh import connect, run

cli = connect()
cmds = [
    # 确保 cert 目录存在
    "mkdir -p /www/server/panel/vhost/cert/team.hunao.xin && echo dir-ok",
    # 签发（ZeroSSL，webroot 验证，EC-256）
    "~/.acme.sh/acme.sh --issue -d team.hunao.xin --webroot /www/wwwroot/team.hunao.xin/acme --keylength ec-256 --server zerossl 2>&1 | tail -25",
]
for c in cmds:
    code, o, e = run(cli, c, timeout=300)
    print("$ " + c[:70])
    print(o.strip()[:2000])
    if e.strip():
        print("[err]", e.strip()[:500])
cli.close()
