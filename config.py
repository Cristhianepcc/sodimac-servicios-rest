"""Configuración de la aplicación.

Lee variables de entorno (o del archivo .env) para decidir el backend de
persistencia y la conexión a PostgreSQL. Por defecto usa el repositorio en
memoria (doble de prueba) para que el proyecto arranque sin base de datos.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # 'memoria' (doble de prueba, default) | 'sqlalchemy' (PostgreSQL)
    REPO_BACKEND = os.getenv("REPO_BACKEND", "memoria")

    # Conexión PostgreSQL usada cuando REPO_BACKEND == 'sqlalchemy'.
    # docker-compose.yml levanta un Postgres que coincide con esta URL por defecto.
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://sodimac:sodimac@localhost:5432/reabastecimiento",
    )

    # Crea las tablas automáticamente al iniciar (útil en desarrollo/laboratorio).
    AUTO_CREATE_TABLES = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
