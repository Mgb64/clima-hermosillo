from pathlib import Path
import textwrap

W,H=960,540
BG=(0.035,0.065,0.12); FG=(0.92,0.95,0.98); MUT=(0.61,0.70,0.79); ACC=(0.19,0.84,0.72); PANEL=(0.065,0.11,0.18)
slides=[]
def color(c): return ' '.join(str(x) for x in c)
def rect(x,y,w,h,c): return f'{color(c)} rg {x} {H-y-h} {w} {h} re f\n'
def esc(s): return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
def txt(x,y,s,size=18,c=FG,bold=False):
    return f'BT /{"F2" if bold else "F1"} {size} Tf {color(c)} rg 1 0 0 1 {x} {H-y-size} Tm ({esc(s)}) Tj ET\n'
def base(k,title,subtitle):
    return rect(0,0,W,H,BG)+rect(44,43,36,4,ACC)+txt(44,62,k.upper(),11,ACC,True)+txt(44,88,title,32,FG,True)+txt(44,138,subtitle,15,MUT)
def footer(s,n):
    return s+rect(44,495,872,1,PANEL)+txt(44,508,'CLIMA HERMOSILLO  /  Arquitectura y funcionamiento',10,MUT)+txt(866,506,f'{n:02d} / 12',11,ACC)
def cards(k,title,sub,items,note):
    s=base(k,title,sub)
    width=(872-20*(len(items)-1))/len(items)
    for i,(head,body) in enumerate(items):
        x=44+i*(width+20)
        s+=rect(x,193,width,224,PANEL)+txt(x+20,211,head,19,ACC,True)
        y=253
        for paragraph in body:
            for line in textwrap.wrap(paragraph,width=int((width-40)/8.1)):
                s+=txt(x+20,y,line,16);y+=23
            y+=10
    s+=txt(44,450,note,14,MUT)
    slides.append(s)

s=rect(0,0,W,H,BG)+rect(650,0,310,H,PANEL)+rect(52,67,55,5,ACC)
s+=txt(52,95,'PROYECTO DE DATOS',13,ACC,True)+txt(52,159,'Clima',64,FG,True)+txt(52,231,'Hermosillo',64,FG,True)
s+=txt(55,330,'De una API meteorológica a un dashboard interactivo',19,MUT)
s+=txt(55,382,'Python  /  PostgreSQL  /  Streamlit  /  Docker',16,ACC)
for i,(a,b) in enumerate([('01','Obtener'),('02','Almacenar'),('03','Visualizar')]):
    s+=txt(694,146+i*95,a,14,ACC,True)+txt(694,171+i*95,b,25,FG,True)
slides.append(s)
cards('01 / Propósito','¿Qué resuelve el proyecto?','Un flujo completo de datos meteorológicos para una ubicación fija.',[
('Consultar',['Condiciones actuales estimadas para Hermosillo.','Temperatura, humedad, sensación térmica y viento.']),
('Conservar',['Historial local de capturas.','Versiones sucesivas de los pronósticos horarios.']),
('Analizar',['Temperatura y lluvia esperadas.','Diferencias frente al pronóstico de un día antes.'])], 'Alcance: consume modelos externos; no entrena un modelo propio.')
s=base('02 / Arquitectura','Tres servicios, un flujo de datos','Cada componente tiene una responsabilidad independiente.')
for i,(title,desc) in enumerate([('Open-Meteo','API externa'),('collector','Extracción en Python'),('PostgreSQL','Almacenamiento'),('Streamlit','Visualización')]):
    x=44+i*224
    s+=rect(x,220,200,126,PANEL)+txt(x+15,244,title,22,ACC,True)+txt(x+15,286,desc,14)
    if i<3:s+=txt(x+204,257,'>',20,ACC,True)
s+=txt(44,381,'HTTP + JSON',16,MUT)+txt(268,381,'Inserciones SQL',16,MUT)+txt(492,381,'Consultas SQL',16,MUT)+txt(716,381,'Navegador :8501',16,MUT)
s+=txt(44,450,'Docker Compose coordina collector, db y dashboard dentro de una red interna.',15,MUT)
slides.append(s)
cards('03 / Ingesta','Cómo funciona el recolector','collector/worker.py | Ubicación: 29.0729, -110.9559 | America/Hermosillo',[
('1. Consultar',['Obtiene condiciones actuales y pronóstico de tres días.','Consulta también predicciones con un día de anticipación.']),
('2. Transformar',['Convierte fechas y arreglos JSON en filas.','Alinea por hora los datos para la comparación.']),
('3. Guardar',['Inserta en tres tablas dentro de una transacción.','Espera 600 segundos al finalizar y vuelve a comenzar.'])], 'Requests: HTTP y JSON. Psycopg: conexión y escritura en PostgreSQL.')
cards('04 / Persistencia','Tres tablas con funciones distintas','schema.sql | Identificadores, índices temporales y conservación de versiones.',[
('observations',['Instantánea de condiciones actuales.','fetched_at: captura. observed_at: hora del dato.']),
('forecasts',['Una fila por hora de cada versión descargada.','fetched_at + forecast_for identifica una fila única.']),
('comparisons',['Valores actuales y predicciones anteriores.','valid_hour permite agrupar las comparaciones por hora.'])], 'Las tablas no tienen claves foráneas; se consultan como series temporales.')
cards('05 / Análisis','¿Qué significa la desviación?','La interfaz calcula: valor actual estimado menos predicción anterior.',[
('Ejemplo',['Actual estimado: 34 °C.','Pronóstico anterior: 32 °C.','Desviación: +2 °C.']),
('Interpretación',['Positiva: mayor que lo previsto.','Negativa: menor que lo previsto.','Cero: ambos coinciden.']),
('Alcance',['Compara estimaciones de modelos.','La lluvia se compara en intervalos horarios.','No mide error contra una estación.'])], 'Para evaluar precisión real se necesitarían mediciones independientes de referencia.')
cards('06 / Interfaz','Un dashboard que consulta la base','app/dashboard.py | Streamlit + Pandas + Plotly + SQLAlchemy.',[
('Vista',['Métricas actuales.','Pronóstico de temperatura, lluvia y probabilidad.','Historial y desviaciones.']),
('Consultas',['Última observación.','Última versión de pronóstico.','Hasta 300 capturas históricas y comparaciones.']),
('Actualización',['Fragmento cada 60 segundos con sesión activa.','Caché de resultados: 50 segundos.','Nuevas capturas: ~10 minutos.'])], 'La interfaz puede funcionar con los datos almacenados aunque el recolector falle.')
cards('07 / Contenedores','Configuración de Docker Compose','compose.yaml define imágenes, variables, red, volumen y dependencias.',[
('db',['postgres:16-alpine.','Volumen postgres_data para persistencia.','schema.sql inicializa una base vacía.']),
('collector',['Imagen python:3.12-slim.','DATABASE_URL conecta a db:5432.','UPDATE_SECONDS = 600.']),
('dashboard',['Imagen python:3.12-slim.','Publica el puerto 8501.','Streamlit escucha en 0.0.0.0.'])], 'Las dependencias Python tienen versiones fijadas en los archivos requirements.txt.')
cards('08 / Operación','Arranque, red y recuperación','Los servicios internos utilizan el nombre db para encontrar PostgreSQL.',[
('Arranque',['pg_isready comprueba la disponibilidad de la base.','collector y dashboard esperan ese estado saludable.']),
('Fallos',['HTTP con timeout de 30 segundos.','Excepciones registradas en logs y reintento posterior.','Escrituras con rollback si fallan.']),
('Persistencia',['down conserva el volumen.','down -v elimina los datos.','collector y dashboard: restart unless-stopped.'])], 'Credenciales de demostración en Compose: deben gestionarse como secretos en producción.')
cards('09 / Evaluación','Fortalezas y límites del proyecto','Aspectos que conviene explicar con precisión durante la exposición.',[
('Fortalezas',['Separación de funciones.','Historial y versiones persistentes.','Consultas SQL parametrizadas.','Despliegue con Compose.']),
('Límites',['Tres días no garantizan 72 horas futuras.','Temperatura actual y hora redondeada no coinciden siempre.','Sin política de limpieza.']),
('Mejoras',['Alinear instantes e intervalos.','Separar fallos de las dos APIs.','Gestionar secretos y migraciones.','Agregar monitoreo y retención.'])], 'Si falla la API de predicciones anteriores, el ciclo actual tampoco almacena observaciones.')
s=base('10 / Demostración','Cómo presentar el sistema en vivo','Ejecutar desde la carpeta clima-hermosillo. Iniciarlo con anticipación.')
steps=[('1  Iniciar','docker compose up --build -d'),('2  Revisar servicios','docker compose ps'),('3  Ver actividad','docker compose logs --tail=30 collector'),('4  Abrir la interfaz','http://localhost:8501')]
for i,(label,command) in enumerate(steps):
    y=192+i*65
    s+=txt(44,y,label,16,ACC,True)+rect(280,y-3,636,48,PANEL)+txt(299,y+8,command,17)
s+=txt(44,463,'Mostrar: métricas > pronóstico > desviaciones > historial almacenado.',15,MUT)
slides.append(s)
cards('11 / Cierre','De datos externos a información útil','El aporte central es integrar y conservar un flujo de datos reproducible.',[
('Obtener',['Python automatiza la consulta de una fuente meteorológica.','No hay entrenamiento de un modelo propio.']),
('Conservar',['PostgreSQL guarda capturas y versiones de pronósticos.','Permite analizar su evolución en el tiempo.']),
('Comunicar',['Streamlit convierte registros en métricas y gráficas.','Docker Compose reúne los componentes.'])], 'Base del análisis: código local. Compose y sintaxis validados; ejecución no verificada.')

objects=[]
def obj(data):
    objects.append(data if isinstance(data,bytes) else data.encode('cp1252'));return len(objects)
root=obj('');pages=obj('')
f1=obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>')
f2=obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>')
ids=[]
for n,s in enumerate(slides,1):
    stream=footer(s,n).encode('cp1252')
    content=obj(b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'endstream')
    ids.append(obj(f'<< /Type /Page /Parent {pages} 0 R /MediaBox [0 0 {W} {H}] /Resources << /Font << /F1 {f1} 0 R /F2 {f2} 0 R >> >> /Contents {content} 0 R >>'))
objects[root-1]=f'<< /Type /Catalog /Pages {pages} 0 R >>'.encode()
objects[pages-1]=f'<< /Type /Pages /Kids [{" ".join(f"{i} 0 R" for i in ids)}] /Count {len(ids)} >>'.encode()
info=obj('<< /Title (Clima Hermosillo - Arquitectura y funcionamiento) /Subject (Presentación del proyecto) /Creator (Python) >>')
data=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
for i,o in enumerate(objects,1):
    offsets.append(len(data));data+=f'{i} 0 obj\n'.encode()+o+b'\nendobj\n'
xref=len(data);data+=f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode()
for offset in offsets[1:]: data+=f'{offset:010d} 00000 n \n'.encode()
data+=f'trailer\n<< /Size {len(objects)+1} /Root {root} 0 R /Info {info} 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
out=Path(__file__).parent/'Presentacion_Clima_Hermosillo.pdf';out.write_bytes(data)
print(f'{out.resolve()} | {len(slides)} diapositivas | {len(data)} bytes')
