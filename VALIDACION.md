# Validación del paquete

Fecha: 2026-10-03. Se documentan verificaciones reales; no se simula una ejecución cloud.

| Verificación | Resultado |
|---|---|
| pytest negocio | 14 pruebas aprobadas. |
| pytest con Airflow 2.10.5 instalado en entorno aislado | 15 pruebas aprobadas, incluida importación del DAG y contrato de dependencias. |
| dbt-core 1.9.4 + dbt-snowflake 1.9.2 | Instalación exitosa; dbt parse exitoso, 4 modelos y 20 tests reconocidos. |
| API HTTP local + lectura del CSV | Respuesta HTTP y reconciliación: 18 pedidos, 15 costos y 15 entregados. |
| Baseline de negocio | Ingresos S/2850.00 y margen S/779.00 verificados por pytest. |
| Bootstrap Airflow | Migración del metastore y creación real de usuario/Connections aprobadas usando configuración de prueba local. |
| Python y YAML | Archivos Python compilables; estructura YAML validada. |
| PDF arquitectura | 2 páginas renderizadas y revisadas visualmente. |

Los entornos locales de verificación usan Python 3.12. La imagen Docker fija Python
3.11; CI construye esa imagen y ejecuta las mismas pruebas para validar ese entorno.

Pendiente de ejecutar con recursos del alumno:

1. Docker Compose: este entorno no tiene Docker instalado; no se realizó build ni up.
2. Ingesta real en MinIO y carga Snowflake: requieren Docker y tu cuenta cloud.
3. dbt build/test contra Snowflake: parse valida sintaxis y linaje, no los resultados SQL.
4. Publicación GitHub, PR verde y Branch Protection: el workflow está incluido, pero no ejecutado en GitHub.
5. Video: debe grabarse mostrando una ejecución auténtica, completar sus URLs y regenerar el PDF.

No se incluyen reportes fingidos. reports/city_profitability.csv se crea sólo tras
una ejecución exitosa. No se ha creado historial Git artificial ni introducido
credenciales reales en el paquete.
