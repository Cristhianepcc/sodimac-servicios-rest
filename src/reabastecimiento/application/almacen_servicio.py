"""Servicio de aplicación del Almacén (Reabastecimiento)."""
from __future__ import annotations

from src.reabastecimiento.domain.ubicacion import IUbicacionRepositorio, Ubicacion, UbicacionFabrica
from src.reabastecimiento.infrastructure import get_almacen_repositorio
from src.shared.errores import Conflicto, NoEncontrado


class AlmacenServicio:
    def __init__(self, repositorio: IUbicacionRepositorio | None = None) -> None:
        self._repo = repositorio or get_almacen_repositorio()

    def registrar_ubicacion(self, codigo: str, zona: str, sku: str, cantidad: int = 0) -> Ubicacion:
        if self._repo.buscar_por_codigo(codigo):
            raise Conflicto(f"Ya existe una ubicación con código '{codigo}'.")

        ubicacion = UbicacionFabrica.crear(codigo=codigo, zona=zona, sku=sku, cantidad=cantidad)
        self._repo.adicionar(ubicacion)
        return ubicacion

    def ubicar_mercaderia(self, codigo: str, zona: str, sku: str, cantidad: int = 0) -> Ubicacion:
        ubicacion_existente = self._repo.buscar_por_codigo(codigo)
        if ubicacion_existente is not None:
            ubicacion_existente.zona = zona.strip().upper()
            ubicacion_existente.sku = sku.strip().upper()
            ubicacion_existente.actualizar_cantidad(cantidad)
            self._repo.actualizar(ubicacion_existente)
            return ubicacion_existente

        ubicacion = UbicacionFabrica.crear(codigo=codigo, zona=zona, sku=sku, cantidad=cantidad)
        self._repo.adicionar(ubicacion)
        return ubicacion

    def consultar_ubicacion(self, sku: str) -> Ubicacion:
        ubicacion = self._repo.buscar_por_sku(sku)
        if ubicacion is None:
            raise NoEncontrado(f"No existe una ubicación para el SKU '{sku}'.")
        return ubicacion

    def actualizar_inventario(self, sku: str, stock: int) -> Ubicacion:
        ubicacion = self.consultar_ubicacion(sku)
        ubicacion.actualizar_cantidad(stock)
        self._repo.actualizar(ubicacion)
        return ubicacion
