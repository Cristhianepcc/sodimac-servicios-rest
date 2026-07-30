from __future__ import annotations

from src.reabastecimiento.domain.auditoria import Auditoria, IAuditoriaRepositorio, IMovimientoStockRepositorio, MovimientoStock


class AuditoriaRepositorioMemoria(IAuditoriaRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, Auditoria] = {}

    def adicionar_auditoria(self, auditoria: Auditoria) -> None:
        self._datos[auditoria.id] = auditoria

    def buscar_auditoria(self, auditoria_id: str) -> Auditoria | None:
        return self._datos.get(auditoria_id)

    def listar_auditorias(self) -> list[Auditoria]:
        return list(self._datos.values())

    def actualizar_auditoria(self, auditoria: Auditoria) -> None:
        self._datos[auditoria.id] = auditoria


class MovimientoStockRepositorioMemoria(IMovimientoStockRepositorio):
    def __init__(self) -> None:
        self._datos: list[MovimientoStock] = []

    def adicionar(self, movimiento: MovimientoStock) -> None:
        self._datos.append(movimiento)

    def listar_por_sku(self, sku: str) -> list[MovimientoStock]:
        return [m for m in self._datos if m.sku == sku]

    def listar_todos(self) -> list[MovimientoStock]:
        return list(self._datos)
