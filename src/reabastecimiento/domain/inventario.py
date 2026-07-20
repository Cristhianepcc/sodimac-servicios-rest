"""Dominio del proceso `reabastecimiento` — servicio de Inventario (referencia).

Entidad ProductoInventario + interfaz de repositorio + fábrica. Python puro.
Endpoints asociados (Práctica 4 §5.1): consultar stock, detectar bajo stock,
actualizar stock, generar alerta de reabastecimiento.
"""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.shared.errores import ErrorDominio


@dataclass
class ProductoInventario:
    sku: str
    nombre: str
    stock: int = 0
    stock_minimo: int = 0

    @property
    def bajo_stock(self) -> bool:
        return self.stock <= self.stock_minimo

    def actualizar_stock(self, nuevo_stock: int) -> None:
        if nuevo_stock < 0:
            raise ErrorDominio("El stock no puede ser negativo.")
        self.stock = nuevo_stock


class ProductoFabrica:
    @staticmethod
    def crear(sku: str, nombre: str, stock: int = 0, stock_minimo: int = 0) -> ProductoInventario:
        if not sku or not sku.strip():
            raise ErrorDominio("El SKU es obligatorio.")
        if not nombre or not nombre.strip():
            raise ErrorDominio("El nombre del producto es obligatorio.")
        if stock < 0 or stock_minimo < 0:
            raise ErrorDominio("Stock y stock mínimo no pueden ser negativos.")
        return ProductoInventario(sku.strip(), nombre.strip(), stock, stock_minimo)


class IProductoRepositorio(ABC):
    @abstractmethod
    def adicionar(self, producto: ProductoInventario) -> None: ...

    @abstractmethod
    def buscar(self, sku: str) -> ProductoInventario | None: ...

    @abstractmethod
    def actualizar(self, producto: ProductoInventario) -> None: ...

    @abstractmethod
    def listar_bajo_stock(self) -> list[ProductoInventario]: ...
