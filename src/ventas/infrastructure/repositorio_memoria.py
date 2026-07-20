"""Repositorio en memoria (doble de prueba / Fake) del agregado Carrito.

Permite ejecutar la API y las pruebas de aceptación sin base de datos
(recomendado por el enunciado del Lab 7: usar dobles para componentes ausentes).
"""
from __future__ import annotations

from src.ventas.domain.modelo import Carrito
from src.ventas.domain.repositorio import ICarritoRepositorio


class CarritoRepositorioMemoria(ICarritoRepositorio):
    def __init__(self) -> None:
        self._datos: dict[str, Carrito] = {}

    def adicionar(self, carrito: Carrito) -> None:
        self._datos[carrito.id] = carrito

    def buscar(self, carrito_id: str) -> Carrito | None:
        return self._datos.get(carrito_id)

    def listar(self) -> list[Carrito]:
        return list(self._datos.values())
