import sqlite3

def init_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    # Creamos la tabla si no existe
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
              user TEXT,
              message TEXT
              )
    ''')

    conn.commit()
    conn.close()