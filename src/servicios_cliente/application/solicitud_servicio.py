"""Servicio de aplicación de Solicitudes de Servicio (casos de uso)."""
from __future__ import annotations

from src.servicios_cliente.domain.solicitud import SolicitudFabrica, SolicitudServicio
from src.servicios_cliente.infrastructure import get_solicitud_repositorio
from src.shared.errores import NoEncontrado


class SolicitudAppServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_solicitud_repositorio()

    def crear(self, cliente: str, tipo_servicio: str, direccion: str) -> SolicitudServicio:
        solicitud = SolicitudFabrica.crear(cliente, tipo_servicio, direccion)
        self._repo.adicionar(solicitud)
        return solicitud

    def obtener(self, solicitud_id: str) -> SolicitudServicio:
        solicitud = self._repo.buscar(solicitud_id)
        if solicitud is None:
            raise NoEncontrado(f"No existe la solicitud '{solicitud_id}'.")
        return solicitud

    def listar(self) -> list[SolicitudServicio]:
        return self._repo.listar()

    def programar(self, solicitud_id: str, tecnico: str, fecha: str) -> SolicitudServicio:
        solicitud = self.obtener(solicitud_id)
        solicitud.programar(tecnico, fecha)
        self._repo.adicionar(solicitud)
        return solicitud

    def ejecutar(self, solicitud_id: str, descripcion: str, foto_url: str) -> SolicitudServicio:
        solicitud = self.obtener(solicitud_id)
        solicitud.ejecutar(descripcion, foto_url)
        self._repo.adicionar(solicitud)
        return solicitud
