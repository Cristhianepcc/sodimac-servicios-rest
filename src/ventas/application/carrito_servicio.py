"""Servicio de aplicación del proceso `ventas` (casos de uso del carrito).

Coordina dominio + repositorio. No contiene reglas de negocio (esas viven en el
dominio) ni detalles de HTTP (esos viven en el controlador).
"""
from __future__ import annotations

from src.shared.errores import NoEncontrado
from src.ventas.domain.fabrica import CarritoFabrica
from src.ventas.domain.modelo import Carrito
from src.ventas.infrastructure import get_repositorio


class CarritoServicio:
    def __init__(self, repositorio=None) -> None:
        # Inyección de dependencia (permite pasar un doble en pruebas unitarias).
        self._repo = repositorio or get_repositorio()

    def crear(self, cliente: str, items: list[dict]) -> Carrito:
        carrito = CarritoFabrica.crear(cliente, items)
        self._repo.adicionar(carrito)
        return carrito

    def obtener(self, carrito_id: str) -> Carrito:
        carrito = self._repo.buscar(carrito_id)
        if carrito is None:
            raise NoEncontrado(f"No existe el carrito '{carrito_id}'.")
        return carrito

    def listar(self) -> list[Carrito]:
        return self._repo.listar()
