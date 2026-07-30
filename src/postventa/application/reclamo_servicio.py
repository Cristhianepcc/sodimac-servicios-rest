"""Servicio de aplicacion de Reclamos (casos de uso)."""
from __future__ import annotations

from datetime import datetime

from src.postventa.domain.reclamo import EstadoReclamo, Reclamo, ReclamoFabrica
from src.postventa.infrastructure import get_reclamo_repositorio
from src.shared.errores import ErrorDominio, NoEncontrado

NO_CAMBIO = object()


class ReclamoServicio:
    def __init__(self, repositorio=None) -> None:
        self._repo = repositorio or get_reclamo_repositorio()

    def crear(
        self,
        cliente: str,
        dni: str,
        email: str,
        telefono: str,
        producto: str,
        motivo: str,
    ) -> Reclamo:
        reclamo = ReclamoFabrica.crear(cliente, dni, email, telefono, producto, motivo)
        self._repo.adicionar(reclamo)
        return reclamo

    def obtener(self, reclamo_id: str) -> Reclamo:
        reclamo = self._repo.buscar(reclamo_id)
        if reclamo is None:
            raise NoEncontrado(f"No existe el reclamo '{reclamo_id}'.")
        return reclamo

    def listar(self) -> list[Reclamo]:
        return self._repo.listar()

    def listar_abiertos(self, page: int = 1, size: int = 20) -> dict:
        page, size = self._validar_paginacion(page, size)
        items, total = self._repo.listar_abiertos(page, size)
        return {"page": page, "size": size, "total": total, "items": items}

    def listar_para_evaluacion(self, page: int = 1, size: int = 20) -> dict:
        page, size = self._validar_paginacion(page, size)
        items, total = self._repo.listar_para_evaluacion(page, size)
        return {"page": page, "size": size, "total": total, "items": items}

    def listar_para_solucion(self, page: int = 1, size: int = 20) -> dict:
        page, size = self._validar_paginacion(page, size)
        items, total = self._repo.listar_para_solucion(page, size)
        return {"page": page, "size": size, "total": total, "items": items}

    def actualizar(
        self,
        reclamo_id: str,
        cliente=NO_CAMBIO,
        dni=NO_CAMBIO,
        email=NO_CAMBIO,
        telefono=NO_CAMBIO,
        producto=NO_CAMBIO,
        motivo=NO_CAMBIO,
        estado=NO_CAMBIO,
        cumple_garantia=NO_CAMBIO,
        motivo_validacion=NO_CAMBIO,
        diagnostico=NO_CAMBIO,
        procede_evaluacion=NO_CAMBIO,
        tipo_solucion=NO_CAMBIO,
        mensaje_cliente=NO_CAMBIO,
        fecha_cierre=NO_CAMBIO,
        fecha_notificacion=NO_CAMBIO,
    ) -> Reclamo:
        reclamo = self.obtener(reclamo_id)

        if cliente is not NO_CAMBIO:
            reclamo.cliente = cliente
        if dni is not NO_CAMBIO:
            reclamo.dni = dni
        if email is not NO_CAMBIO:
            reclamo.email = email
        if telefono is not NO_CAMBIO:
            reclamo.telefono = telefono
        if producto is not NO_CAMBIO:
            reclamo.producto = producto
        if motivo is not NO_CAMBIO:
            reclamo.motivo = motivo
        if estado is not NO_CAMBIO:
            reclamo.estado = estado if isinstance(estado, EstadoReclamo) else EstadoReclamo(estado)
        if cumple_garantia is not NO_CAMBIO:
            reclamo.cumple_garantia = cumple_garantia
        if motivo_validacion is not NO_CAMBIO:
            reclamo.motivo_validacion = motivo_validacion
        if diagnostico is not NO_CAMBIO:
            reclamo.diagnostico = diagnostico
        if procede_evaluacion is not NO_CAMBIO:
            reclamo.procede_evaluacion = procede_evaluacion
        if tipo_solucion is not NO_CAMBIO:
            reclamo.tipo_solucion = tipo_solucion
        if mensaje_cliente is not NO_CAMBIO:
            reclamo.mensaje_cliente = mensaje_cliente
        if fecha_cierre is not NO_CAMBIO:
            reclamo.fecha_cierre = fecha_cierre
        if fecha_notificacion is not NO_CAMBIO:
            reclamo.fecha_notificacion = fecha_notificacion

        self._repo.actualizar(reclamo)
        return reclamo

    def actualizar_garantia(
        self,
        reclamo_id: str,
        cumple_garantia: bool,
        motivo_validacion: str,
    ) -> Reclamo:
        if not isinstance(cumple_garantia, bool):
            raise ErrorDominio("El campo cumpleGarantia debe ser booleano.")
        if not motivo_validacion or not motivo_validacion.strip():
            raise ErrorDominio("El motivo de validacion es obligatorio.")

        estado = EstadoReclamo.EN_EVALUACION if cumple_garantia else EstadoReclamo.RECHAZADO
        return self.actualizar(
            reclamo_id=reclamo_id,
            cumple_garantia=cumple_garantia,
            motivo_validacion=motivo_validacion.strip(),
            estado=estado,
        )

    def actualizar_evaluacion(self, reclamo_id: str, diagnostico: str, procede: bool) -> Reclamo:
        if not diagnostico or not diagnostico.strip():
            raise ErrorDominio("El diagnostico es obligatorio.")
        if not isinstance(procede, bool):
            raise ErrorDominio("El campo procede debe ser booleano.")

        return self.actualizar(
            reclamo_id=reclamo_id,
            diagnostico=diagnostico.strip(),
            procede_evaluacion=procede,
        )

    def registrar_solucion(self, reclamo_id: str, tipo_solucion: str) -> Reclamo:
        tipo = (tipo_solucion or "").strip().upper()
        if tipo not in {"REEMBOLSO", "CAMBIO", "REPARACION"}:
            raise ErrorDominio("Tipo de solucion no permitido.")

        return self.actualizar(
            reclamo_id=reclamo_id,
            tipo_solucion=tipo,
            estado=EstadoReclamo.RESUELTO,
            fecha_cierre=datetime.utcnow(),
        )

    def registrar_notificacion(self, reclamo_id: str, mensaje_cliente: str) -> Reclamo:
        if not mensaje_cliente or not mensaje_cliente.strip():
            raise ErrorDominio("El mensajeCliente es obligatorio.")

        return self.actualizar(
            reclamo_id=reclamo_id,
            mensaje_cliente=mensaje_cliente.strip(),
            fecha_notificacion=datetime.utcnow(),
        )

    def _validar_paginacion(self, page: int, size: int) -> tuple[int, int]:
        try:
            page = int(page)
            size = int(size)
        except (TypeError, ValueError):
            raise ErrorDominio("Los parametros page y size deben ser numericos.")
        if page < 1:
            raise ErrorDominio("El parametro page debe ser mayor o igual a 1.")
        if size < 1 or size > 100:
            raise ErrorDominio("El parametro size debe estar entre 1 y 100.")
        return page, size
