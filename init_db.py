import sqlite3

conn = sqlite3.connect("hulkamb.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS counters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT,
    counter TEXT,
    note TEXT
)
""")

conn.commit()
conn.close()

print("✔ Tabla counters creada")