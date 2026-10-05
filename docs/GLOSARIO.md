# Glosario y gobierno

| Término | Definición |
|---|---|
| Pedido entregado | Pedido con status=delivered; participa en el mart. |
| Pedido cancelado | Se conserva en staging y se excluye de los indicadores. |
| Costo de reparto | Costo del transportista por pedido; no incluye costo del producto. |
| Margen de contribución | Ingreso menos costo del producto menos costo de reparto; puede ser negativo. No es utilidad neta. |
| Margen porcentual | 100 × suma de márgenes / suma de ingresos; NULL cuando el ingreso es cero. |

Owner técnico: rutanova_data_team. Owner de negocio propuesto: Operaciones.
Grano: ORDER_ID en staging/detalle; ORDER_DATE + CITY en el mart.
Clasificación: datos sintéticos de uso educativo, sin información personal.
Linaje: API/CSV → objetos snapshots/<run hash> → RAW → stg → int → mart.
SOURCE_KEY, RUN_ID e INGESTED_AT vinculan el warehouse con el objeto crudo.
SLA propuesto: disponible antes de 08:00 Lima; no está contratado ni medido en producción.
MinIO tiene versionado. Retención propuesta: 30 días de crudos, con aprobación del owner.
No se activa borrado automático en este laboratorio para preservar la evidencia.
OpenMetadata y Cosmos son mejoras futuras; no están instalados en esta versión.
