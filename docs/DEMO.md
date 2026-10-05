# Guion de demo — 6 a 7 minutos

| Tiempo | Qué mostrar |
|---|---|
| 0:00–0:45 | Caso RutaNova: encontrar rentabilidad por ciudad, dos fuentes y fórmula del margen. Aclarar fuentes simuladas. |
| 0:45–1:30 | Docker Compose con servicios activos, UI Airflow y arquitectura. No mostrar .env ni clave privada. |
| 1:30–3:30 | Ejecutar DAG; expandir grupos y mostrar sensor reschedule, dos ingestas, carga, dbt y reporte. Si tarda, grabar transición editada y aclarar el corte. |
| 3:30–4:15 | MinIO con JSON/CSV del run; Snowflake RAW con trazabilidad. |
| 4:15–5:15 | Modelos dbt, log de tests aprobados y mart con 15 entregados, S/2850 de ingresos, S/779 de margen. |
| 5:15–6:15 | PR público con CI verde y protección de main; explicar un test que detecta un costo faltante. |
| 6:15–6:45 | CSV final, glosario y decisiones: snapshot atómico, permisos y límites de simulación. |

Antes de grabar: haz un ensayo completo, prepara las pestañas y esconde archivos
privados. No presentes tests pendientes como aprobados. Un video de sólo código
no cumple: muestra el pipeline y los resultados ejecutados realmente.
