"""Repositorio en memoria del servicio de Almacén."""
from __future__ import annotations

from src.reabastecimiento.domain.ubicacion import IUbicacionRepositorio, Ubicacion


class UbicacionRepositorioMemoria(IUbicacionRepositorio):
    def __init__(self) -> None:
        self._por_codigo: dict[str, Ubicacion] = {}
        self._por_sku: dict[str, Ubicacion] = {}

    def adicionar(self, ubicacion: Ubicacion) -> None:
        self._por_codigo[ubicacion.codigo.upper()] = ubicacion
        self._por_sku[ubicacion.sku.upper()] = ubicacion

    def buscar_por_codigo(self, codigo: str) -> Ubicacion | None:
        return self._por_codigo.get(codigo.upper())

    def buscar_por_sku(self, sku: str) -> Ubicacion | None:
        return self._por_sku.get(sku.upper())

    def actualizar(self, ubicacion: Ubicacion) -> None:
        self._por_codigo[ubicacion.codigo.upper()] = ubicacion
        self._por_sku[ubicacion.sku.upper()] = ubicacion
