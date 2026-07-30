"""Decoradores de autenticación y autorización compartidos.

Dos variantes:
  - ``login_required(rol)``   → redirige a login (vistas HTML).
  - ``api_login_required(rol)`` → responde 401/403 JSON (endpoints REST).
"""
from __future__ import annotations

from functools import wraps

from flask import Response, jsonify, redirect, session, url_for

# Mapa de home por rol (misma fuente que web_controller para evitar circular).
ROLE_HOME: dict[str, str] = {
    "CLIENTE": "postventa_web.cliente_registrar",
    "POSTVENTA": "postventa_web.postventa_reclamos",
    "TECNICO": "postventa_web.tecnico_evaluaciones",
    "ALMACENERO": "reabastecimiento_web.proveedores",
}


def login_required(rol: str | None = None):
    """Para vistas HTML: redirige a login si no hay sesión, o al home del rol si no coincide."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "usuario" not in session:
                return redirect(url_for("postventa_web.login"))
            if rol and session["usuario"]["rol"] != rol:
                destino = ROLE_HOME.get(session["usuario"]["rol"], "postventa_web.login")
                return redirect(url_for(destino))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def api_login_required(rol: str | None = None):
    """Para endpoints REST: retorna 401/403 JSON en lugar de redirigir."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "usuario" not in session:
                return jsonify({"error": "Autenticación requerida."}), 401
            if rol and session["usuario"]["rol"] != rol:
                return jsonify({"error": f"Acceso no autorizado. Se requiere rol '{rol}'."}), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


def proteger_api_bp(bp, rol: str):
    """Registra un ``before_request`` en el blueprint que exige autenticación y rol.

    Útil para proteger todas las rutas de un blueprint REST sin decorar cada una.
    """
    @bp.before_request
    def _chequear():  # type: ignore[misc]
        if "usuario" not in session:
            return jsonify({"error": "Autenticación requerida."}), 401
        if session["usuario"]["rol"] != rol:
            return jsonify({"error": f"Acceso no autorizado. Se requiere rol '{rol}'."}), 403
