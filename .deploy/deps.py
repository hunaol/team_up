from ssh import connect, run

cli = connect()
cmd = ("cd /www/wwwroot/team.hunao.xin/server && "
       "./venv/bin/pip install -i https://mirrors.cloud.tencent.com/pypi/simple -q -r requirements.txt 2>&1 | tail -5; "
       "./venv/bin/python -c 'import fastapi,uvicorn,sqlalchemy,multipart;print(\"deps ok\", fastapi.__version__, sqlalchemy.__version__)'")
code, o, e = run(cli, cmd, timeout=900)
print("exit", code)
print(o)
print(e[:800])
cli.close()
