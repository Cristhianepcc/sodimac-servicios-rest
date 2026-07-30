from __future__ import annotations

from src.reabastecimiento.domain.auditoria import (
    Auditoria,
    AuditoriaFabrica,
    MovimientoStock,
    MovimientoStockFabrica,
)
from src.reabastecimiento.infrastructure import (
    get_auditoria_repositorio,
    get_movimiento_stock_repositorio,
)
from src.shared.errores import NoEncontrado


class AuditoriaServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_auditoria_repositorio()

    def crear(self, sku: str, tipo: str) -> Auditoria:
        auditoria = AuditoriaFabrica.crear(sku, tipo)
        self._repo.adicionar_auditoria(auditoria)
        return auditoria

    def obtener(self, auditoria_id: str) -> Auditoria:
        a = self._repo.buscar_auditoria(auditoria_id)
        if a is None:
            raise NoEncontrado(f"No existe la auditoría '{auditoria_id}'.")
        return a

    def listar(self) -> list[Auditoria]:
        return self._repo.listar_auditorias()

    def completar(self, auditoria_id: str, observaciones: str = "") -> Auditoria:
        a = self.obtener(auditoria_id)
        a.completar(observaciones)
        self._repo.actualizar_auditoria(a)
        return a


class MovimientoStockServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_movimiento_stock_repositorio()

    def registrar(self, sku: str, tipo: str, cantidad: int, motivo: str, usuario: str = "") -> MovimientoStock:
        movimiento = MovimientoStockFabrica.crear(sku, tipo, cantidad, motivo, usuario)
        self._repo.adicionar(movimiento)
        return movimiento

    def historial(self, sku: str) -> list[MovimientoStock]:
        return self._repo.listar_por_sku(sku)

    def listar_todos(self) -> list[MovimientoStock]:
        return self._repo.listar_todos()
