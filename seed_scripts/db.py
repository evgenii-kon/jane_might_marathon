"""Общая конфигурация подключения к БД для всех seed-скриптов."""

import os
import psycopg2

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "bndcn34894hcn289"),
    "dbname": os.getenv("DB_NAME", "fastapi_db"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)
