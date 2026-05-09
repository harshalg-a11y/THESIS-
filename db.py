import sqlite3
import os
import hashlib
from flask import g

# Database configuration
DB_TYPE = os.environ.get('DB_TYPE', 'sqlite') # Default to sqlite if mysql is not available

def hash_password(password):
    salt = "academic_sophistication_salt"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def get_db():
    if DB_TYPE == 'mysql':
        import pymysql
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = pymysql.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                user=os.environ.get('DB_USER', 'root'),
                password=os.environ.get('DB_PASS', 'your_password'),
                database=os.environ.get('DB_NAME', 'thesis_portal'),
                cursorclass=pymysql.cursors.DictCursor
            )
        return db
    else:
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect('thesis_portal.db')
            db.row_factory = sqlite3.Row
        return db

def init_db():
    if DB_TYPE == 'mysql':
        # In a real MySQL setup, schema would be applied via mysql_schema.sql
        print("Using MySQL. Please ensure mysql_schema.sql is applied.")
        return

    with sqlite3.connect('thesis_portal.db') as conn:
        cursor = conn.cursor()

        # Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                avatar_url TEXT,
                experience_level INTEGER DEFAULT 1
            )
        ''')

        # Thesis Requests Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thesis_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                receiver_id INTEGER NOT NULL,
                sender_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (receiver_id) REFERENCES users (id),
                FOREIGN KEY (sender_id) REFERENCES users (id)
            )
        ''')

        # Messages Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                sender_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                is_lounge BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES thesis_requests (id),
                FOREIGN KEY (sender_id) REFERENCES users (id)
            )
        ''')

        # Guidelines Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guidelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_id) REFERENCES users (id)
            )
        ''')

        # Audit Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Files Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                request_id INTEGER NOT NULL,
                original_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES thesis_requests (id)
            )
        ''')

        # Seed initial users for testing with hashed passwords
        admin_pass = hash_password('admin123')
        sender_pass = hash_password('sender123')
        user_pass = hash_password('user123')

        cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role, full_name, experience_level) VALUES (1, 'admin', ?, 'admin', 'System Administrator', 3)", [admin_pass])
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role, full_name, experience_level) VALUES (2, 'sender1', ?, 'sender', 'Expert Writer 1', 1)", [sender_pass])
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role, full_name, experience_level) VALUES (3, 'sender2', ?, 'sender', 'Expert Writer 2', 2)", [sender_pass])
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role, full_name, experience_level) VALUES (4, 'user1', ?, 'receiver', 'Student User 1', 1)", [user_pass])

        conn.commit()

def query_db(query, args=(), one=False):
    if DB_TYPE == 'mysql':
        query = query.replace('?', '%s') # Convert sqlite param style to mysql
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    if DB_TYPE == 'mysql':
        query = query.replace('?', '%s')
    db = get_db()
    db.execute(query, args)
    db.commit()

def log_audit(user_id, action):
    execute_db("INSERT INTO audit_logs (user_id, action) VALUES (?, ?)", [user_id, action])
