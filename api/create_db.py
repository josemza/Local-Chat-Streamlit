import sqlite3

def init_db():
    conn = sqlite3.connect('D:\Proyectos_python\Portafolio_LLM\Local-Chat-Streamlit\database\local-chat-streamlit.db')
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