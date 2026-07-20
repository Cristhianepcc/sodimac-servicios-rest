"""Provider del repositorio de `ventas`.

Devuelve un singleton según `REPO_BACKEND` (memoria | sqlalchemy). Los servicios
de aplicación llaman a `get_repositorio()` sin conocer la implementación concreta.
"""
from __future__ import annotations

from config import Config
from src.ventas.domain.repositorio import ICarritoRepositorio

_repositorio: ICarritoRepositorio | None = None


def get_repositorio() -> ICarritoRepositorio:
    global _repositorio
    if _repositorio is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .repositorio_sqlalchemy import CarritoRepositorioSQLAlchemy

            _repositorio = CarritoRepositorioSQLAlchemy()
        else:
            from .repositorio_memoria import CarritoRepositorioMemoria

            _repositorio = CarritoRepositorioMemoria()
    return _repositorio
