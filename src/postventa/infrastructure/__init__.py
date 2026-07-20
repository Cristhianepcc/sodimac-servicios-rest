"""Providers de repositorios del proceso `postventa`."""
from __future__ import annotations

from config import Config
from src.postventa.domain.reclamo import IReclamoRepositorio

_repo_reclamo: IReclamoRepositorio | None = None


def get_reclamo_repositorio() -> IReclamoRepositorio:
    global _repo_reclamo
    if _repo_reclamo is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .reclamo_sqlalchemy import ReclamoRepositorioSQLAlchemy

            _repo_reclamo = ReclamoRepositorioSQLAlchemy()
        else:
            from .reclamo_memoria import ReclamoRepositorioMemoria

            _repo_reclamo = ReclamoRepositorioMemoria()
    return _repo_reclamo
