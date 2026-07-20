"""Helper para endpoints aún no implementados (andamiaje de trabajo en equipo).

Cada integrante reemplaza el cuerpo del controlador por la implementación real
(dominio → aplicación → infraestructura). Mientras tanto, el endpoint existe y
responde 501, de modo que:
  - las rutas ya están registradas (autoregistro funciona),
  - las pruebas de aceptación en Postman pueden escribirse y **fallar** (enfoque
    BDD: primero la prueba falla, luego se implementa hasta que pase).
"""
from __future__ import annotations

from flask import jsonify


def no_implementado(servicio: str, integrante: str):
    return (
        jsonify(
            {
                "error": "Servicio no implementado todavía.",
                "servicio": servicio,
                "responsable": integrante,
                "pista": "Implementar dominio → aplicación → infraestructura → controlador.",
            }
        ),
        501,
    )
