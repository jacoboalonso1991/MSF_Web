import sqlite3

conn = sqlite3.connect("hulkamb.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    tcp TEXT,
    role TEXT
)
""")

conn.commit()
conn.close()

print("✔ Tabla members creada")