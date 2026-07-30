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

    # --- Mensajería asíncrona (integración con los procesos BPM de Bonita) ---
    # 'memoria' (doble de prueba, default) | 'rabbitmq' (broker real)
    EVENTOS_BACKEND = os.getenv("EVENTOS_BACKEND", "memoria")

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_HEARTBEAT = int(os.getenv("RABBITMQ_HEARTBEAT", "600"))
    RABBITMQ_TIMEOUT = int(os.getenv("RABBITMQ_TIMEOUT", "300"))

    # Colas compartidas con el proceso BPM (mismos nombres que en Bonita/lab6).
    COLA_CONVOCATORIAS = os.getenv("COLA_CONVOCATORIAS", "rse.convocatorias")
    COLA_POSTULACIONES = os.getenv("COLA_POSTULACIONES", "rse.postulaciones")
    # Salida: el servicio notifica al proceso BPM el resultado de sus tareas
    # automáticas (la ServiceTask "Consolidar KPIs" consume de esta cola).
    COLA_NOTIFICACIONES = os.getenv("COLA_NOTIFICACIONES", "rse.notificaciones")
