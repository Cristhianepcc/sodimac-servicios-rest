# Proceso de Postventa y Experiencia del Cliente

## Integrante

Erick Pérez

---

# 1. Descripción del Proceso

El proceso de Postventa tiene como objetivo gestionar reclamos de clientes relacionados con productos defectuosos, garantizando una atención estructurada hasta su resolución.

---
## Flujo del Proceso de Negocio

![Proceso de Postventa](/docs/diagramas/Diagrama_postventa.png)

**Figura 1.** Flujo BPMN del proceso de Postventa y Experiencia del Cliente.
-------------

# 2. Dominios, Áreas Funcionales y Servicios

| Dominio | Área Funcional | Servicio |
|----------|----------|----------|
| Postventa | Gestión de Reclamos | Registrar Reclamo |
| Postventa | Gestión de Garantías | Validar Garantía |
| Postventa | Evaluación Técnica | Registrar Evaluación |
| Postventa | Gestión de Soluciones | Registrar Solución |
| Postventa | Comunicación | Notificar Cliente |

---

# 3. Refinamiento de Servicios

| Servicio | Responsabilidad |
|----------|----------|
| Registrar Reclamo | Registrar una solicitud del cliente |
| Validar Garantía | Verificar requisitos de garantía |
| Evaluación Técnica | Analizar el producto |
| Registrar Solución | Definir reembolso, cambio o reparación |
| Notificar Cliente | Comunicar resultado del proceso |

---

# 4. Modelo de Dominio

La entidad principal del sistema es Reclamo.

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

---

# 5. Arquitectura

![Proceso de Postventa](/docs/diagramas/arquitectura_postventa.png)

La solución utiliza una arquitectura en capas compuesta por:

- Dominio
- Aplicación
- Infraestructura
- Presentación

La persistencia se realiza mediante PostgreSQL y SQLAlchemy.

---

# 6. Implementación de Servicios REST

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

---

# 7. Interfaz Web

Roles implementados:

## Cliente

- Registrar reclamos
- Consultar estado
- Visualizar respuesta

## Postventa

- Validar garantía
- Gestionar reclamos

## Técnico

- Registrar evaluación
- Registrar solución
- Enviar notificaciones

---

# 8. Flujo Implementado

Cliente
→ Reclamo
→ Garantía
→ Evaluación
→ Solución
→ Notificación
→ Cierre

---

# 9. Resultados

Se implementó exitosamente el proceso completo de Postventa mediante servicios REST e interfaz web basada en Flask, Jinja2 y Bootstrap.
