import sqlite3

conn = sqlite3.connect('mensajes.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(mensajes)")
columnas = cursor.fetchall()

for col in columnas:
    print(col)

conn.close()
