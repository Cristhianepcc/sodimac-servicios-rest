"""Errores de dominio/aplicación compartidos por todos los módulos.

Los controladores traducen estas excepciones a códigos HTTP (ver
`src/shared/http.py`). Así el dominio permanece agnóstico de HTTP.
"""


class ErrorDominio(Exception):
    """Violación de una regla de negocio (→ HTTP 400)."""

    codigo_http = 400


class NoEncontrado(ErrorDominio):
    """La entidad solicitada no existe (→ HTTP 404)."""

    codigo_http = 404


class Conflicto(ErrorDominio):
    """Conflicto de estado, p. ej. recurso duplicado (→ HTTP 409)."""

    codigo_http = 409
