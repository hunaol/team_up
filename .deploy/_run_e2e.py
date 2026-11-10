"""把 _e2e_remote.py 传到服务器执行，回收输出后删除临时文件。"""
import sys

from srun import connect

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

cli = connect()
sftp = cli.open_sftp()
sftp.put(r"E:\Project\trae_team\.deploy\_e2e_remote.py", "/tmp/_e2e_remote.py")
sftp.close()

cmd = "cd /tmp && /www/wwwroot/team.hunao.xin/server/venv/bin/python _e2e_remote.py; rm -f /tmp/_e2e_remote.py"
_, out, err = cli.exec_command(cmd, timeout=240)
print(out.read().decode("utf-8", "replace"))
e = err.read().decode("utf-8", "replace")
if e.strip():
    print("--- stderr ---")
    print(e)
cli.close()
