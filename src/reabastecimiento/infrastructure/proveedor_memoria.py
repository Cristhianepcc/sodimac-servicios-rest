"""Repositorio en memoria (Fake) del servicio de Proveedores."""
from __future__ import annotations

from src.reabastecimiento.domain.proveedor import IProveedorRepositorio, Proveedor


class ProveedorRepositorioMemoria(IProveedorRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, Proveedor] = {}

    def adicionar(self, proveedor: Proveedor) -> None:
        self._datos[proveedor.id] = proveedor

    def buscar(self, proveedor_id: str) -> Proveedor | None:
        return self._datos.get(proveedor_id)

    def listar(self) -> list[Proveedor]:
        return list(self._datos.values())

    def actualizar(self, proveedor: Proveedor) -> None:
        self._datos[proveedor.id] = proveedor
