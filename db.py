# db.py
# ============================================================
# Thin wrapper around mysql.connector.
# All queries use parameterized inputs to prevent SQL injection.
# ============================================================

import mysql.connector
from config import Config


def get_connection():
    """Return a new MySQL connection using settings from Config."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        autocommit=False
    )


def execute_query(query, params=None, fetch=True):
    """
    Execute a SELECT query and return all rows as a list of dicts.
    params must be a tuple or list (never concatenate user input!).
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        return []
    finally:
        cursor.close()
        conn.close()


def execute_write(query, params=None):
    """
    Execute an INSERT / UPDATE / DELETE and commit.
    Returns lastrowid for INSERT statements.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
