import sqlite3, json
c = sqlite3.connect(r"E:\Project\trae_team\backend\app.db")
tables = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
print("tables", tables)
for t in tables:
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})")]
    rows = list(c.execute(f"select * from {t}"))
    print(t, cols, "rows=", len(rows))
    for r in rows[:12]:
        print("   ", r)
