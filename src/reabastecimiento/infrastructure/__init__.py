"""Providers de repositorios del proceso `reabastecimiento`.

Cada servicio (Inventario, Compras, Recepción, Almacén, Distribución, Auditoría)
expone su propio `get_*_repositorio()`. Aquí está el de Inventario (referencia);
cada integrante agrega el suyo al implementar su servicio.
"""
from __future__ import annotations

from config import Config
from src.reabastecimiento.domain.inventario import IProductoRepositorio
from src.reabastecimiento.domain.ordenes_compra import IOrdenCompraRepositorio
from src.reabastecimiento.domain.ubicacion import IUbicacionRepositorio

_repo_inventario: IProductoRepositorio | None = None
_repo_ordenes_compra: IOrdenCompraRepositorio | None = None
_repo_almacen: IUbicacionRepositorio | None = None


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


def get_ordenes_compra_repositorio() -> IOrdenCompraRepositorio:
    global _repo_ordenes_compra
    if _repo_ordenes_compra is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .ordenes_compra_sqlalchemy import OrdenCompraRepositorioSQLAlchemy

            _repo_ordenes_compra = OrdenCompraRepositorioSQLAlchemy()
        else:
            from .ordenes_compra_memoria import OrdenCompraRepositorioMemoria

            _repo_ordenes_compra = OrdenCompraRepositorioMemoria()
    return _repo_ordenes_compra


def get_almacen_repositorio() -> IUbicacionRepositorio:
    global _repo_almacen
    if _repo_almacen is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .almacen_sqlalchemy import UbicacionRepositorioSQLAlchemy

            _repo_almacen = UbicacionRepositorioSQLAlchemy()
        else:
            from .almacen_memoria import UbicacionRepositorioMemoria

            _repo_almacen = UbicacionRepositorioMemoria()
    return _repo_almacen
