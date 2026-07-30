"""Application factory de la API Sodimac.

`create_app()` construye la app Flask y **autoregistra** todos los blueprints
que cada integrante define en `src/<proceso>/presentation/*_controller.py`.

Convención (para evitar conflictos de merge): cada controlador expone una
variable de módulo llamada `bp` (una instancia de `flask.Blueprint`). El factory
descubre e importa esos módulos automáticamente; **nadie edita un archivo central
de rutas**.
"""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from flask import Flask, jsonify

from config import Config
from src.shared.http import registrar_manejadores_error
from src.shared.openapi import registrar_openapi

# Procesos de negocio (bounded contexts). Agregar aquí un nuevo proceso solo si
# se crea un proceso de negocio nuevo (no hace falta para agregar servicios).
PROCESOS = ["ventas", "reabastecimiento", "servicios_cliente", "postventa", "rse", "web"]


def _autoregistrar_blueprints(app: Flask) -> None:
    """Importa cada `src/<proceso>/presentation/*_controller.py` y registra su `bp`."""
    base_dir = Path(__file__).parent
    for proceso in PROCESOS:
        paquete_presentacion = f"src.{proceso}.presentation"
        ruta = base_dir / proceso / "presentation"
        if not ruta.is_dir():
            continue
        for mod in pkgutil.iter_modules([str(ruta)]):
            if not mod.name.endswith("_controller"):
                continue
            modulo = importlib.import_module(f"{paquete_presentacion}.{mod.name}")
            bp = getattr(modulo, "bp", None)
            if bp is not None:
                app.register_blueprint(bp)


def create_app() -> Flask:
    # ATENCIÓN (SonarQube python:S4502 — protección CSRF).
    #
    # Esta app sirve dos cosas a la vez:
    #   - una API REST sin estado, consumida por los conectores de Bonita y el
    #     worker de eventos (ahí CSRF no aplica: no hay credencial ambiental);
    #   - el frontend web de postventa (`src/web`), que SÍ usa sesión por cookie
    #     (`session["usuario"]`) y formularios POST como `/login`.
    #
    # Por el segundo, CSRF sí aplica: un sitio de terceros puede hacer que el
    # navegador de un usuario autenticado envíe un POST con su cookie. Falta
    # proteger los formularios de `src/web` (p. ej. CSRFProtect limitado a ese
    # blueprint, dejando la API fuera para no romper a los conectores).
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    # TODO(seguridad): `SECRET_KEY` debe venir siempre del entorno. El valor por
    # defecto firma las cookies de sesión y está en el repositorio, así que
    # cualquiera puede falsificar una sesión en un despliegue real.
    app.secret_key = app.config.get("SECRET_KEY") or "postventa-web-dev"

    if Config.REPO_BACKEND == "sqlalchemy" and Config.AUTO_CREATE_TABLES:
        from src.shared.db import crear_tablas

        crear_tablas()

    registrar_manejadores_error(app)
    _autoregistrar_blueprints(app)
    # Después del autoregistro: la spec se deriva de las rutas ya montadas.
    registrar_openapi(app)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "backend": Config.REPO_BACKEND}), 200

    return app
