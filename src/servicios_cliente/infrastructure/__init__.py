"""Providers de repositorios del proceso `servicios_cliente`."""
from __future__ import annotations

from config import Config
from src.servicios_cliente.domain.solicitud import ISolicitudRepositorio

_repo_solicitud: ISolicitudRepositorio | None = None


def get_solicitud_repositorio() -> ISolicitudRepositorio:
    global _repo_solicitud
    if _repo_solicitud is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .solicitud_sqlalchemy import SolicitudRepositorioSQLAlchemy

            _repo_solicitud = SolicitudRepositorioSQLAlchemy()
        else:
            from .solicitud_memoria import SolicitudRepositorioMemoria

            _repo_solicitud = SolicitudRepositorioMemoria()
    return _repo_solicitud
