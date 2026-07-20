"""Providers de repositorios del proceso `reabastecimiento`.

Cada servicio (Inventario, Compras, Recepción, Almacén, Distribución, Auditoría)
expone su propio `get_*_repositorio()`. Aquí está el de Inventario (referencia);
cada integrante agrega el suyo al implementar su servicio.
"""
from __future__ import annotations

from config import Config
from src.reabastecimiento.domain.inventario import IProductoRepositorio

_repo_inventario: IProductoRepositorio | None = None


def get_inventario_repositorio() -> IProductoRepositorio:
    global _repo_inventario
    if _repo_inventario is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .inventario_sqlalchemy import ProductoRepositorioSQLAlchemy

            _repo_inventario = ProductoRepositorioSQLAlchemy()
        else:
            from .inventario_memoria import ProductoRepositorioMemoria

            _repo_inventario = ProductoRepositorioMemoria()
    return _repo_inventario
