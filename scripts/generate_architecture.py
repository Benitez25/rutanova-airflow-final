"""Regenerate the required two-page PDF after adding real repo/video links.
Local use: pip install reportlab; python scripts/generate_architecture.py
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
ROOT = Path(__file__).resolve().parents[1]
BLUE = colors.HexColor('#123B53')
TEAL = colors.HexColor('#007C83')
GRAY = colors.HexColor('#53616A')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom', fontName='Helvetica-Bold', fontSize=23, leading=27, textColor=BLUE, spaceAfter=10))
styles.add(ParagraphStyle(name='SubCustom', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=TEAL, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name='TextCustom', fontName='Helvetica', fontSize=9, leading=12, textColor=BLUE, spaceAfter=6))
styles.add(ParagraphStyle(name='SmallCustom', fontName='Helvetica', fontSize=8, leading=10, textColor=GRAY, spaceAfter=4))

def p(text, style='TextCustom'):
    return Paragraph(text, styles[style])

def table(rows, widths, header=True):
    converted = [[p(str(cell),'SmallCustom') for cell in row] for row in rows]
    t = Table(converted, colWidths=widths, hAlign='LEFT')
    ts = [('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),1,TEAL),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E5F1F2'))]
    for i in range(1,len(rows)):
        if i%2==0: ts.append(('BACKGROUND',(0,i),(-1,i),colors.HexColor('#F5F7F8')))
    t.setStyle(TableStyle(ts))
    return t

class ArchitectureDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 511
        self.height = 120
    def draw(self):
        c = self.canv
        def box(x,y,w,label):
            c.setFillColor(colors.HexColor('#E5F1F2'));c.setStrokeColor(TEAL)
            c.roundRect(x,y,w,26,4,stroke=1,fill=1)
            c.setFillColor(BLUE);c.setFont('Helvetica-Bold',8)
            c.drawCentredString(x+w/2,y+10,label)
        def arrow(x1,y1,x2,y2):
            c.setStrokeColor(TEAL);c.setFillColor(TEAL);c.line(x1,y1,x2,y2)
            path=c.beginPath()
            if y1==y2:
                path.moveTo(x2,y2);path.lineTo(x2-5,y2+3);path.lineTo(x2-5,y2-3)
            else:
                path.moveTo(x2,y2);path.lineTo(x2-3,y2+5);path.lineTo(x2+3,y2+5)
            path.close();c.drawPath(path,fill=1,stroke=0)
        box(10,90,130,'API de pedidos')
        box(175,90,130,'CSV de reparto')
        box(10,47,295,'Airflow + MinIO (crudos por run)')
        arrow(75,90,75,73);arrow(240,90,240,73)
        box(10,4,150,'Snowflake RAW')
        box(193,4,132,'dbt: stg -> int')
        box(358,4,143,'Mart + reporte CSV')
        arrow(85,47,85,30);arrow(160,17,193,17);arrow(325,17,358,17)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(TEAL);canvas.line(42,38,A4[0]-42,38)
    canvas.setFont('Helvetica',8);canvas.setFillColor(GRAY)
    canvas.drawString(42,25,'Apache Airflow | Proyecto final integrador | RutaNova')
    canvas.drawRightString(A4[0]-42,25,f'{doc.page} / 2')
    canvas.restoreState()

def main():
    meta = json.loads((ROOT/'docs/arquitectura.json').read_text())
    path = ROOT/'docs/Arquitectura_RutaNova.pdf'
    story = [p('RutaNova','TitleCustom'),p('Rentabilidad de pedidos y costos de reparto','SubCustom'),
             p('Documento de arquitectura - Proyecto final de Apache Airflow','SmallCustom'),
             p('Equipo: '+escape(meta['integrantes']),'SmallCustom')]
    story += [p('1. Caso de negocio y resultado','SubCustom'),
              p('Una operación comercial necesita identificar qué ciudades generan mayor margen tras pagar el producto y el reparto. El pipeline integra pedidos de una API HTTP y costos del transportista en CSV. Excluye cancelaciones y produce indicadores por fecha y ciudad.'),
              p('<b>Fuentes simuladas explícitamente:</b> API local y CSV con 18 pedidos, 15 entregados y 3 cancelados. La simulación permite reproducir la demo sin depender de una API pública. El warehouse Snowflake sí requiere una cuenta real.'),
              p('<b>Fórmula:</b> margen = ingreso - costo del producto - costo de reparto. Porcentaje = 100 × suma de márgenes / suma de ingresos; NULL si el ingreso es cero. Se permiten márgenes negativos. No representa utilidad neta.'),
              p('2. Arquitectura y linaje','SubCustom'), ArchitectureDiagram(), Spacer(1,5)]
    story.append(table([
        ['Etapa','Componente y movimiento de datos'],
        ['1. Orquestación','Airflow en Docker, LocalExecutor + Postgres. DAG diario 07:00 Lima; catchup=False; una ejecución activa.'],
        ['2. Fuentes','HTTP API /orders y CSV delivery_costs.csv. Sensor reschedule espera archivo no vacío. Ingestas con validaciones.'],
        ['3. Respaldo crudo','MinIO: bucket rutanova-raw, objetos por hash del run_id y versionado. Ambas fuentes pasan por almacenamiento intermedio.'],
        ['4. Warehouse','Snowflake RUTANOVA.RAW: snapshot completo cargado en transacción. SOURCE_KEY y RUN_ID vinculan cada carga con MinIO.'],
        ['5. Transformación','dbt: stg_orders + stg_delivery_costs → int_order_profitability → mart_city_profitability. Operador Airflow ejecuta dbt build.'],
        ['6. Consumo','Snowflake ANALYTICS.MART_CITY_PROFITABILITY y reporte CSV local; resultados disponibles sólo después de aprobar tests.']
    ],[103,408]))
    story += [Spacer(1,8),p('<b>Baseline esperado del fixture:</b> 15 entregados, S/ 2,850.00 de ingresos y S/ 779.00 de margen. El snapshot es fijo y sus fechas no cambian con el schedule.','SmallCustom'),PageBreak(),
              p('Diseño, calidad y entrega','TitleCustom'),
              p('3. Decisiones técnicas','SubCustom')]
    story.append(table([
        ['Decisión','Justificación'],
        ['Snapshot atómico','Fuentes pequeñas y completas. DELETE + INSERT dentro de BEGIN/COMMIT evita duplicados al reintentar y revierte fallos. DDL fuera de la transacción. No es CDC.'],
        ['MinIO local','Reproduce object storage sin cuenta adicional; permite auditar el crudo antes de cargar Snowflake. Usuario de ingesta restringido al bucket.'],
        ['Snowflake','Mantiene la tecnología recomendada por el curso. Warehouse XSMALL, AUTO_SUSPEND=60 y rol con acceso acotado a RAW/ANALYTICS.'],
        ['dbt desde operador','PythonOperator ejecuta dbt build con subprocess y falla por código de salida. Es la alternativa mínima permitida por sección 5.3; no se usa Cosmos.'],
        ['Secretos y autenticación','Airflow Connections cifradas; profiles.yml con env_var. Clave privada local fuera de Git e imagen. Autenticación Snowflake por par de claves.']
    ],[103,408]))
    story += [p('4. Pruebas, operación y gobierno','SubCustom'),
              p('<b>pytest:</b> importes inválidos, duplicados, fechas incorrectas, costos faltantes/huérfanos, margen negativo, ingreso cero y baseline de negocio. Test adicional de contrato del DAG con Airflow real.'),
              p('<b>dbt:</b> unique, not_null, relationships, accepted_values; SQL para importes no negativos, grano fecha/ciudad y reconciliaciones. Los tests de datos se verifican contra Snowflake durante la demo.'),
              p('<b>CI:</b> GitHub Actions en PR y main; pruebas de negocio, construcción Docker, importación DAG y parse dbt. Protección de main debe exigir checks verdes. No hay CD automático.'),
              p('<b>Operación:</b> retries/backoff, timeout del sensor y serialización de runs. Owner técnico: rutanova_data_team. Granos: pedido y fecha/ciudad. Glosario y matriz de cumplimiento incluidos. No se instala OpenMetadata.'),
              p('5. Enlaces de entrega y límites','SubCustom'),
              p('Repositorio público: '+escape(meta['repositorio']),'SmallCustom'),
              p('Video demo (5-8 min): '+escape(meta['video']),'SmallCustom'),
              p('Completar ambos enlaces con evidencia real antes de entregar. Docker local es un laboratorio sin alta disponibilidad; para producción faltan alertas, gestión centralizada de secretos, retención automática y diseño incremental. No se fabrica historial Git ni resultados de ejecución.','SmallCustom')]
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=40,bottomMargin=49)
    doc.title='RutaNova - Arquitectura del pipeline'
    doc.author='Equipo RutaNova'
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(path)
if __name__ == '__main__':
    main()
