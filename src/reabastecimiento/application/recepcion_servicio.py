from __future__ import annotations

from src.reabastecimiento.domain.recepcion import (
    Inspeccion,
    InspeccionFabrica,
    Recepcion,
    RecepcionFabrica,
)
from src.reabastecimiento.infrastructure import (
    get_inspeccion_repositorio,
    get_recepcion_repositorio,
)
from src.shared.errores import NoEncontrado


class RecepcionServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_recepcion_repositorio()

    def registrar(self, orden_compra_id: str, items: list[dict]) -> Recepcion:
        recepcion = RecepcionFabrica.crear(orden_compra_id, items)
        self._repo.adicionar_recepcion(recepcion)
        return recepcion

    def obtener(self, recepcion_id: str) -> Recepcion:
        r = self._repo.buscar_recepcion(recepcion_id)
        if r is None:
            raise NoEncontrado(f"No existe la recepción '{recepcion_id}'.")
        return r

    def listar(self) -> list[Recepcion]:
        return self._repo.listar_recepciones()

    def confirmar(self, recepcion_id: str) -> Recepcion:
        r = self.obtener(recepcion_id)
        r.confirmar()
        self._repo.actualizar_recepcion(r)
        return r


class InspeccionServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_inspeccion_repositorio()

    def crear(self, recepcion_id: str) -> Inspeccion:
        inspeccion = InspeccionFabrica.crear(recepcion_id)
        self._repo.adicionar(inspeccion)
        return inspeccion

    def obtener(self, inspeccion_id: str) -> Inspeccion:
        i = self._repo.buscar(inspeccion_id)
        if i is None:
            raise NoEncontrado(f"No existe la inspección '{inspeccion_id}'.")
        return i

    def validar(self, inspeccion_id: str, observaciones: str = "") -> Inspeccion:
        i = self.obtener(inspeccion_id)
        i.validar(observaciones)
        self._repo.actualizar(i)
        return i

    def rechazar(self, inspeccion_id: str, observaciones: str) -> Inspeccion:
        i = self.obtener(inspeccion_id)
        i.rechazar(observaciones)
        self._repo.actualizar(i)
        return i

    def listar_por_recepcion(self, recepcion_id: str) -> list[Inspeccion]:
        return self._repo.listar_por_recepcion(recepcion_id)
