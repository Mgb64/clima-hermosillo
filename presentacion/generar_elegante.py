from pathlib import Path
import textwrap
import generar_pdf as p

INK=(.08,.16,.22); PAPER=(.97,.96,.93); MUT=(.39,.44,.46); ACC=(.73,.30,.20); LINE=(.83,.84,.81); WHITE=(1,1,1); TEAL=(.12,.40,.42)
R=p.rect; T=p.txt
slides=[]
def line(x,y,w,c=LINE): return R(x,y,w,1,c)
def text(x,y,s,size=18,c=INK,b=False):return T(x,y,s,size,c,b)
def para(x,y,s,width=48,size=18,c=MUT,leading=26):
    out=''
    for l in textwrap.wrap(s,width):out+=text(x,y,l,size,c);y+=leading
    return out

def start(ch,title,sub='',dark=False):
    bg=INK if dark else PAPER; fg=PAPER if dark else INK
    s=R(0,0,960,540,bg)+text(48,29,'CLIMA / HERMOSILLO',11,ACC,True)+text(690,29,ch.upper(),10,fg)
    s+=line(48,56,864,TEAL if dark else LINE)+text(48,88,title,34,fg,True)
    if sub:s+=text(50,141,sub,15,(.70,.76,.77) if dark else MUT)
    return s

def add(s,dark=False):
    n=len(slides)+1;c=(.65,.72,.73) if dark else MUT
    s+=line(48,495,864,TEAL if dark else LINE)+text(48,510,'INTRODUCCIÓN A CIENCIA DE DATOS  /  ANÁLISIS DEL PROYECTO',9,c)
    s+=text(865,507,f'{n:02d} / 12',11,ACC)
    slides.append(s)

def label(x,y,n,title,body,width=38):
    return text(x,y,n,13,ACC,True)+text(x,y+29,title,23,INK,True)+para(x,y+76,body,width,18)

def arrow(x,y,w=20):return line(x,y,w,ACC)+R(x+w-3,y-3,6,7,ACC)

s=start('Proyecto de datos','',dark=True)
s+=text(48,111,'EL CLIMA,',62,PAPER,True)+text(48,180,'CON HISTORIA.',62,PAPER,True)
s+=para(51,287,'Una aplicación para consultar, conservar y comparar datos meteorológicos de Hermosillo.',48,22,(.73,.79,.79),31)
s+=text(51,432,'PYTHON   /   POSTGRESQL   /   STREAMLIT   /   DOCKER',12,(.72,.78,.78))
# Stylized sun and horizon, fully vector.
s+=R(739,172,78,78,ACC)+line(673,297,225,TEAL)+line(694,323,204,TEAL)+line(721,349,177,TEAL)
s+=text(695,386,'29.0729° N',15,PAPER)+text(695,411,'110.9559° O',15,PAPER)
add(s,True)

s=start('01 / Propósito','Del dato externo a una vista útil','El valor está en integrar una fuente, conservar sus versiones y hacerlas comprensibles.')
s+=label(49,217,'01','Consultar','Condiciones actuales estimadas y pronósticos para una ubicación fija.',29)
s+=label(350,217,'02','Conservar','Capturas periódicas y versiones de los pronósticos dentro de PostgreSQL.',29)
s+=label(651,217,'03','Comparar','Diferencias entre valores actuales y predicciones con un día de anticipación.',29)
s+=line(329,211,1)+text(49,450,'El proyecto consume predicciones externas; no entrena un modelo propio.',16,TEAL)
add(s)

s=start('02 / Arquitectura','Tres servicios. Un flujo continuo.','El navegador muestra los datos guardados; la recolección funciona de manera independiente.')
for i,(title,role,detail) in enumerate([('Open-Meteo','FUENTE EXTERNA','HTTP / JSON'),('collector','SERVICIO PYTHON','Requests + Psycopg'),('db','POSTGRESQL 16','Tablas + volumen'),('dashboard','STREAMLIT','Navegador :8501')]):
    x=48+i*224
    s+=R(x,225,192,134,WHITE)+R(x,225,192,4,ACC if i==0 else TEAL)
    s+=text(x+14,247,role,10,MUT,True)+text(x+14,276,title,24,INK,True)+text(x+14,322,detail,12,MUT)
    if i<3:s+=arrow(x+197,292,19)
s+=line(272,393,640,TEAL)+text(432,409,'RED INTERNA DE DOCKER COMPOSE',12,TEAL,True)
add(s)

s=start('03 / Recolección','Una captura, paso a paso','collector/worker.py | Coordenadas fijas y zona America/Hermosillo.')
for i,(a,b) in enumerate([('Consultar','Dos peticiones: clima y predicciones anteriores.'),('Transformar','Fechas, series horarias y alineación de valores.'),('Guardar','Tres tablas en una transacción de PostgreSQL.'),('Esperar','600 segundos al terminar; después, repetir.')]):
    y=198+i*65
    s+=text(50,y,f'0{i+1}',20,ACC,True)+text(105,y,a,20,INK,True)+text(284,y+3,b,16,MUT)
    if i<3:s+=line(105,y+48,805)
s+=text(50,464,'Timeout HTTP: 30 s. Si ocurre un error, se registra y se reintenta en el siguiente ciclo.',13,TEAL)
add(s)

s=start('04 / Modelo de datos','Tres tablas, tres preguntas','schema.sql | Identificadores e índices temporales; sin claves foráneas entre tablas.')
for i,(name,q,fields) in enumerate([('observations','¿Qué valor tenemos ahora?',['fetched_at / observed_at','temperature / humidity','apparent_temperature','precipitation / wind_speed']),('forecasts','¿Qué esperábamos para cada hora?',['fetched_at / forecast_for','temperature / precipitation','precipitation_probability','UNIQUE(captura, hora destino)']),('comparisons','¿Cuánto cambió la predicción?',['fetched_at / valid_hour','current_temperature','predicted_temperature_24h','lluvia actual y predicha'])]):
    x=48+296*i
    s+=R(x,198,272,252,WHITE)+text(x+16,219,name,23,TEAL,True)+para(x+16,260,q,29,15,INK,21)
    for j,f in enumerate(fields):s+=text(x+16,321+j*25,f,12,MUT)
add(s)

s=start('05 / Versiones','Dos fechas que no significan lo mismo','Conservar versiones permite observar cómo evoluciona una misma predicción.')
s+=text(49,204,'fetched_at',24,TEAL,True)+para(49,246,'Momento en que se descargó el pronóstico.',35,19)
s+=text(510,204,'forecast_for',24,ACC,True)+para(510,246,'Hora para la que se calculó la predicción.',35,19)
s+=R(49,331,862,119,WHITE)+text(70,349,'EJEMPLO ILUSTRATIVO',10,ACC,True)
s+=text(70,379,'Hoy, 10:00',23,INK,True)+text(363,379,'Mañana, 15:00',23,INK,True)+text(727,379,'32 °C',29,TEAL,True)
s+=arrow(258,396,65)+arrow(609,396,65)+text(70,418,'Hora de descarga',12,MUT)+text(363,418,'Hora pronosticada',12,MUT)+text(727,418,'Predicción',12,MUT)
add(s)

s=start('06 / Comparación','Leer una desviación con cuidado','La diferencia describe un cambio respecto al pronóstico anterior.')
s+=R(49,202,862,105,INK)+text(76,234,'Actual estimado',26,PAPER,True)+text(323,232,'-',29,ACC,True)+text(372,234,'Pronóstico anterior',26,PAPER,True)+text(702,232,'=',29,ACC,True)+text(753,233,'Desviación',23,PAPER,True)
s+=text(51,338,'34 °C - 32 °C = +2 °C',33,ACC,True)+text(53,390,'Ejemplo ilustrativo, no una captura del sistema.',13,MUT)
s+=para(530,335,'Se comparan estimaciones de modelos. Para medir precisión real se necesitan observaciones independientes.',34,19,INK,28)
s+=text(52,453,'La precipitación se compara por hora para evitar mezclar intervalos distintos.',15,TEAL)
add(s)

s=start('07 / Visualización','Una interfaz, cuatro lecturas','app/dashboard.py | Esquema de la interfaz: no representa datos reales.')
s+=R(48,191,538,275,WHITE)
for i,t in enumerate(['Temperatura','Sensación','Humedad','Viento']):
    x=62+i*129;s+=R(x,207,117,55,PAPER)+text(x+8,216,t,11,MUT)+text(x+8,238,'--',17,TEAL,True)
s+=text(63,280,'PRONÓSTICO HORARIO',10,TEAL,True)
for j,h in enumerate([20,31,42,55,67,74,68,55,39,28,21,32]):s+=R(72+j*41,388-h,21,h,(.56,.72,.70))
s+=line(62,390,510)+text(64,412,'Desviaciones',13,INK,True)+text(320,412,'Historial local',13,INK,True)
s+=label(631,205,'LECTURA','Desde PostgreSQL','Última observación, última versión del pronóstico y hasta 300 capturas.',26)
s+=text(631,380,'60 s',36,ACC,True)+text(631,430,'Actualización de la vista',15,MUT)
add(s)

s=start('08 / Configuración','Docker hace reproducible el entorno','compose.yaml coordina el arranque, la comunicación y la persistencia.')
rows=[('Servicio','Imagen / entorno','Configuración principal'),('db','postgres:16-alpine','Volumen postgres_data + schema.sql'),('collector','python:3.12-slim','DATABASE_URL + UPDATE_SECONDS=600'),('dashboard','python:3.12-slim','Puerto 8501 + DATABASE_URL')]
for i,row in enumerate(rows):
    y=197+i*55
    if i==0:s+=R(49,y,862,46,INK)
    for x,v in zip([63,261,503],row):s+=text(x,y+13,v,14,PAPER if i==0 else INK,i==0)
    if i>0:s+=line(49,y+48,862)
s+=para(51,431,'db:5432 es una dirección interna. El navegador entra por localhost:8501.',83,16,TEAL,23)
add(s)

s=start('09 / Operación','Qué ocurre al arrancar o fallar','El diseño conserva datos y contempla reintentos básicos.')
s+=label(49,204,'ARRANQUE','Base disponible','pg_isready valida PostgreSQL antes de iniciar los otros servicios.',35)
s+=label(510,204,'RECUPERACIÓN','Errores registrados','El recolector registra excepciones y vuelve a intentar después de la espera.',35)
s+=line(49,370,862)+text(49,390,'Persistencia',20,TEAL,True)+para(49,425,'down conserva el volumen; down -v también elimina los datos.',48,16)
s+=text(510,390,'Transacciones',20,TEAL,True)+para(510,425,'Una falla de escritura revierte las inserciones de ese ciclo.',43,16)
add(s)

s=start('10 / Alcance','Límites que orientan las mejoras','Precisar el alcance ayuda a interpretar correctamente el resultado.')
for i,(a,b) in enumerate([('Horizonte del pronóstico','Tres días solicitados no garantizan 72 horas futuras completas.'),('Comparación temporal','La temperatura actual puede no coincidir con la hora redondeada.'),('Dependencia externa','Si falla la segunda API, tampoco se guarda la captura actual.'),('Paso a producción','Gestionar secretos, migraciones, retención y monitoreo.')]):
    y=195+i*67;s+=text(51,y,a,19,INK,True)+text(51,y+29,b,16,MUT)
add(s)

s=start('11 / Demostración','De la arquitectura a la pantalla','Ejecutar desde la carpeta clima-hermosillo. Iniciar antes de la exposición.',True)
for i,(a,b) in enumerate([('01  Iniciar','docker compose up --build -d'),('02  Revisar','docker compose ps'),('03  Ver actividad','docker compose logs --tail=30 collector'),('04  Navegar','http://localhost:8501')]):
    y=203+i*54;s+=text(49,y,a,16,(.72,.79,.79))+text(300,y,b,18,PAPER,True)
s+=text(50,449,'Obtener. Conservar. Comparar. Comunicar.',22,(.88,.52,.37),True)
add(s,True)

objects=[]
def obj(v):objects.append(v if isinstance(v,bytes) else v.encode('cp1252'));return len(objects)
root=obj('');pages=obj('');f1=obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>');f2=obj('<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>');ids=[]
for slide in slides:
    raw=slide.encode('cp1252');c=obj(b'<< /Length '+str(len(raw)).encode()+b' >>\nstream\n'+raw+b'endstream')
    ids.append(obj(f'<< /Type /Page /Parent {pages} 0 R /MediaBox [0 0 960 540] /Resources << /Font << /F1 {f1} 0 R /F2 {f2} 0 R >> >> /Contents {c} 0 R >>'))
objects[root-1]=f'<< /Type /Catalog /Pages {pages} 0 R >>'.encode();objects[pages-1]=f'<< /Type /Pages /Kids [{" ".join(str(i)+" 0 R" for i in ids)}] /Count {len(ids)} >>'.encode()
info=obj('<< /Title (Clima Hermosillo - Presentación) /Subject (Arquitectura, configuración y operación) >>')
b=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
for i,o in enumerate(objects,1):offsets.append(len(b));b+=f'{i} 0 obj\n'.encode()+o+b'\nendobj\n'
x=len(b);b+=f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode()
for o in offsets[1:]:b+=f'{o:010d} 00000 n \n'.encode()
b+=f'trailer\n<< /Size {len(objects)+1} /Root {root} 0 R /Info {info} 0 R >>\nstartxref\n{x}\n%%EOF\n'.encode()
f=Path(__file__).parent/'Presentacion_Clima_Hermosillo_Elegante.pdf';f.write_bytes(b);print(f.resolve())
