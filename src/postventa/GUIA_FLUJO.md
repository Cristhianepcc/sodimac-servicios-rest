# Postventa y Experiencia del Cliente

**Responsable:** Erick Pérez

## Descripción

El módulo de Postventa permite gestionar el ciclo completo de atención de reclamos de clientes.

El flujo implementado es:

Registrar Reclamo
→ Validar Garantía
→ Evaluar Producto
→ Determinar Solución
→ Notificar Cliente
→ Cerrar Caso

Para simplificar la persistencia se decidió centralizar toda la información del proceso en una única entidad denominada `Reclamo`.

---

## Dominio

### Entidad Principal: Reclamo

Campos:

- id
- cliente
- dni
- email
- telefono
- producto
- motivo
- estado
- cumpleGarantia
- motivoValidacion
- diagnostico
- procedeEvaluacion
- tipoSolucion
- mensajeCliente
- fechaCierre
- fechaNotificacion

Estados posibles:

- REGISTRADO
- EN_EVALUACION
- RESUELTO
- RECHAZADO

---

## Arquitectura

El módulo sigue una arquitectura en capas:

- Dominio
- Aplicación
- Infraestructura
- Presentación

Estructura:

src/postventa/

├── domain/
├── application/
├── infrastructure/
└── presentation/

---

## Flujo del Proceso

1. Cliente registra un reclamo.
2. Postventa valida la garantía.
3. Técnico registra la evaluación.
4. Técnico define la solución.
5. Se envía una notificación al cliente.
6. El caso se marca como resuelto.

---

## Servicios REST
| Método | Endpoint | Descripción |
|----------|----------|----------|
| POST | /api/reclamos | Registrar reclamo |
| GET | /api/reclamos | Listar reclamos |
| GET | /api/reclamos/{id} | Consultar reclamo |
| PUT | /api/reclamos/{id} | Actualizar reclamo |
| PATCH | /api/reclamos/{id}/garantia | Validar garantía |
| GET | /api/evaluaciones | Reclamos pendientes de evaluación |
| PATCH | /api/reclamos/{id}/evaluacion | Registrar evaluación |
| GET | /api/soluciones | Reclamos pendientes de solución |
| PATCH | /api/reclamos/{id}/solucion | Registrar solución |
| POST | /api/reclamos/{id}/notificacion | Notificar cliente |