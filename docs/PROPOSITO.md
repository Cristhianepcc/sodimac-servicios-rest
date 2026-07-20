# Propósito

Implementar los **servicios web REST** de los **procesos de negocio de Sodimac**,
guiados por su especificación de comportamiento (**BDD**), aplicando prácticas de
**Clean Code**, **SOLID**, **DDD** y arquitectura en capas, sobre un framework MVC/REST
(Flask) y un ORM (SQLAlchemy + PostgreSQL).

Es la continuación de:
- **Práctica 4** — identificación de servicios candidatos a partir de los procesos.
- **Laboratorio 5** — modelado BPM (proceso de Reabastecimiento y de RSE).

## Alcance

Se exponen como API REST los 5 procesos de negocio principales de Sodimac:

1. Venta y Atención al Cliente (Omnicanal)
2. Cadena de Suministro / Reabastecimiento
3. Servicios al Cliente (Instalaciones y Proyectos)
4. Postventa y Experiencia del Cliente
5. Responsabilidad Social y Sostenibilidad (RSE)

Cada proceso es un **bounded context** independiente. Las operaciones de negocio se
prueban con **pruebas de aceptación (API)** en Postman siguiendo **Given–When–Then**.
