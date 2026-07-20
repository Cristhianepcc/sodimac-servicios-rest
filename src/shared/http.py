"""Utilidades HTTP compartidas por los controladores (capa presentación).

Centraliza el registro de manejadores de error para traducir excepciones de
dominio a respuestas JSON, de modo que los controladores no repitan try/except.
"""
from __future__ import annotations

from flask import Flask, jsonify

from src.shared.errores import ErrorDominio


def registrar_manejadores_error(app: Flask) -> None:
    @app.errorhandler(ErrorDominio)
    def _manejar_error_dominio(exc: ErrorDominio):
        return jsonify({"error": str(exc)}), exc.codigo_http

    @app.errorhandler(404)
    def _no_encontrado(_exc):
        return jsonify({"error": "Recurso no encontrado."}), 404

    @app.errorhandler(400)
    def _peticion_invalida(exc):
        return jsonify({"error": getattr(exc, "description", "Petición inválida.")}), 400
