"""Servicio de aplicación del Proveedor (casos de uso)."""
from __future__ import annotations

from src.reabastecimiento.domain.proveedor import (
    Proveedor,
    ProveedorFabrica,
)
from src.reabastecimiento.infrastructure import get_proveedor_repositorio
from src.shared.errores import Conflicto, NoEncontrado


class ProveedorServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_proveedor_repositorio()

    def registrar(self, nombre: str, ruc: str) -> Proveedor:
        proveedor = ProveedorFabrica.crear(nombre, ruc)
        self._repo.adicionar(proveedor)
        return proveedor

    def obtener(self, proveedor_id: str) -> Proveedor:
        proveedor = self._repo.buscar(proveedor_id)
        if proveedor is None:
            raise NoEncontrado(f"No existe el proveedor '{proveedor_id}'.")
        return proveedor

    def listar(self) -> list[Proveedor]:
        return self._repo.listar()

    def evaluar(self, proveedor_id: str, puntaje: int) -> Proveedor:
        proveedor = self.obtener(proveedor_id)
        proveedor.evaluar(puntaje)
        self._repo.actualizar(proveedor)
        return proveedor

    def aprobar(self, proveedor_id: str) -> Proveedor:
        proveedor = self.obtener(proveedor_id)
        proveedor.aprobar()
        self._repo.actualizar(proveedor)
        return proveedor

    def rechazar(self, proveedor_id: str) -> Proveedor:
        proveedor = self.obtener(proveedor_id)
        proveedor.rechazar()
        self._repo.actualizar(proveedor)
        return proveedor
