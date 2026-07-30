from __future__ import annotations

from src.reabastecimiento.domain.recepcion import (
    IInspeccionRepositorio,
    IRecepcionRepositorio,
    Inspeccion,
    Recepcion,
)


class RecepcionRepositorioMemoria(IRecepcionRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, Recepcion] = {}

    def adicionar_recepcion(self, recepcion: Recepcion) -> None:
        self._datos[recepcion.id] = recepcion

    def buscar_recepcion(self, recepcion_id: str) -> Recepcion | None:
        return self._datos.get(recepcion_id)

    def listar_recepciones(self) -> list[Recepcion]:
        return list(self._datos.values())

    def actualizar_recepcion(self, recepcion: Recepcion) -> None:
        self._datos[recepcion.id] = recepcion


class InspeccionRepositorioMemoria(IInspeccionRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, Inspeccion] = {}

    def adicionar(self, inspeccion: Inspeccion) -> None:
        self._datos[inspeccion.id] = inspeccion

    def buscar(self, inspeccion_id: str) -> Inspeccion | None:
        return self._datos.get(inspeccion_id)

    def listar_por_recepcion(self, recepcion_id: str) -> list[Inspeccion]:
        return [i for i in self._datos.values() if i.recepcion_id == recepcion_id]

    def actualizar(self, inspeccion: Inspeccion) -> None:
        self._datos[inspeccion.id] = inspeccion
