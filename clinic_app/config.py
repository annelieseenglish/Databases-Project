# config.py
# ============================================================
# Application configuration.
# Edit DB credentials before running locally.
# ============================================================

import os

class Config:
    # ----------------------------------------------------------
    # MySQL connection settings
    # Change these to match your local MySQL installation.
    # ----------------------------------------------------------
    DB_HOST     = os.environ.get('DB_HOST',     'localhost')
    DB_PORT     = int(os.environ.get('DB_PORT', 3306))
    DB_USER     = os.environ.get('DB_USER',     'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password')  # ← change this
    DB_NAME     = os.environ.get('DB_NAME',     'clinic_db')

    # Flask secret key (used for flash messages / sessions)
    SECRET_KEY  = os.environ.get('SECRET_KEY',  'clinic-dev-secret-2026')

    # Business hours enforcement
    BUSINESS_START_HOUR = 8    # 08:00
    BUSINESS_END_HOUR   = 17   # 17:00 (5 PM)
