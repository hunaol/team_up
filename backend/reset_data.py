"""清空全部业务数据，只保留管理员账号（admin / admin123）。

用法：python reset_data.py
会删除：users / posts / favorites / tokens 全部记录，以及 uploads 下的图片。
保留：admins 表（管理员账号与密码不变）。
"""

import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "app.db")

c = sqlite3.connect(DB)
for t in ("favorites", "tokens", "posts", "users"):
    c.execute("DELETE FROM " + t)
try:
    c.execute("DELETE FROM sqlite_sequence WHERE name IN ('favorites','tokens','posts','users')")
except sqlite3.OperationalError:
    pass
c.commit()

admins = c.execute("SELECT id, username FROM admins").fetchall()
counts = {t: c.execute("SELECT COUNT(*) FROM " + t).fetchone()[0]
          for t in ("users", "posts", "favorites", "tokens", "admins")}
c.close()

# 清空上传的封面图
updir = os.path.join(BASE, "uploads")
removed = 0
if os.path.isdir(updir):
    for name in os.listdir(updir):
        p = os.path.join(updir, name)
        if os.path.isfile(p):
            os.remove(p)
            removed += 1

print("admins kept:", admins)
print("counts:", counts)
print("upload files removed:", removed)
