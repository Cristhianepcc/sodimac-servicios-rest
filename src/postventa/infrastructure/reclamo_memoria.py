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
