import sqlite3

def add_message(user, message,path_db):
    conn = sqlite3.connect(path_db)
    c = conn.cursor()
    c.execute("INSERT INTO messages (user, message) VALUES (?, ?)", (user, message))
    conn.commit()
    conn.close()

def get_messages(path_db,limit=4,all=True):
    conn = sqlite3.connect(path_db)
    c = conn.cursor()
    if all:
        c.execute("SELECT timestamp, user, message FROM messages ORDER BY id DESC")
    else:
        c.execute("SELECT timestamp, user, message FROM messages ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    # Convertir las tuplas a diccionarios
    messages = [{'timestamp': row[0], 'user': row[1], 'message': row[2]} for row in rows]
    return messages[::-1]