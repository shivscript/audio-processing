import sqlite3
import logging

logger = logging.getLogger(__name__)

DB_FILE = "users.db"

def init_db():
    """Initialize SQLite database"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        conn.commit()


def get_user(user_id=None, username=None):
    """Retrieve user by ID or username"""
    query = "SELECT * FROM users WHERE id = ?" if user_id else "SELECT * FROM users WHERE username = ?"
    param = (user_id,) if user_id else (username,)

    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(query, param)
            return c.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None


def insert_user(username, password):
    """Insert new user if username is unique"""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
