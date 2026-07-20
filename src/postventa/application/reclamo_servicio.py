"""Servicio de aplicación de Reclamos (casos de uso)."""
from __future__ import annotations

from src.postventa.domain.reclamo import Reclamo, ReclamoFabrica
from src.postventa.infrastructure import get_reclamo_repositorio
from src.shared.errores import NoEncontrado


class ReclamoServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_reclamo_repositorio()

    def crear(self, cliente: str, producto: str, motivo: str) -> Reclamo:
        reclamo = ReclamoFabrica.crear(cliente, producto, motivo)
        self._repo.adicionar(reclamo)
        return reclamo

    def obtener(self, reclamo_id: str) -> Reclamo:
        reclamo = self._repo.buscar(reclamo_id)
        if reclamo is None:
            raise NoEncontrado(f"No existe el reclamo '{reclamo_id}'.")
        return reclamo

    def listar(self) -> list[Reclamo]:
        return self._repo.listar()
