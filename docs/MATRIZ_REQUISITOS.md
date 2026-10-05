# Matriz de cumplimiento y evidencia

| Requisito | Implementación / evidencia |
|---|---|
| Caso distinto de TiendaNova | RutaNova, rentabilidad logística. |
| Schedule real y catchup=False | DAG diario 07:00 Lima. |
| TaskGroup y sensor | ingestion, warehouse, transformation; PythonSensor reschedule. |
| Retries y errores explícitos | 2 reintentos Airflow con backoff; HTTP GET con backoff; validaciones bloqueantes. |
| Secrets en Connections/Variables | bootstrap crea 3 Connections cifradas con Fernet; .env y claves ignorados. |
| Dos tipos de fuente | HTTP API simulada + CSV del transportista. |
| Object storage antes del warehouse | Ambas fuentes archivadas en MinIO; carga lee exclusivamente esos objetos. |
| Snowflake | RAW y ANALYTICS, rol acotado y warehouse XSMALL con autosuspend. |
| 3 modelos encadenados | stg_orders → int_order_profitability → mart_city_profitability; cuarto stg_delivery_costs. |
| dbt tests | unique/not_null/relationships/accepted_values y 4 tests SQL de negocio. |
| dbt orquestado | PythonOperator ejecuta dbt build con subprocess y código de salida verificado. Opción mínima permitida en sección 5.3; sin Cosmos. |
| profiles env_var | dbt/profiles.yml; secretos no quedan en el DAG ni en XCom. |
| pytest de negocio | tests/test_business.py. |
| CI en cada PR | .github/workflows/ci.yml, negocio + build Docker + DAG + parse dbt. |
| Branch Protection | Activar en GitHub; no puede demostrarse sólo con archivos. |
| Historial real y PR verde | Construir con avances/revisiones reales; no fabricar fechas ni commits. |
| README, doc_md, owner, glosario | README, DAG, docs/GLOSARIO.md. |
| Consumo final | mart en Snowflake y reports/city_profitability.csv tras ejecución. |
| PDF arquitectura y video | PDF incluido; completar URLs reales y grabar siguiendo docs/DEMO.md. |

Pendientes de ejecución externa: construir Docker, ejecutar contra Snowflake, obtener
run verde y dbt tests reales, publicar GitHub, activar protección y grabar video.
La validación local realizada por el autor del paquete se documenta en VALIDACION.md.
