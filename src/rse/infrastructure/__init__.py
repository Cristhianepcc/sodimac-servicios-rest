"""Providers de repositorios del proceso `rse`."""
from __future__ import annotations

from config import Config
from src.rse.domain.iniciativa import IIniciativaRepositorio

_repo_iniciativa: IIniciativaRepositorio | None = None


def get_iniciativa_repositorio() -> IIniciativaRepositorio:
    global _repo_iniciativa
    if _repo_iniciativa is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .iniciativa_sqlalchemy import IniciativaRepositorioSQLAlchemy

            _repo_iniciativa = IniciativaRepositorioSQLAlchemy()
        else:
            from .iniciativa_memoria import IniciativaRepositorioMemoria

            _repo_iniciativa = IniciativaRepositorioMemoria()
    return _repo_iniciativa
