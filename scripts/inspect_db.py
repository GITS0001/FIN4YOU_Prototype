import sqlite3
import json

conn = sqlite3.connect('data/fin4you.db')
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
info = {}
for (t,) in tables:
    count = cursor.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    cols = cursor.execute(f"PRAGMA table_info({t})").fetchall()
    sample = cursor.execute(f"SELECT * FROM {t} LIMIT 3").fetchall()
    info[t] = {
        'count': count,
        'columns': [c[1] for c in cols],
        'sample': sample
    }

print(json.dumps(info, indent=2, default=str))
