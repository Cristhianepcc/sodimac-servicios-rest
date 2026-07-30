"""Dominio del servicio de Almacén (Reabastecimiento)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.shared.errores import ErrorDominio


@dataclass
class Ubicacion:
    codigo: str
    zona: str
    sku: str
    cantidad: int = 0

    def actualizar_cantidad(self, nueva_cantidad: int) -> None:
        if nueva_cantidad < 0:
            raise ErrorDominio("La cantidad no puede ser negativa.")
        self.cantidad = nueva_cantidad


class UbicacionFabrica:
    @staticmethod
    def crear(codigo: str, zona: str, sku: str, cantidad: int = 0) -> Ubicacion:
        if not codigo or not codigo.strip():
            raise ErrorDominio("El código de ubicación es obligatorio.")
        if not zona or not zona.strip():
            raise ErrorDominio("La zona es obligatoria.")
        if not sku or not sku.strip():
            raise ErrorDominio("El SKU es obligatorio.")
        if cantidad < 0:
            raise ErrorDominio("La cantidad no puede ser negativa.")

        return Ubicacion(
            codigo=codigo.strip().upper(),
            zona=zona.strip().upper(),
            sku=sku.strip().upper(),
            cantidad=int(cantidad),
        )


class IUbicacionRepositorio(ABC):
    @abstractmethod
    def adicionar(self, ubicacion: Ubicacion) -> None: ...

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> Ubicacion | None: ...

    @abstractmethod
    def buscar_por_sku(self, sku: str) -> Ubicacion | None: ...

    @abstractmethod
    def actualizar(self, ubicacion: Ubicacion) -> None: ...
