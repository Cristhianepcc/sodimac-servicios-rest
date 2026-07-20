"""Interfaz del repositorio del agregado Carrito (puerto de DDD).

El dominio define la abstracción; la infraestructura provee la implementación
(en memoria o SQLAlchemy). Inversión de dependencias (la D de SOLID).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .modelo import Carrito


class ICarritoRepositorio(ABC):
    @abstractmethod
    def adicionar(self, carrito: Carrito) -> None: ...

    @abstractmethod
    def buscar(self, carrito_id: str) -> Carrito | None: ...

    @abstractmethod
    def listar(self) -> list[Carrito]: ...
