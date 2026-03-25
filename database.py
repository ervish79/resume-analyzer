import sqlite3
import bcrypt

# Create database connection
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# CREATE TABLES
# =========================

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password BLOB
)
""")

# Resume history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT,
    score REAL,
    found TEXT,
    missing TEXT
)
""")

conn.commit()

# =========================
# USER FUNCTIONS
# =========================

def add_user(username, password):
    try:
        # Hash password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        return True
    except:
        return False

def get_user(username, password):
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()

    if result:
        stored_password = result[0]

        if bcrypt.checkpw(password.encode(), stored_password):
            return True

    return False


def get_all_users():
    cursor.execute("SELECT username FROM users")
    return cursor.fetchall()

# =========================
# HISTORY FUNCTIONS
# =========================

def save_result(username, role, score, found, missing):
    cursor.execute(
        "INSERT INTO history (username, role, score, found, missing) VALUES (?, ?, ?, ?, ?)",
        (username, role, score, ", ".join(found), ", ".join(missing))
    )
    conn.commit()

def get_history(username):
    cursor.execute("SELECT role, score, found, missing FROM history WHERE username=?", (username,))
    return cursor.fetchall()


# =========================
# ADMIN STATS FUNCTION
# =========================
def get_admin_stats():
    """
    Returns total resumes analyzed and average score
    """
    cursor.execute("SELECT COUNT(*) FROM history")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM history")
    avg = cursor.fetchone()[0]

    return total, avg