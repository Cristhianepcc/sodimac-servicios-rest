"""Repositorio en memoria (Fake) de Reclamos."""
from __future__ import annotations

from src.postventa.domain.reclamo import IReclamoRepositorio, Reclamo


class ReclamoRepositorioMemoria(IReclamoRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, Reclamo] = {}

    def adicionar(self, reclamo: Reclamo) -> None:
        self._datos[reclamo.id] = reclamo

    def buscar(self, reclamo_id: str) -> Reclamo | None:
        return self._datos.get(reclamo_id)

    def listar(self) -> list[Reclamo]:
        return list(self._datos.values())

    def actualizar(self, reclamo: Reclamo) -> None:
        self._datos[reclamo.id] = reclamo

    def listar_abiertos(self, page: int, size: int) -> tuple[list[Reclamo], int]:
        reclamos = [
            r
            for r in self._datos.values()
            if r.fecha_cierre is None or r.estado.value != "RESUELTO"
        ]
        return self._paginar(reclamos, page, size)

    def listar_para_evaluacion(self, page: int, size: int) -> tuple[list[Reclamo], int]:
        reclamos = [r for r in self._datos.values() if r.cumple_garantia is True]
        return self._paginar(reclamos, page, size)

    def listar_para_solucion(self, page: int, size: int) -> tuple[list[Reclamo], int]:
        reclamos = [r for r in self._datos.values() if r.procede_evaluacion is True]
        return self._paginar(reclamos, page, size)

    def _paginar(self, reclamos: list[Reclamo], page: int, size: int) -> tuple[list[Reclamo], int]:
        inicio = (page - 1) * size
        fin = inicio + size
        return reclamos[inicio:fin], len(reclamos)
