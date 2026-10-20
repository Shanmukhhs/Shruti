import sqlite3
import uuid
import os
from datetime import datetime
from flask import current_app


def generate_uuid():
    """Generate a UUID v4 as a string."""
    return str(uuid.uuid4())


def get_db_path():
    """Get the database file path from config or default."""
    return current_app.config.get('DB_PATH', 'instance/shruti.db')


def get_db_connection():
    """Create a new database connection."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def db_execute(sql, params=None):
    """Execute an INSERT, UPDATE, or DELETE query."""
    if params is None:
        params = ()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def db_query(sql, params=None):
    """Execute a SELECT query and return results."""
    if params is None:
        params = ()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        conn.close()


def db_query_one(sql, params=None):
    """Execute a SELECT query and return a single result."""
    if params is None:
        params = ()
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()
    finally:
        conn.close()


def init_db():
    """Initialize the database with schema.sql."""
    # Ensure instance directory exists
    db_path = get_db_path()
    instance_dir = os.path.dirname(db_path)
    if instance_dir and not os.path.exists(instance_dir):
        os.makedirs(instance_dir, exist_ok=True)

    # Create database and tables if they don't exist
    # schema.sql is in db/ folder at project root
    project_root = os.path.dirname(current_app.root_path)
    schema_path = os.path.join(project_root, 'db', 'schema.sql')
    if not os.path.exists(schema_path):
        current_app.logger.error(f"Schema file not found: {schema_path}")
        return False

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = get_db_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()
        current_app.logger.info("Database initialized successfully")
        return True
    except Exception as e:
        current_app.logger.error(f"Database initialization failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_timestamp():
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat() + 'Z'
