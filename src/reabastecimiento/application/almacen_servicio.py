from __future__ import annotations

from src.reabastecimiento.domain.almacen import (
    MercaderiaUbicada,
    MercaderiaUbicadaFabrica,
    Ubicacion,
    UbicacionFabrica,
)
from src.reabastecimiento.infrastructure import get_almacen_repositorio
from src.shared.errores import Conflicto, NoEncontrado


class AlmacenServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_almacen_repositorio()

    def registrar_ubicacion(self, codigo: str, pasillo: str, estante: str, nivel: str) -> Ubicacion:
        existe = self._repo.buscar_ubicacion(codigo)
        if existe:
            raise Conflicto(f"Ya existe la ubicación '{codigo}'.")
        ubicacion = UbicacionFabrica.crear(codigo, pasillo, estante, nivel)
        self._repo.adicionar_ubicacion(ubicacion)
        return ubicacion

    def listar_ubicaciones(self) -> list[Ubicacion]:
        return self._repo.listar_ubicaciones()

    def consultar_ubicacion(self, codigo: str) -> Ubicacion:
        u = self._repo.buscar_ubicacion(codigo)
        if u is None:
            raise NoEncontrado(f"No existe la ubicación '{codigo}'.")
        return u

    def ubicar_mercaderia(self, sku: str, ubicacion_codigo: str, cantidad: int) -> MercaderiaUbicada:
        u = self._repo.buscar_ubicacion(ubicacion_codigo)
        if u is None:
            raise NoEncontrado(f"No existe la ubicación '{ubicacion_codigo}'.")
        mercaderia = MercaderiaUbicadaFabrica.crear(sku, ubicacion_codigo, cantidad)
        self._repo.ubicar_mercaderia(mercaderia)
        return mercaderia

    def consultar_por_sku(self, sku: str) -> list[MercaderiaUbicada]:
        return self._repo.buscar_por_sku(sku)

    def actualizar_inventario_cd(self, sku: str, ubicacion_codigo: str, cantidad: int) -> dict:
        self._repo.actualizar_inventario_ubicacion(sku, ubicacion_codigo, cantidad)
        return {"sku": sku, "ubicacionCodigo": ubicacion_codigo, "cantidad": cantidad}
