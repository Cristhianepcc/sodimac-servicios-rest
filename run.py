"""Punto de entrada de la aplicación.

Uso:
    python run.py                         # backend en memoria (default)
    REPO_BACKEND=sqlalchemy python run.py # backend PostgreSQL
"""
from config import Config
from src import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
