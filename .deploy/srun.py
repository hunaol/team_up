import sys, paramiko

HOST = "122.51.48.109"
USER = "root"
PWD = "qwehantao182,"

def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=22, username=USER, password=PWD, timeout=20,
              allow_agent=False, look_for_keys=False)
    return c

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "id; uname -a"
    cli = connect()
    _, out, err = cli.exec_command(cmd, timeout=120)
    print(out.read().decode("utf-8", "replace"))
    e = err.read().decode("utf-8", "replace")
    if e.strip():
        print("--- stderr ---")
        print(e)
    cli.close()
