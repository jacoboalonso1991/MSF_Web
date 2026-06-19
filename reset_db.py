import sqlite3

conn = sqlite3.connect("hulkamb.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS wars")

cursor.execute("""
CREATE TABLE wars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rival TEXT,
    liga TEXT,
    fecha TEXT,
    resultado TEXT,
    fallos INTEGER,
    defensas INTEGER
)
""")

conn.commit()
conn.close()

print("Base de datos reiniciada correctamente")