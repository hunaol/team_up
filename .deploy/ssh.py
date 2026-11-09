import os, sys, paramiko

HOST = "122.51.48.109"
USER = "root"
PWD = "qwehantao182,"

def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, port=22, username=USER, password=PWD, timeout=20,
              allow_agent=False, look_for_keys=False)
    return c

def run(cli, cmd, timeout=600):
    _, out, err = cli.exec_command(cmd, timeout=timeout, get_pty=False)
    o = out.read().decode("utf-8", "replace")
    e = err.read().decode("utf-8", "replace")
    code = out.channel.recv_exit_status()
    return code, o, e

def put_dir(cli, local_dir, remote_dir):
    sftp = cli.open_sftp()
    def mkdirs(path):
        parts = path.strip("/").split("/")
        cur = ""
        for p in parts:
            cur += "/" + p
            try:
                sftp.stat(cur)
            except IOError:
                sftp.mkdir(cur)
    mkdirs(remote_dir)
    count = 0
    for root, dirs, files in os.walk(local_dir):
        rel = os.path.relpath(root, local_dir).replace("\\", "/")
        rdir = remote_dir if rel == "." else remote_dir + "/" + rel
        mkdirs(rdir)
        for f in files:
            lp = os.path.join(root, f)
            rp = rdir + "/" + f
            try:
                sftp.put(lp, rp)
                count += 1
            except Exception as ex:
                print("put fail", rp, ex)
    sftp.close()
    return count
