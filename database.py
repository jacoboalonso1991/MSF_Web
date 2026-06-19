import sqlite3

conn = sqlite3.connect("hulkamb.db")
cursor = conn.cursor()

# 🟢 Tabla guerras
cursor.execute("""
CREATE TABLE IF NOT EXISTS wars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rival TEXT,
    liga TEXT,
    fecha TEXT,
    resultado TEXT,
    fallos INTEGER,
    defensas INTEGER
)
""")

# 🟢 Tabla infografías
cursor.execute("""
CREATE TABLE IF NOT EXISTS infografias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    imagen TEXT
)
""")

conn.commit()
conn.close()

print("Base de datos lista ✔")