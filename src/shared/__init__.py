"""Kernel compartido (shared kernel) entre todos los bounded contexts.

Contiene infraestructura transversal: conexión a BD, errores de dominio,
utilidades HTTP y de serialización. NO contiene lógica de negocio de ningún
proceso; cada proceso vive en su propio paquete (`src/<proceso>`).
"""
