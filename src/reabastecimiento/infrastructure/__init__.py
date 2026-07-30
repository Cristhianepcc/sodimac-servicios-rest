"""Providers de repositorios del proceso `reabastecimiento`."""
from __future__ import annotations

from config import Config
from src.reabastecimiento.domain.inventario import IProductoRepositorio
from src.reabastecimiento.domain.proveedor import IProveedorRepositorio
from src.reabastecimiento.domain.orden_compra import IOrdenCompraRepositorio
from src.reabastecimiento.domain.almacen import IAlmacenRepositorio
from src.reabastecimiento.domain.recepcion import IRecepcionRepositorio, IInspeccionRepositorio
from src.reabastecimiento.domain.distribucion import IDistribucionRepositorio
from src.reabastecimiento.domain.auditoria import IAuditoriaRepositorio, IMovimientoStockRepositorio

_repo_inventario: IProductoRepositorio | None = None
_repo_proveedor: IProveedorRepositorio | None = None
_repo_orden_compra: IOrdenCompraRepositorio | None = None
_repo_almacen: IAlmacenRepositorio | None = None
_repo_recepcion: IRecepcionRepositorio | None = None
_repo_inspeccion: IInspeccionRepositorio | None = None
_repo_distribucion: IDistribucionRepositorio | None = None
_repo_auditoria: IAuditoriaRepositorio | None = None
_repo_movimiento_stock: IMovimientoStockRepositorio | None = None


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


def get_proveedor_repositorio() -> IProveedorRepositorio:
    global _repo_proveedor
    if _repo_proveedor is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .proveedor_sqlalchemy import ProveedorRepositorioSQLAlchemy
            _repo_proveedor = ProveedorRepositorioSQLAlchemy()
        else:
            from .proveedor_memoria import ProveedorRepositorioMemoria
            _repo_proveedor = ProveedorRepositorioMemoria()
    return _repo_proveedor


def get_orden_compra_repositorio() -> IOrdenCompraRepositorio:
    global _repo_orden_compra
    if _repo_orden_compra is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .orden_compra_sqlalchemy import OrdenCompraRepositorioSQLAlchemy
            _repo_orden_compra = OrdenCompraRepositorioSQLAlchemy()
        else:
            from .orden_compra_memoria import OrdenCompraRepositorioMemoria
            _repo_orden_compra = OrdenCompraRepositorioMemoria()
    return _repo_orden_compra


def get_almacen_repositorio() -> IAlmacenRepositorio:
    global _repo_almacen
    if _repo_almacen is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .almacen_sqlalchemy import AlmacenRepositorioSQLAlchemy
            _repo_almacen = AlmacenRepositorioSQLAlchemy()
        else:
            from .almacen_memoria import AlmacenRepositorioMemoria
            _repo_almacen = AlmacenRepositorioMemoria()
    return _repo_almacen


def get_recepcion_repositorio() -> IRecepcionRepositorio:
    global _repo_recepcion
    if _repo_recepcion is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .recepcion_sqlalchemy import RecepcionRepositorioSQLAlchemy
            _repo_recepcion = RecepcionRepositorioSQLAlchemy()
        else:
            from .recepcion_memoria import RecepcionRepositorioMemoria
            _repo_recepcion = RecepcionRepositorioMemoria()
    return _repo_recepcion


def get_inspeccion_repositorio() -> IInspeccionRepositorio:
    global _repo_inspeccion
    if _repo_inspeccion is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .recepcion_sqlalchemy import InspeccionRepositorioSQLAlchemy
            _repo_inspeccion = InspeccionRepositorioSQLAlchemy()
        else:
            from .recepcion_memoria import InspeccionRepositorioMemoria
            _repo_inspeccion = InspeccionRepositorioMemoria()
    return _repo_inspeccion


def get_distribucion_repositorio() -> IDistribucionRepositorio:
    global _repo_distribucion
    if _repo_distribucion is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .distribucion_sqlalchemy import DistribucionRepositorioSQLAlchemy
            _repo_distribucion = DistribucionRepositorioSQLAlchemy()
        else:
            from .distribucion_memoria import DistribucionRepositorioMemoria
            _repo_distribucion = DistribucionRepositorioMemoria()
    return _repo_distribucion


def get_auditoria_repositorio() -> IAuditoriaRepositorio:
    global _repo_auditoria
    if _repo_auditoria is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .auditoria_sqlalchemy import AuditoriaRepositorioSQLAlchemy
            _repo_auditoria = AuditoriaRepositorioSQLAlchemy()
        else:
            from .auditoria_memoria import AuditoriaRepositorioMemoria
            _repo_auditoria = AuditoriaRepositorioMemoria()
    return _repo_auditoria


def get_movimiento_stock_repositorio() -> IMovimientoStockRepositorio:
    global _repo_movimiento_stock
    if _repo_movimiento_stock is None:
        if Config.REPO_BACKEND == "sqlalchemy":
            from .auditoria_sqlalchemy import MovimientoStockRepositorioSQLAlchemy
            _repo_movimiento_stock = MovimientoStockRepositorioSQLAlchemy()
        else:
            from .auditoria_memoria import MovimientoStockRepositorioMemoria
            _repo_movimiento_stock = MovimientoStockRepositorioMemoria()
    return _repo_movimiento_stock
