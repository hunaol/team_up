"""清理 run_tests.py 产生的测试数据，使测试可从干净状态开始。"""

import sqlite3

TEST_IDS = ("20990001", "20990002")

c = sqlite3.connect("app.db")
uids = [r[0] for r in c.execute(
    "select id from users where student_id in (?, ?)", TEST_IDS)]
for uid in uids:
    pids = [r[0] for r in c.execute("select id from posts where user_id=?", (uid,))]
    for pid in pids:
        c.execute("delete from favorites where post_id=?", (pid,))
    c.execute("delete from favorites where user_id=?", (uid,))
    c.execute("delete from tokens where user_id=?", (uid,))
    c.execute("delete from posts where user_id=?", (uid,))
    c.execute("delete from users where id=?", (uid,))
c.commit()
print("removed users:", uids)
print("users now:", c.execute("select id, student_id from users").fetchall())
