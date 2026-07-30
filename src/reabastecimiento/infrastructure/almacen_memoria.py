from __future__ import annotations

from src.reabastecimiento.domain.almacen import IAlmacenRepositorio, MercaderiaUbicada, Ubicacion


class AlmacenRepositorioMemoria(IAlmacenRepositorio):
    def __init__(self) -> None:
        self._ubicaciones: dict[str, Ubicacion] = {}
        self._mercaderia: dict[str, MercaderiaUbicada] = {}

    def adicionar_ubicacion(self, ubicacion: Ubicacion) -> None:
        self._ubicaciones[ubicacion.codigo] = ubicacion

    def buscar_ubicacion(self, codigo: str) -> Ubicacion | None:
        return self._ubicaciones.get(codigo)

    def listar_ubicaciones(self) -> list[Ubicacion]:
        return list(self._ubicaciones.values())

    def ubicar_mercaderia(self, mercaderia: MercaderiaUbicada) -> None:
        self._mercaderia[mercaderia.id] = mercaderia

    def buscar_por_sku(self, sku: str) -> list[MercaderiaUbicada]:
        return [m for m in self._mercaderia.values() if m.sku == sku]

    def actualizar_inventario_ubicacion(self, sku: str, ubicacion_codigo: str, cantidad: int) -> None:
        for m in self._mercaderia.values():
            if m.sku == sku and m.ubicacion_codigo == ubicacion_codigo:
                m.cantidad = cantidad
                return
