---
source: Manual_de_Usuario_SICOP_2025.pdf
pages: 60
file_size_mb: 4.81
extraction_date: "2026-04-21T16:43:51.163526+00:00"
language: unknown
tables_found: 75
has_images: true
has_scanned_pages: false
features_used: ["text_fast", "tables", "tables_camelot", "tables_tabula"]
extraction_time_sec: 2.73
quality_score: 74.0
quality_label: "acceptable"
is_valid: true
from_cache: false
warnings: ["camelot-py not installed; tables_camelot skipped", "tabula-py not installed; tables_tabula skipped"]
---
<!-- Page 1 -->

Manual de Usuario 
Sistema de Contabilidad y Presupuesto

“Funcionalidad para la ejecución del presupuesto”.

Última Actualización: Enero 2025

Versión: SICOP25 v17Oct2024

<!-- Page 2 -->

HOJA 
2 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

CONTENIDO

1. INTRODUCCIÓN ..................................................................................................................... 4

1.1 
ANTECEDENTES ............................................................................................................................................. 4 
1.2 
OBJETIVO DEL SICOP .................................................................................................................................. 4 
1.2.1 
NORMATIVIDAD APLICABLE .................................................................................................................... 4 
1.3 
ALCANCE ........................................................................................................................................................ 5 
1.4 
CONSIDERACIONES ....................................................................................................................................... 5 
1.5 
RECOMENDACIONES SOBRE EL USO DEL SISTEMA ....................................................................................... 5 
1.6 
USUARIOS(AS) FINALES ................................................................................................................................. 5 
1.7 
DEFINICIONES, ABREVIATURAS Y REFERENCIAS ........................................................................................... 6

2. ACCESO AL SISTEMA ............................................................................................................. 7

2.1 
TRÁMITE DE ACCESO AL SICOP ................................................................................................................... 7 
2.2 
INICIAR SESIÓN .............................................................................................................................................. 8 
2.3 
CAMBIAR ROL O CONTRASEÑA .................................................................................................................... 10

3. FUNCIONALIDADES DE USO GENERAL ....................................................................................11

3.1 
MENÚ PRINCIPAL ......................................................................................................................................... 11 
3.2 
COMUNICADOS ............................................................................................................................................ 12 
3.3 
FLUJOS DE TRABAJO .................................................................................................................................... 13 
3.3.1 
CARACTERÍSTICAS GENERALES DE LOS FLUJOS DE TRABAJO. ........................................................... 16 
3.3.2 
CARACTERÍSTICAS GENERALES DEL DOCUMENTO EN EL SICOP. ..................................................... 17 
3.4 
FUNCIONALIDADES DE LOS COMPONENTES DE LA PANTALLA ..................................................................... 18 
3.4.1 
COMPONENTES DEL ENCABEZADO ...................................................................................................... 18 
3.4.2 
COMPONENTES DEL MULTILÍNEA. ........................................................................................................ 20 
3.4.3 
COMPONENTES DE FILTROS ................................................................................................................ 23 
3.4.4 
BOTONES DE USO GENERAL ................................................................................................................ 24 
3.5 
AVANCE MÚLTIPLE ....................................................................................................................................... 26 
3.6 
CATÁLOGOS ................................................................................................................................................. 27 
3.6.1 
BOTONES PARA MANTENIMIENTO DE CATÁLOGOS .............................................................................. 29 
3.7 
CARGAS POR PLANTILLA .............................................................................................................................. 30 
3.7.1 
LAYOUT ................................................................................................................................................ 30 
3.7.2 
ESTADO DE TICKET .............................................................................................................................. 34 
3.7.3 
COPIA INTERFAZ .................................................................................................................................. 35

4. OPERACIÓN DEL SISTEMA .....................................................................................................37

4.1 
OPERACIÓN ................................................................................................................................................. 37 
4.2 
REPORTES ................................................................................................................................................... 37 
4.2.1 
BOTONES DE USO GENERAL PARA REPORTES .................................................................................... 38 
4.2.2 
PARÁMETROS PARA GENERAR REPORTES .......................................................................................... 39 
4.3 
EXTRACCIÓN DE INFORMACIÓN ................................................................................................................... 40 
4.3.1 
GENERAR UN PROCESO DE EXTRACCIÓN ............................................................................................ 40 
4.3.2 
BOTONES DEL EXTRACTOR DE INFORMACIÓN ..................................................................................... 47 
4.3.3 
EJECUTAR UN PROCESO DE EXTRACCIÓN ........................................................................................... 48

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 2 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 2 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 3 -->

HOJA 
3 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.4 
CONSULTAS ................................................................................................................................................. 51 
4.4.1 
CONSULTA GENERAL DEL PRESUPUESTO .......................................................................................... 51 
4.4.2 
BOTONES PARA CONSULTA GENERAL DEL PRESUPUESTO ................................................................ 55 
4.4.3 
CONSULTA DE ENVÍO SIAFF – WEB.................................................................................................. 55 
4.4.4 
BOTONES PARA CONSULTA EL ENVÍO SIAFF - WEB ......................................................................... 57 
4.5 
CONFIGURADOR(A) ...................................................................................................................................... 58 
4.5.1 
EJEMPLO 1 ........................................................................................................................................... 59 
4.5.2 
EJEMPLO 2 .......................................................................................................................................... 60

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 3 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 3 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 4 -->

HOJA 
4 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

1. INTRODUCCIÓN

1.1 
ANTECEDENTES 
 
Con el propósito de avanzar en la integración de la información contable y presupuestaria, el 
Gobierno Federal, a través de la Secretaría de Hacienda y Crédito Público (SHCP), presentó el 
Sistema de Contabilidad y Presupuesto (SICOP) con base en las mejores prácticas nacionales 
e internacionales, cuyo propósito no sólo es la transparencia de la información, la armonización 
y la rendición de cuentas, sino la transformación de la información disponible en una herramienta 
de política pública que coadyuve en la toma de decisiones y a la formulación de estrategias. 
 
El SICOP es la herramienta tecnológica para el procesamiento automático de las operaciones 
presupuestarias y extrapresupuestarias del Poder Ejecutivo Federal, en tiempo real y a nivel 
transaccional. De esta manera, el SICOP constituye el único punto de entrada para la recepción 
y el registro de operaciones presupuestarias para las dependencias del sector central de la 
Administración Pública Federal (APF). 
 
Asimismo, provee la información de los registros de las transacciones del Egreso que alimentan 
al Sistema de Contabilidad Gubernamental (SCG) para realizar el registro de las operaciones 
contables y producir los estados e informes financieros del Poder Ejecutivo Federal. 
 
Desde sus inicios, el SICOP ha presentado constantes mantenimientos que reflejan mejoras en 
su operación y actualizaciones derivadas de reformas en la normatividad aplicable, por lo que el 
presente instructivo deberá actualizarse con base en las transformaciones del sistema. 
 
1.2 
OBJETIVO DEL SICOP 
 
Procesar a nivel transaccional, en forma automática y en tiempo real todas las operaciones 
presupuestarias y extrapresupuestarias que acontecen en el ámbito del ente del Poder Ejecutivo 
y producir información sobre la ejecución del Presupuesto de Egresos estructurada de acuerdo 
con la clave presupuestaria en los diferentes momentos del egreso.

1.2.1 NORMATIVIDAD APLICABLE 
 
Lo anterior con fundamento en lo establecido en los artículos 73 y 90 de la Constitución Política 
de los Estados Unidos Mexicanos; 2, 3 y 31 de la Ley Orgánica de la Administración Pública 
Federal; 1, 52 y 57, de la Ley Federal de Presupuesto y Responsabilidad Hacendaria; 6, 9, 10, 
64, 65, 66 y 73 de su Reglamento; 1, 2, 4, 16, 38, 41 y 42 de la Ley General de Contabilidad 
Gubernamental; así como en el artículo 39 de la Ley de la Tesorería de la Federación, 96 y 99 
de su Reglamento; y 64 fracciones III y IV del Reglamento Interior de la Secretaría de Hacienda 
y Crédito Público; el Manual Administrativo de Aplicación General en Materia de Recursos 
Financieros; el Decreto del Presupuesto de Egresos de la Federación; la normatividad emitida 
por el Consejo Nacional de Armonización Contable y demás disposiciones relativas que resulten 
aplicables.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 4 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 4 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 5 -->

HOJA 
5 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

1.3 
ALCANCE 
 
El presente Manual está elaborado con el fin de ser un instrumento que apoye las tareas que las 
personas usuarias finales de SICOP ejecutarán en dicho sistema y que son parte de sus 
actividades y responsabilidades cotidianas. 
 
1.4 
CONSIDERACIONES 
 
1. El presente Manual de Usuario describe de manera general las tareas y actividades que

la persona usuaria final podrá ejecutar en el sistema, sin embargo, el acceso a cada 
funcionalidad depende del rol asignado.

2. El Manual está desarrollado con un enfoque de uso del sistema, no está diseñado para

solucionar dudas específicas de la aplicación de las normas y lineamientos contables 
definidos en la Ley General de Contabilidad Gubernamental y otras normas aplicables, 
por lo que, en éste, únicamente se incluyen los conceptos normativos y de operación 
necesarios para la comprensión del uso del sistema en la ejecución de los diferentes 
procesos que en él pueden realizar. 
 
1.5 
RECOMENDACIONES SOBRE EL USO DEL SISTEMA

 
La clave de acceso y la firma electrónica son de uso personal e intransferible. 
 
Guardar la información con frecuencia, en caso de problemas en la red de datos, 
servidores, base de datos, etc., no pierde la información capturada. 
 
Las opciones en el menú: catálogos, flujos de trabajo, eventos y datos, los privilegios de 
acceso, registro, consulta, etc., dependen del rol de la persona usuaria. 
 
El rol de la persona usuaria lo debe realizar el(la) configurador(a) de cada Ramo. 
 
La sesión se cierra cuando exista un tiempo sin actividad. Tiempo máximo de inactividad 
10 min. 
 
Se debe usar sólo una sesión a la vez. 
 
Utilizar como navegador de Internet el Firefox 51 de Mozilla. 
 
1.6 
USUARIOS(AS) FINALES 
 
Dependencias de la Administración Pública Federal.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 5 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 5 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 6 -->

HOJA 
6 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

1.7 
DEFINICIONES, ABREVIATURAS Y REFERENCIAS 
 
APF: Administración Pública Federal. 
 
COMPRANET: Es un sistema transaccional que permite a las instituciones públicas realizar 
procedimientos de contratación de manera electrónica, mixta o presencial; los licitantes, 
proveedores o contratistas cuentan con funcionalidades en el sistema que les permite consultar 
los procedimientos de contratación y enviar sus proposiciones técnicas y económicas de manera 
segura. Administrado por la Secretaría de la Función Pública (SFP). 
 
GPR: Government Resource Planning (ERP aplicado al gobierno) ERP (del inglés Enterprise 
Resource Planning) hace referencia a un conjunto de sistemas de información que gestionan 
todas las áreas de negocio de una organización: finanzas, ventas, marketing, producción, RRHH, 
cadena de suministro, etc. 
 
SCG 2.0: Sistema de Contabilidad Gubernamental 2.0. 
 
SHCP: Secretaría de Hacienda y Crédito Público: Secretaría. 
 
SICOP: Sistema de Contabilidad y Presupuesto. 
 
SIAFF: Sistema Integral de Administración Financiera Federal

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 6 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 6 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 7 -->

HOJA 
7 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

2. ACCESO AL SISTEMA

2.1 TRÁMITE DE ACCESO AL SICOP

Para ingresar al sistema es necesario realizar el trámite de registro con el(la) configurador(a) del 
SICOP de su Ramo, quien realiza el alta y asigna el rol correspondiente. De igual forma, para el 
caso de un reingreso es necesario ponerse en contacto con el(la)configurador(a) de usuarios de 
su Ramo para el trámite de activación.

Cada paso de los flujos de trabajo está relacionado con un rol. Dependiendo del rol que tenga la 
persona usuaria, son los privilegios que obtenga para su operación, ejemplo: tener acceso a 
ciertas acciones, catálogos y/o consultar cierta información. Las opciones del menú también 
dependen de los privilegios que tenga el perfil asociado al rol.

NOTAS:

1. Su usuario y contraseña es únicamente válido para la instancia de SICOP y el ciclo

presupuestario en el que fue registrado.

2. Es necesario tener instalada en el equipo la aplicación de JAVA para el correcto

funcionamiento del sistema.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 7 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 7 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 8 -->

HOJA 
8 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

2.2 INICIAR SESIÓN 
 
Una vez tramitado el acceso con su configurador(a), la persona usuaria debe ingresar al sistema 
y aparecen tres campos que se solicitan llenar: usuario, contraseña y seleccionar la instancia a 
la que se requiere ingresar, posteriormente se debe dar clic en el botón “Aceptar”.

La captura de los datos debe considerar mayúsculas y/o minúsculas de acuerdo con la 
información proporcionada a la persona usuaria. 
 
Si los datos no son correctos se mostrará el siguiente mensaje y se deberá revisar la información 
capturada:

Si los datos son correctos, se debe seleccionar un “Rol”. Esta opción varía según la configuración 
que tenga cada Ramo y los permisos que se le concedan a cada persona usuaria. Se debe 
seleccionar el rol a emplear según la actividad que vaya a realizar la persona usuaria en el 
sistema, dar clic en botón “Aceptar”.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 8 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 8 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 9 -->

HOJA 
9 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Una vez seleccionado el rol correspondiente, ingresa a la pantalla del SICOP la cual muestra el 
“Menú principal”, éste permite a la persona usuaria generar procesos, extracciones de 
información o solamente generar reportes y consultas.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 9 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 9 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 10 -->

HOJA 
10 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

2.3 CAMBIAR ROL O CONTRASEÑA

En caso de requerir cambiar el rol o la contraseña, en la parte superior derecha de la pantalla en

el letrero “Sesión” se ubica un ícono con flecha invertida 
 y al dar clic despliega las 
siguientes opciones: “Cambiar de Rol, Cambiar Contraseña y Salir”. 
 
Cambiar de Rol: permite ingresar a otra actividad configurada para la persona usuaria. 
Cambiar Contraseña: permite modificar la contraseña de acceso al SICOP de la persona usuaria.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 10 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 10 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 11 -->

HOJA 
11 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3. FUNCIONALIDADES DE USO GENERAL 
 
A continuación, se describe la funcionalidad de los principales componentes que la persona 
usuaria puede utilizar en la ejecución de tareas que lleve a cabo dentro del sistema.

3.1 MENÚ PRINCIPAL 
 
Después de haber firmado y seleccionado el rol requerido, al ingresar se muestra la página del 
SICOP, el “Menú Principal” contiene las carpetas que permite a las personas usuarias consultar 
manuales, guías o comunicados del sistema, generar procesos, extracciones de información o 
generar reportes y consultas.

De acuerdo con el rol seleccionado el “Menú Principal” muestra diferentes carpetas para generar 
entre otras funcionalidades, los flujos de trabajo.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 11 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 11 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 12 -->

HOJA 
12 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.2 COMUNICADOS

En esta carpeta las personas usuarias del SICOP pueden conocer las nuevas funcionalidades 
que se implementan en el sistema. Dicha carpeta se cuenta integrada por los apartados que se 
muestran en la siguiente figura:

En cada apartado se agregan los diferentes comunicados:

 
Funcionalidad Operativa se muestran el manual del usuario y las guías de operación.

 
Preguntas y Respuestas tiene el propósito de apoyar a las personas usuarias con las 
preguntas frecuentes y sus respectivas respuestas. 
 
Para consultar los documentos que se muestran en este apartado, las personas usuarias deben 
abrir la carpeta y el sistema despliega la lista de documentos existentes; después seleccionar el 
archivo requerido dar clic para visualizarlo. Los documentos se pueden consultar, imprimir o 
descargar.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 12 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 12 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 13 -->

HOJA 
13 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.3 FLUJOS DE TRABAJO

Para crear un nuevo proceso se tiene que utilizar la siguiente ruta: Seleccionar del Menú Principal 
la carpeta “Operación”, dar clic en la carpeta “Flujos de Trabajo” y elegir “Inbox”, como se muestra 
en la siguiente figura.

Al seguir esta ruta, el sistema direcciona al Inbox donde se pueden crear procesos nuevos en la 
“Bandeja de Entrada” (1) y buscar procesos capturados o finalizados en la sección “Procesos” 
(2).

1

2

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 13 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 13 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 14 -->

HOJA 
14 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Para crear un nuevo proceso, se debe dar clic en la flecha invertida
 (3), el sistema despliega 
todos los flujos de trabajo, a los que el rol ingresado tiene permisos de captura, posteriormente 
la persona usuaria debe seleccionar el tipo de flujo que requiere utilizar y dar clic en el botón 
“Iniciar Proceso” (3.1).

3.1

3

3.2

El sistema emite el “No. de Proceso” iniciado (3.2), el cual se debe conservar para posteriores 
consultas o seguimiento al trámite. Al seleccionar el botón “Aceptar” el sistema muestra la parte 
de inferior de la pantalla (4) el proceso iniciado y al dar clic nos lleva al documento para realizar 
la captura.

4

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 14 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 14 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 15 -->

HOJA 
15 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

La bandeja de “Procesos” (2) permite identificar algún proceso que se haya creado en el 
momento o con anterioridad mediante los siguientes filtros:

 
Procesos = Seleccionar el nombre del flujo de trabajo que se requiere consultar o trabajar. 
 
No. de proceso = Número que identifica el proceso que requiere consultar o trabajar. 
 
Fecha = Una vez especificado el flujo de trabajo a buscar, el sistema muestra todos los 
procesos que se encuentren dentro del rango de fechas solicitado. 
 
Ticket de carga = Cuando se trata de un archivo cargado por Layout (plantilla), el sistema 
recupera el o los procesos generados con dicho número de ticket. 
 
Una vez llenados los criterios se debe dar clic en el botón “Buscar”. El sistema muestra en la 
parte inferior de la pantalla (4) el proceso requerido, al dar clic nos lleva al documento para 
realizar la captura o dar seguimiento al trámite.

4

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 15 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 15 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 16 -->

HOJA 
16 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.3.1 CARACTERÍSTICAS GENERALES DE LOS FLUJOS DE TRABAJO.

Los flujos de trabajo representan el conjunto de pasos y acciones que definen los procesos que 
la persona usuaria debe avanzar, desde su inicio hasta su finalización, así como dar seguimiento 
en el sistema a cada uno de los documentos para ejecutar algún trámite. 
 
Los flujos de trabajo se muestran con la siguiente nomenclatura: 
 
Nombre:

WF_COMPROMISO_2 
 
Donde:

WF: Work Flow = Flujo de Trabajo 
COMPROMISO: Nombre referencia del documento 
2: Tipo de Flujo 
 
Existen los siguientes cuatro tipos de flujo y los más comunes son 1 y 2:

1. Descentralizado (unidad que captura es quien autoriza). La persona usuaria que lo

captura finaliza la transacción. 
 
2. Centralizado (por lo general autorizados por la DGPOP o equivalente quien finaliza el

registro). 
 
3. La carga es por LAYOUT y avanza de forma automática (carga de archivo).

Interacción del GRP de algunas dependencias con el SICOP. 
 
4. Requieren una autorización externa al Ramo en el SICOP para ser finalizados, por

ejemplo: Traspaso entre ramos.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 16 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 16 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 17 -->

HOJA 
17 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.3.2 CARACTERÍSTICAS GENERALES DEL DOCUMENTO EN EL SICOP.

La pantalla de captura o registro de información de cualquier flujo de trabajo que deriva de un 
documento, sirve para crear procesos para su posterior revisión y posible autorización. 
 
Los documentos en el sistema están integrados por los siguientes elementos:

Nombre 
Descripción 
Componente 
Es un campo de captura, que puede derivar de un catálogo, fecha, 
selección de valores o texto. 
Ejemplo: 
 Concepto 
La persona usuaria debe capturar el concepto en relación al flujo de trabajo.

* 
Significa que el dato es obligatorio. 
Encabezado 
Sección que permite realizar el registro general de información. Los 
componentes que corresponden al encabezado. (1)

Filtros 
Sección que funciona como un buscador de datos para facilitar el llenado 
de la sección Multilínea. (2)

Multilínea 
Sección que permite visualizar el detalle de las claves presupuestarias, 
según los criterios colocados en los filtros. (3)

1

2

Filtros 
Encabezado

3

Multilínea

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 17 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 17 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 17 (vía pdfplumber)

|  | Nombre |  |  | Descripción |  |
| - | ------ | - | - | ----------- | - |
| Componente |  |  | Es un campo de captura, que puede derivar de un catálogo, fecha,<br>selección de valores o texto.<br>Ejemplo:<br>Concepto<br>La persona usuaria debe capturar el concepto en relación al flujo de trabajo. |  |  |
| * |  |  | Significa que el dato es obligatorio. |  |  |
| Encabezado |  |  | Sección que permite realizar el registro general de información. Los<br>componentes que corresponden al encabezado. (1) |  |  |
| Filtros |  |  | Sección que funciona como un buscador de datos para facilitar el llenado<br>de la sección Multilínea. (2) |  |  |
| Multilínea |  |  | Sección que permite visualizar el detalle de las claves presupuestarias,<br>según los criterios colocados en los filtros. (3) |  |  |

<!-- Page 18 -->

HOJA 
18 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.4 FUNCIONALIDADES DE LOS COMPONENTES DE LA PANTALLA

3.4.1 COMPONENTES DEL ENCABEZADO

A continuación, se describen los principales componentes de la sección de encabezado:

Botones/Encabezado 
Descripción

Fechas. Para incorporar la fecha requerida (Inicial, final, 
etc.), dar clic en el triángulo invertido y se muestra el 
calendario del mes actual permitiendo cambiarlo de mes 
con flechas adelante-atrás y seleccionar el día. (1)

Componentes con lista de valores predefinidos. Al dar 
clic al triángulo invertido, se muestra una lista de selección 
(combo box) con los valores permitidos para el campo. No 
es posible capturar algún otro valor. (2)

Componentes con valores por default. Al abrir un 
documento es probable que aparezcan datos precapturados, esto es porque:

 
Son valores asignados por default que siempre 
van asociados al documento. 
 
Se ejecutó un proceso previo al abrir el 
documento que los llenó.

* 
Componentes obligatorios. Los componentes del 
encabezado que tengan un asterisco a la izquierda deben 
capturarse para poder avanzar.

Texto de ayuda. En la parte superior de la pantalla del 
documento (debajo de los íconos) se presenta un renglón 
con fondo amarillo en el cual se muestra la ayuda asociada 
a cada componente, indicando el significado de éste. La 
persona usuaria debe colocarse en el componente 
requerido y el sistema en la parte superior define la ayuda. 
(3)

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 18 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 18 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 18 (vía pdfplumber)

|  | Botones/Encabezado |  |  | Descripción |  |
| - | ------------------ | - | - | ----------- | - |
|  |  |  | Fechas. Para incorporar la fecha requerida (Inicial, final,<br>etc.), dar clic en el triángulo invertido y se muestra el<br>calendario del mes actual permitiendo cambiarlo de mes<br>con flechas adelante-atrás y seleccionar el día. (1) |  |  |
|  |  |  | Componentes con lista de valores predefinidos. Al dar<br>clic al triángulo invertido, se muestra una lista de selección<br>(combo box) con los valores permitidos para el campo. No<br>es posible capturar algún otro valor. (2) |  |  |
|  |  |  | Componentes con valores por default. Al abrir un<br>documento es probable que aparezcan datos pre-<br>capturados, esto es porque:<br> Son valores asignados por default que siempre<br>van asociados al documento.<br> Se ejecutó un proceso previo al abrir el<br>documento que los llenó. |  |  |
| * |  |  | Componentes obligatorios. Los componentes del<br>encabezado que tengan un asterisco a la izquierda deben<br>capturarse para poder avanzar. |  |  |
|  |  |  | Texto de ayuda. En la parte superior de la pantalla del<br>documento (debajo de los íconos) se presenta un renglón<br>con fondo amarillo en el cual se muestra la ayuda asociada<br>a cada componente, indicando el significado de éste. La<br>persona usuaria debe colocarse en el componente<br>requerido y el sistema en la parte superior define la ayuda.<br>(3) |  |  |

<!-- Page 19 -->

HOJA 
19 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Botones/Encabezado 
Descripción

Ventana de catálogo. Para algunos componentes del se 
muestra el ícono con una lupa a la derecha, significa que 
abren un “submenú” para poder seleccionar la opción que 
debe capturarse. Dar clic en el ícono para que se 
desplieguen los datos del catálogo. Seleccionar el dato 
deseado y dar clic en el botón aceptar. (4)

3

4

1

2

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 19 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 19 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 19 (vía pdfplumber)

|  | Botones/Encabezado |  |  | Descripción |  |
| - | ------------------ | - | - | ----------- | - |
|  |  |  | Ventana de catálogo. Para algunos componentes del se<br>muestra el ícono con una lupa a la derecha, significa que<br>abren un “submenú” para poder seleccionar la opción que<br>debe capturarse. Dar clic en el ícono para que se<br>desplieguen los datos del catálogo. Seleccionar el dato<br>deseado y dar clic en el botón aceptar. (4) |  |  |

<!-- Page 20 -->

HOJA 
20 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.4.2 COMPONENTES DEL MULTILÍNEA. 
 
Los siguientes botones del multilínea se encuentran en la parte inferior del encabezado:

Botones /Multilínea 
Descripción

Selecciona los registros. Permite seleccionar toda la 
información que se encuentren en el multilínea. La persona 
usuaria debe dar clic en el botón y el sistema selecciona 
toda la información (1). Para seleccionar / quitar una o más 
líneas dar clic en el recuadro de lado izquierdo del 
multilínea, como se muestra en el siguiente ejemplo.

Actualiza información. Permite refrescar la información 
del multilínea. La persona usuaria debe dar clic en el botón 
para actualizar la información en el multilínea.

Borra información. Elimina reglón seleccionado en el 
multilínea. La persona usuaria debe dar clic en el botón 
para borrar la información previamente seleccionada en el 
multilínea.

Edita los registros. Permite editar el renglón del 
multilínea. La persona usuaria debe seleccionar el 
elemento que requiere modificar y en el momento se 
encuentre resaltado en azul, dar clic en el botón para 
realizar los cambios, se muestra la ventana de captura. 
Ver imagen (2).

Copiar. Copia reglón seleccionado en el multilínea. 
Seleccione el renglón del detalle a copiar, dando clic en el 
recuadro que aparece a la izquierda del registro. 
Oprima el botón para copiar, se mostrará el renglón 
copiado al final del multilínea. Ver imagen (3).

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 20 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 20 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 20 (vía pdfplumber)

|  | Botones /Multilínea |  |  | Descripción |  |
| - | ------------------- | - | - | ----------- | - |
|  |  |  | Selecciona los registros. Permite seleccionar toda la<br>información que se encuentren en el multilínea. La persona<br>usuaria debe dar clic en el botón y el sistema selecciona<br>toda la información (1). Para seleccionar / quitar una o más<br>líneas dar clic en el recuadro de lado izquierdo del<br>multilínea, como se muestra en el siguiente ejemplo. |  |  |
|  |  |  | Actualiza información. Permite refrescar la información<br>del multilínea. La persona usuaria debe dar clic en el botón<br>para actualizar la información en el multilínea. |  |  |
|  |  |  | Borra información. Elimina reglón seleccionado en el<br>multilínea. La persona usuaria debe dar clic en el botón<br>para borrar la información previamente seleccionada en el<br>multilínea. |  |  |
|  |  |  | Edita los registros. Permite editar el renglón del<br>multilínea. La persona usuaria debe seleccionar el<br>elemento que requiere modificar y en el momento se<br>encuentre resaltado en azul, dar clic en el botón para<br>realizar los cambios, se muestra la ventana de captura.<br>Ver imagen (2). |  |  |
|  |  |  | Copiar. Copia reglón seleccionado en el multilínea.<br>Seleccione el renglón del detalle a copiar, dando clic en el<br>recuadro que aparece a la izquierda del registro.<br>Oprima el botón para copiar, se mostrará el renglón<br>copiado al final del multilínea. Ver imagen (3). |  |  |

<!-- Page 21 -->

HOJA 
21 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Botones /Multilínea 
Descripción

Busca información. Realiza la búsqueda de la 
información con los criterios insertados en los filtros, 
cerrando el proceso y no permitiendo el acceso hasta 
que la información se encuentre completa. La persona 
usuaria debe dar clic en el botón para obtener la 
información 
requerida 
en 
el 
multilínea, 
una 
vez 
establecidos los criterios de búsqueda en los filtros. El 
sistema envía el siguiente mensaje, dar clic al botón 
aceptar.

Mensaje de Sistema

Busca información. Realiza la búsqueda de la 
información con los criterios insertados en los filtros, 
buscando la información en el momento sin cerrar el 
proceso. Al dar clic en este botón se recuperan los 
registros en el multilínea con datos indicados en los filtros, 
delimitando la búsqueda. El sistema envía el siguiente 
mensaje.

Espere miesntras se ejecuta el siguiente proceso...

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 21 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 21 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 21 (vía pdfplumber)

|  | Botones /Multilínea |  |  | Descripción |  |
| - | ------------------- | - | - | ----------- | - |
|  |  |  | Busca información. Realiza la búsqueda de la<br>información con los criterios insertados en los filtros,<br>cerrando el proceso y no permitiendo el acceso hasta<br>que la información se encuentre completa. La persona<br>usuaria debe dar clic en el botón para obtener la<br>información requerida en el multilínea, una vez<br>establecidos los criterios de búsqueda en los filtros. El<br>sistema envía el siguiente mensaje, dar clic al botón<br>aceptar.<br>M ensaje de S istem a |  |  |
|  |  |  | Busca información. Realiza la búsqueda de la<br>información con los criterios insertados en los filtros,<br>buscando la información en el momento sin cerrar el<br>proceso. Al dar clic en este botón se recuperan los<br>registros en el multilínea con datos indicados en los filtros,<br>delimitando la búsqueda. El sistema envía el siguiente<br>mensaje.<br>E s p e re m ie s n tra s s e eje c u ta el s ig u ie n te p ro c es o ... |  |  |

<!-- Page 22 -->

HOJA 
22 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Imagen para seleccionar y editar los registros del multilínea.

1

2

Imagen para copiar en el multilínea. (En el ejemplo, el renglón 2 es copia del 1.)

3

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 22 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 22 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 23 -->

HOJA 
23 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.4.3 COMPONENTES DE FILTROS 
 
En la sección de los filtros la persona usuaria delimita la búsqueda de información para que el 
sistema recupere los datos en el multilínea o detalle. 
Después del llenado de filtros requeridos la persona usuaria debe dar clic en el ícono

para que el sistema realice la búsqueda de datos con los criterios insertados en los 
filtros, buscando la información en el momento sin cerrar el proceso, como se muestra en la 
siguiente imagen.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 23 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 23 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 24 -->

HOJA 
24 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.4.4 BOTONES DE USO GENERAL

En este apartado se describen las funciones estándar que la persona usuaria puede encontrar 
en los documentos del sistema.

Botón 
Descripción

Regresa al menú principal. Regresa al menú inicial del 
sistema, al dar clic al botón. Si capturó/modificó datos y no los 
guardó pide confirmación para salir.

Regresa al menú anterior. Cierra la pantalla del documento 
al dar clic y muestra nuevamente la pantalla anterior. En caso 
de captura o cambio, el sistema solicita confirmación antes de 
salir. Los datos no guardados se pierden.

Valida campos requeridos. Verifica que los datos 
obligatorios de los componentes hayan sido capturados o 
seleccionados del catálogo correspondiente, mostrando la 
lista de datos faltantes e indicando si pertenecen al 
encabezado o al multilínea. 
El documento no avanza al siguiente paso mientras no se 
capturen todos los datos obligatorios.

Guarda captura/cambios. Válida y guarda los datos 
capturados/modificados. Además de validar, guarda cambios 
capturados, en su caso, señala omisiones de captura 
obligatoria.

Valida datos. Valida datos de la pantalla y cálculo de 
fórmulas (reglas) asociadas al documento. Al ejecutar está 
acción el sistema guarda los datos capturados y regresa a la 
pantalla anterior. Para avanzar el documento es necesario 
volver a ingresar y en caso de que existan errores el sistema 
los muestra.

Envía a ... Envía el documento al siguiente paso; por ejemplo: 
de captura a revisor o de revisor a autorizador 
.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 24 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 24 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 24 (vía pdfplumber)

| Botón | Descripción |
| ----- | ----------- |
|  | Regresa al menú principal. Regresa al menú inicial del<br>sistema, al dar clic al botón. Si capturó/modificó datos y no los<br>guardó pide confirmación para salir. |
|  | Regresa al menú anterior. Cierra la pantalla del documento<br>al dar clic y muestra nuevamente la pantalla anterior. En caso<br>de captura o cambio, el sistema solicita confirmación antes de<br>salir. Los datos no guardados se pierden. |
|  | Valida campos requeridos. Verifica que los datos<br>obligatorios de los componentes hayan sido capturados o<br>seleccionados del catálogo correspondiente, mostrando la<br>lista de datos faltantes e indicando si pertenecen al<br>encabezado o al multilínea.<br>El documento no avanza al siguiente paso mientras no se<br>capturen todos los datos obligatorios. |
|  | Guarda captura/cambios. Válida y guarda los datos<br>capturados/modificados. Además de validar, guarda cambios<br>capturados, en su caso, señala omisiones de captura<br>obligatoria. |
|  | Valida datos. Valida datos de la pantalla y cálculo de<br>fórmulas (reglas) asociadas al documento. Al ejecutar está<br>acción el sistema guarda los datos capturados y regresa a la<br>pantalla anterior. Para avanzar el documento es necesario<br>volver a ingresar y en caso de que existan errores el sistema<br>los muestra. |
|  | Envía a ... Envía el documento al siguiente paso; por ejemplo:<br>de captura a revisor o de revisor a autorizador<br>. |

<!-- Page 25 -->

HOJA 
25 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Botón 
Descripción

Suspende. Al suspender el proceso no continúa y la acción 
solo aplica cuando el proceso aún no tiene afectación 
presupuestaria.

Informe de captura. Presenta un reporte de la captura 
realizada, al dar clic. Así mismo, se puede descargar o 
imprimir.

Adjunta documentos. Al dar clic el sistema muestra la ruta 
para adjuntar el archivo y permite agregar información del 
archivo anexo.

Archivos adjuntos

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 25 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 25 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 25 (vía pdfplumber)

| Botón | Descripción |
| ----- | ----------- |
|  | Suspende. Al suspender el proceso no continúa y la acción<br>solo aplica cuando el proceso aún no tiene afectación<br>presupuestaria. |
|  | Informe de captura. Presenta un reporte de la captura<br>realizada, al dar clic. Así mismo, se puede descargar o<br>imprimir. |
|  | Adjunta documentos. Al dar clic el sistema muestra la ruta<br>para adjuntar el archivo y permite agregar información del<br>archivo anexo.<br>A rch ivo s a d ju n to s |

<!-- Page 26 -->

HOJA 
26 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.5 AVANCE MÚLTIPLE

Esta opción permite avanzar varios procesos de un flujo de trabajo al mismo tiempo, siempre y 
cuando se encuentren en un mismo paso. 
 
Para realizar el avance múltiple la persona usuaria debe ingresar a Menú Principal, elegir la 
carpeta Operación y seleccionar la opción Avance Múltiple.

El sistema le muestra la siguiente pantalla:

1 
2

Posteriormente la persona usuaria debe seleccionar los parámetros de búsqueda. En sección 
“Proceso” (1) seleccionar el flujo de trabajo y en “Paso” (2) indicar el paso donde se encuentran 
los procesos. Por default el sistema presenta la fecha actual como fecha final de búsqueda, 
puede cambiarlas de acuerdo con sus requerimientos. 
 
Dé clic en el botón “Buscar” (3), si se encuentran procesos correspondientes al flujo de trabajo y 
al paso proporcionado, se muestran los registros permitiendo seleccionarlos con un pequeño 
recuadro antes del número de los procesos (4), seleccionar y luego elija la acción que requiera 
aplicar (5) y dé clic en el botón “Avanzar” (6).

3

6 
5

4

Todos los procesos avanzan al siguiente paso.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 26 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 26 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 27 -->

HOJA 
27 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.6 CATÁLOGOS

Esta funcionalidad le permite a la persona usuaria dar de alta, modificar, inactivar o eliminar 
registros de los catálogos, siempre y cuando tenga privilegios para ello. 
 
Seleccione desde el Menú Principal la carpeta Operación - Documentos y la opción de Catálogos.

Se presenta del lado derecho de la pantalla la lista de catálogos a los que la persona usuaria 
tiene acceso dependiendo del rol seleccionado, en la cual se puede ver el nombre, la descripción 
y el estado del catálogo.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 27 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 27 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 28 -->

HOJA 
28 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Un catálogo puede estar en estado activo o en mantenimiento. El catálogo activo puede 
modificarse y consultarse, el catálogo en mantenimiento no lo permite debido a que se encuentra 
en modificación. 
 
Para consultar el contenido del catálogo, la persona usuaria debe dar clic en el catálogo requerido 
y el sistema ingresa al catálogo seleccionado, como se muestra en el siguiente ejemplo:

Todos los catálogos tienen dos columnas en común: *Fecha efectiva y *Activo. La *Fecha 
efectiva, corresponde la fecha a partir de la cual el registro capturado tiene vigencia y *Activo, 
indica si un registro se encuentra activo o no. 
 
Si al presentarse el catálogo no muestra en el conjunto de registros, los que se requieren 
consultar o modificar, la persona usuaria debe dar clic en el botón “Filtrar” para buscar la 
información requerida. 
 
Es importante señalar que, de acuerdo con los privilegios del rol de la persona usuaria, el sistema 
permite:

• 
Ver o no la opción de catálogos en el menú. 
• 
Acceder a ciertos catálogos. 
• 
Modificar algunos o todos los componentes (columnas). 
• 
Dar de alta/eliminar/modificar renglones. 
• 
Consultar únicamente ciertos renglones.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 28 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 28 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 29 -->

HOJA 
29 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.6.1 BOTONES PARA MANTENIMIENTO DE CATÁLOGOS 
 
A continuación, se describen las acciones que pueden ser ejecutadas por la persona usuaria en 
los catálogos, a través de los botones de acción.

Botón 
Descripción

Regresa al menú anterior. Cierra la pantalla del catálogo, al dar clic y muestra 
nuevamente la pantalla anterior. Si capturó/modificó datos y no los guardó, el 
sistema pide confirmación para salir. Los datos no guardados se pierden.

Guarda captura/cambios. Valida y guarda los datos capturados/modificados. 
Además de validar, guarda cambios capturados, en su caso, señala omisiones 
de captura obligatoria.

Filtra. Filtra la información utilizando uno o más criterios de búsqueda.

Selecciona los componentes. Permite seleccionar toda la información que se 
encuentren en el catálogo. La persona usuaria debe dar clic en el botón y el 
sistema selecciona toda la información. Para seleccionar / quitar una o más 
líneas dar clic en el recuadro de lado izquierdo del catálogo, como se muestra 
en el siguiente ejemplo.

Actualiza información. Permite refrescar la información de los registros. La 
persona usuaria debe dar clic en el botón para actualizar la información.

Agrega. Permite a la persona usuaria la captura de un nuevo registro. El 
sistema despliega la pantalla para captura de datos.

Borra información. Elimina renglón seleccionado en el catálogo. La persona 
usuaria debe dar clic en el botón para borrar la información previamente 
seleccionada en los registros.

Edita los registros. Permite editar el renglón del catálogo. La persona usuaria 
debe seleccionar el elemento que requiere editar y en el momento que se 
encuentre resaltado en azul, dar clic en el botón para acceder realizar los 
cambios.

Copiar. Copia el renglón seleccionado en el catálogo. La persona usuaria debe 
seleccionar el renglón a copiar, dando clic en el recuadro que aparece a la 
izquierda del registro, posteriormente dar clic en el botón para copiar y el 
sistema muestra el renglón copiado al final de los registros.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 29 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 29 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 29 (vía pdfplumber)

| Botón | Descripción |
| ----- | ----------- |
|  | Regresa al menú anterior. Cierra la pantalla del catálogo, al dar clic y muestra<br>nuevamente la pantalla anterior. Si capturó/modificó datos y no los guardó, el<br>sistema pide confirmación para salir. Los datos no guardados se pierden. |
|  | Guarda captura/cambios. Valida y guarda los datos capturados/modificados.<br>Además de validar, guarda cambios capturados, en su caso, señala omisiones<br>de captura obligatoria. |
|  | Filtra. Filtra la información utilizando uno o más criterios de búsqueda. |
|  | Selecciona los componentes. Permite seleccionar toda la información que se<br>encuentren en el catálogo. La persona usuaria debe dar clic en el botón y el<br>sistema selecciona toda la información. Para seleccionar / quitar una o más<br>líneas dar clic en el recuadro de lado izquierdo del catálogo, como se muestra<br>en el siguiente ejemplo. |
|  | Actualiza información. Permite refrescar la información de los registros. La<br>persona usuaria debe dar clic en el botón para actualizar la información. |
|  | Agrega. Permite a la persona usuaria la captura de un nuevo registro. El<br>sistema despliega la pantalla para captura de datos. |
|  | Borra información. Elimina renglón seleccionado en el catálogo. La persona<br>usuaria debe dar clic en el botón para borrar la información previamente<br>seleccionada en los registros. |
|  | Edita los registros. Permite editar el renglón del catálogo. La persona usuaria<br>debe seleccionar el elemento que requiere editar y en el momento que se<br>encuentre resaltado en azul, dar clic en el botón para acceder realizar los<br>cambios. |
|  | Copiar. Copia el renglón seleccionado en el catálogo. La persona usuaria debe<br>seleccionar el renglón a copiar, dando clic en el recuadro que aparece a la<br>izquierda del registro, posteriormente dar clic en el botón para copiar y el<br>sistema muestra el renglón copiado al final de los registros. |

<!-- Page 30 -->

HOJA 
30 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.7 CARGAS POR PLANTILLA 
 
Esta opción le permite cargar un archivo formato .CSV separados por comas para posteriormente 
pasar la información a los componentes del documento asociado al flujo de trabajo que la persona 
usuaria desee operar en el sistema. 
 
Los layout (plantilla) son utilizados para estructurar el archivo .CSV para la carga de cada 
documento.

3.7.1 LAYOUT 
 
Para descargar el layout o plantilla la persona usuaria debe ingresar al Menú Principal - 
Operación - Documentos - Carga de Archivo (csv), como se muestra en la siguiente imagen.

Al dar clic en la opción “Carga de Archivo (cvs)”, el sistema muestra la pantalla donde se puede 
seleccionar el flujo de trabajo que se requiere cargar.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 30 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 30 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 31 -->

HOJA 
31 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

En la pantalla Carga de Archivo, la persona usuaria debe dar clic en el botón del triángulo

invertido 
, el sistema despliegala lista de los flujos de trabajo a los que se tenga acceso,

dependiendo del rol. Seleccione el flujo de trabajo.

El sistema muestra en 5 columnas la siguiente información: Nombre, Descripción, CSV, XSD, y 
Estatus.

1

Seleccione el nombre del documento que se muestra debajo de la columna CSV que aparece en 
el sistema con letra azul y subrayada.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 31 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 31 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 32 -->

HOJA 
32 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

El sistema muestra la ventana “Abriendo…” en donde la persona usuaria puede descargar la 
plantilla en Excel en donde se muestra las columnas con la información que se debe capturar.

Cada celda se debe sustituir por el valor del documento.

El layout creado, en primera instancia se recomienda guardarlo como .XLSX con dos pestañas: 
una con los datos con encabezados y otra con los datos sin encabezados auxiliares. 
 
Ejemplo:

Si en el layout desean cargar varios movimientos, simplemente deben pegar uno tras otro, cada 
encabezado representa un proceso como se muestra en el ejemplo:

Ya teniendo la información guardada como .XLSX, la persona usuaria se debe colocar en la 
pestaña de los datos simples y guardar el archivo como .CSV. 
 
Para no perder el formato de los datos que han sido asignados, TODO lo que el archivo pregunte 
al darle guardar, debe decir Si o ACEPTAR. TODO lo que pregunte al darle CERRAR, debe decir 
NO. 
 
Una vez que tenemos el archivo .CVS lo convertimos a formato .ZIP, dar clic derecho para enviar 
al formato, como se muestra en el ejemplo:

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 32 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 32 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 33 -->

HOJA 
33 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Una vez que contamos con el archivo .ZIP, ingresamos al sistema a la ruta Operación - 
Documentos - Carga de Archivo se carga el archivo en la misma ventana donde se descargó la 
plantilla para el layout.

Seleccionar de la pantalla “Carga de Archivo”, el flujo de trabajo del documento que se requiera, 
dar clic en el botón “Buscar”, elegir el documento en ZIP y dar clic en “Aceptar”, el sistema genera 
el número de ticket de la carga, mismo que la persona usuaria deberá anotar sin comas.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 33 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 33 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 34 -->

HOJA 
34 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

3.7.2 ESTADO DE TICKET

Para revisar que la carga sea satisfactoria, seleccione la opción del Menú Principal - Operación 
-Documentos - “Estado de Ticket” y el sistema muestra la pantalla “Verificar Estado de Ticket”: 
La persona usuaria debe captura en la caja de texto el número de ticket que asignó el sistema 
en la carga, dar clic en el botón “Aceptar”.

Cuando la carga no genera errores, manda el mensaje de TERMINADO.

En la pantalla “Verificar Estado de Ticket”, si el archivo de carga contiene errores, nos indica en 
donde está el error. La persona usuaria debe corregir el archivo, guardar de nuevo el .CSV, crear 
el .ZIP y cargar de nueva cuenta generando otro ticket.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 34 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 34 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 35 -->

HOJA 
35 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

El sistema puede presentar tres posibles estatus de la carga:

Estado 
Descripción

En proceso 
Indica que el archivo aún se está validando. Debe consultar nuevamente 
su estado.

Terminado

Indica que el archivo se terminó de validar, que los datos fueron correctos 
y que puede proceder con la copia de los datos hacia las tablas de 
operación.

Indica que el archivo se validó y se muestran en la pantalla la lista de 
errores.

Terminado con 
Errores

En caso de error, debe corregir su archivo de datos e iniciar un nuevo 
proceso de carga (un nuevo ticket).

Después de obtener la carga del archivo con éxito se debe ingresa a la opción “Copia Interfaz” 
para generar el proceso.

3.7.3 COPIA INTERFAZ

Para realizar la copia de la interfaz generada, seleccione la opción del Menú Principal - Operación 
- Documentos - “Copia Interfaz” y registre el número de ticket, dar clic en el botón “Aceptar”.

Si el proceso de la copia es satisfactorio, el sistema despliega un mensaje indicando “Envío a 
copiado exitoso”.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 35 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 35 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 35 (vía pdfplumber)

|  | Estado |  |  | Descripción |  |
| - | ------ | - | - | ----------- | - |
| En proceso |  |  | Indica que el archivo aún se está validando. Debe consultar nuevamente<br>su estado. |  |  |
| Terminado |  |  | Indica que el archivo se terminó de validar, que los datos fueron correctos<br>y que puede proceder con la copia de los datos hacia las tablas de<br>operación. |  |  |
| Terminado con<br>Errores |  |  | Indica que el archivo se validó y se muestran en la pantalla la lista de<br>errores.<br>En caso de error, debe corregir su archivo de datos e iniciar un nuevo<br>proceso de carga (un nuevo ticket). |  |  |

<!-- Page 36 -->

HOJA 
36 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

El sistema genera un “número de proceso” por cada proceso que se haya cargado en el archivo, 
el cual se puede operar ingresando al Menú Principal – Operación – Flujos de Trabajo – Inbox 
para abrir la pantalla “Bandeja de Entrada” - “Procesos”.

Al ingresar a la pantalla “Bandeja de Entrada” en la sección “Procesos” la persona usuaria debe 
capturar en el campo “Ticket de Carga” el número de ticket con el que se generó la carga de 
archivo y el sistema muestra el o los procesos generados (1). Se debe seleccionar el proceso 
(fila color azul) y al dar clic se ingresa al documento del proceso requerido.

1

Se puede selecionar un rango de fechas con la finalidad de que muestre toda la información 
generada y relacionada al número de ticket. 
 
Después de seleccionar el proceso el sistema accesa a la pantalla del documento requerido en 
donde la persona usuaria debe dar trámite a su documento. Para continuar el flujo de trabajo 
seleccionado, la persona usuaria debe realizar los pasos que se explican en el apartado “3.3 
Flujos de Trabajo” del presente Manual.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 36 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 36 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 37 -->

HOJA 
37 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4. OPERACIÓN DEL SISTEMA

4.1 OPERACIÓN

El presente apartado está enfocado a la descripción específica de los flujos de trabajo asociados 
a los documentos que pueden ser ejecutados por la persona usuaria final para poder registrar y 
controlar su operación en el sistema. 
 
Se debe considerar que los flujos de trabajo están agrupados en procesos y que la descripción 
del Manual está hecha sobre la funcionalidad central de flujos y documentos del SICOP, por lo 
que los flujos, documentos, componentes y catálogos pueden cambiar respecto a la 
configuración personalizada que cada Ramo definió para adaptar las particularidades de su 
operación y normativa al sistema central.

4.2 REPORTES

El SICOP en su Menú Principal cuenta con la carpeta de Reportes la cual contiene reportes que 
pueden exportarse a un archivo (PDF). Principalmente se puede generar informes estructurados 
para toma de decisiones o como soporte documental del registro realizado en el SICOP. 
 
En la carpeta de Reportes, los principales son “Estados del Presupuesto” y “Movimientos por 
Proceso”.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 37 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 37 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 38 -->

HOJA 
38 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Los Reportes “Estados del Presupuesto” permiten conocer al momento, el estado del 
presupuesto correspondiente al Ramo, ordenándolo por Unidad, Objeto de gasto, Clave 
presupuestaria o Concepto de gasto. Permite colocar parámetros como filtro de la información a 
generar. 
 
Los reportes de “Movimientos por Proceso” permiten contar con un soporte documental del 
registro efectuado en el SICOP de un documento (ejemplo Compromiso o Cuenta por Liquidar 
Certificada). 
 
Los parámetros, por lo general, solicitan el número del documento (por ejemplo: número de 
solicitud de pago) y/o folio en algunos casos. Además, nos permiten localizar procesos, 
generando una búsqueda por parámetros como objeto de gasto, fechas, si se encuentra en 
trámite o está autorizada, y demás criterios. 
 
Para generar reportes, la persona usuaria cuenta con búsquedas de información y se pueden 
utilizar para lectura o impresión.

4.2.1 BOTONES DE USO GENERAL PARA REPORTES

Botón 
Descripción

Enviar consulta. Abre el reporte con los parámetros solicitados, en 
formato PDF.

Restablecer. Limpia los parámetros modificados, por los que arroja 
el sistema por default.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 38 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 38 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 38 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Enviar consulta. Abre el reporte con los parámetros solicitados, en<br>formato PDF. |  |  |
|  |  |  | Restablecer. Limpia los parámetros modificados, por los que arroja<br>el sistema por default. |  |  |

<!-- Page 39 -->

HOJA 
39 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.2.2 PARÁMETROS PARA GENERAR REPORTES

Los criterios de búsqueda en los reportes son:

Donde: 
A.ID_UNIDAD IN ('700','710') 
Se indica de qué unidades requerimos la información:

• 
Si sólo es un par de unidades, las separamos como sé muestra en el ejemplo, con una 
‘coma’: 
 
 A.ID_UNIDAD IN (‘100',‘110') 
• 
Si se trata de un rango de unidades, se especifica de la siguiente manera: 
 
A.ID_UNIDAD BETWEEN ‘100' AND ‘118’ 
 
AND SUBSTR (A. SUBCUENTA,25,8) 
Esta sección indica la forma en que vamos a filtrar, es decir, por programa prioritario, objeto de 
gasto, o sólo capitulo, entidad federativa, etc... 
 
El ejemplo nos dice A. SUBCUENTA,25,8 donde:

• 
25 = indica la posición donde comienza el criterio de búsqueda, para este caso, 
empieza en capítulo. 
• 
8 = El número de posiciones que ocupa el criterio a considerar, para este caso, se está 
indicando el objeto de gasto completo, incluidos los puntos de separación, es decir: si 
queremos el COG: 21101, el criterio se especifica así 2.1.1.01, si contamos los 
caracteres son 8. 
 
IN ('2.1.1.01','2.4.1.03') 
Se indica el rango del filtro, en este caso, de que objetos de gasto se van a filtrar:

• 
Si sólo es un par de filtros, las separamos como sé muestra en el ejemplo, con una 
‘coma’: 
 
 IN (‘3.7.2.04’, ‘3.7.5.04') 
• 
Si se trata de un rango de filtros, se especifica de la siguiente manera: 
 
BETWEEN ‘3.7.2.04‘AND ‘3.7.5.04' 
 
Por lo anterior, si lo que desea es ver la información de la unidad 700 a la 800 y filtrar por 
programa M001, la línea debe indicarse de la siguiente forma: 
 
A.ID_UNIDAD BETWEEN '700‘AND ‘800' AND SUBSTR(A.SUBCUENTA,20,4) IN (‘M001')

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 39 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 39 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 40 -->

HOJA 
40 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.3 EXTRACCIÓN DE INFORMACIÓN

Un proceso de extracción le permite obtener datos relacionados con los documentos y con las 
tablas de saldos y movimientos, condicionados mediante valores fijos o variables que pueden 
ser sustituidos al momento de ejecución. Una vez que el proceso se ha definido es posible 
ejecutarlo una y otra vez para generar archivos de salida de tipo .CSV y .XML que pueden ser 
editados con herramientas fuera del sistema.

4.3.1 GENERAR UN PROCESO DE EXTRACCIÓN

Seleccione la opción Extracción en su menú principal, como se muestra en la siguiente figura:

Se presenta del lado derecho de la pantalla la lista de procesos de extracción previamente 
definidos, y el botón “Nuevo”, que le permite generar una nueva extracción.

1

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 40 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 40 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 41 -->

HOJA 
41 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

En la lista de procesos de extracción en el encabezado (1) se presentan los siguientes datos:

Etiqueta 
Descripción

Clave 
Es una clave única que identifica a la extracción.

Descripción 
Es la definición de manera general de la extracción.

Documento/saldos/movimientos 
Muestra el nombre del documento.

Estado 
Los estados posibles son:

1) En definición: es posible modificar/copiar/borrar. 
2) Liberado: la extracción ya se encuentra en uso por algún

rol y no es posible modificarlo. 
3) Suspendido: la extracción ya no está siendo usada, pero

tampoco es posible modificarla ni borrarla, dado que ya 
existe registro de su uso. 
 
Al seleccionar nuevo el sistema presenta la siguiente pantalla:

3

2

La persona usuaria debe capturar la clave, descripción (se muestran en una pantalla de 
Extracción de información inicial) y posteriormente seleccionar movimientos. En la pestaña 
Columna, se deben seleccionar los componentes que se requiere aparezcan en el archivo de 
salida como encabezado, la fecha de aplicación, el Ramo, la Unidad, etc. 
Al seleccionar: Documento, Saldos o Movimientos (2), en automático se presenta una lista del 
lado izquierdo de la pantalla con todos los componentes disponibles, puede seleccionar todos y 
enviarlos a la lista de la derecha (3) o ir seleccionando uno a uno.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 41 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 41 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 41 (vía pdfplumber)

| Etiqueta | Descripción |
| -------- | ----------- |
| Clave | Es una clave única que identifica a la extracción. |
| Descripción | Es la definición de manera general de la extracción. |
| Documento/saldos/movimientos | Muestra el nombre del documento. |
| Estado | Los estados posibles son:<br>1) En definición: es posible modificar/copiar/borrar.<br>2) Liberado: la extracción ya se encuentra en uso por algún<br>rol y no es posible modificarlo.<br>3) Suspendido: la extracción ya no está siendo usada, pero<br>tampoco es posible modificarla ni borrarla, dado que ya<br>existe registro de su uso. |

<!-- Page 42 -->

HOJA 
42 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Para los Documentos:

 
Por default se presenta seleccionados el Ramo - Unidad creadora y el Folio del 
documento, y no puede eliminarse.

 
Los nombres que ve son la etiqueta del componente y entre paréntesis su descripción.

Para el caso de Saldos y Movimientos:

 
Los nombres que ve son los nombres de las columnas en base de datos y son 
representativos del dato que contienen.

En la pestaña Catálogos se muestra una lista de selección con los valores de los Catálogos 
asociados al documento, a saldos o movimientos, según aplique, puede seleccionarlos (4), y en 
la lista (5) que aparece del abajo de lado izquierdo de la pantalla, se muestra sus componentes, 
los cuales también pueden seleccionarlos y enviarlos a la lista de la derecha, éstos en conjunto 
con los seleccionados en la pestaña Columnas, son los que conforman las columnas para el 
archivo de salida.

4

6

5

Observe en la pantalla que para identificar de cual catálogo fue seleccionado cada componente, 
se muestra en la lista de la derecha (6) el nombre del catálogo en mayúsculas seguido de la 
etiqueta del componente y de la descripción. 
 
En la pestaña Condiciones se definen las condiciones que se aplican para obtener la 
información de la base de datos, aun cuando no es obligatorio poner condiciones, se sugiere que 
las ponga para evitar procesamiento innecesario para la base de datos, para reducir el tamaño 
de los archivos de salida y lo más importante por seguridad de la información.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 42 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 42 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 43 -->

HOJA 
43 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

7

Dé clic en el botón Agregar y se muestra en la pantalla las condiciones adicionadas (7). 
 
Para eliminar una condición, marque el renglón y dé clic en el botón Eliminar. Para modificar una 
condición, marque el renglón y dé clic en el botón Editar. Las condiciones las puede cambiar de 
orden usando las flechas arriba, abajo, que se encuentran a la derecha de la lista de condiciones. 
 
Para dar de alta una condición se debe considerar lo siguiente:

Etiqueta 
Descripción

Conector 
Seleccionar el conector (AND u OR). Es obligatorio seleccionar como conector 
para la primera condición la palabra AND.

Componente

Seleccionar el componente que se va a condicionar, se muestra una lista de 
los componentes del documento/saldos/movimientos.

Seleccionar el operador de la lista. Los operadores disponibles son:

> 
mayor que

>= 
mayor igual que

Operador

< 
menor que

<= 
menor igual que

= 
Igual

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 43 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 43 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 43 (vía pdfplumber)

| Etiqueta | Descripción |
| -------- | ----------- |
| Conector | Seleccionar el conector (AND u OR). Es obligatorio seleccionar como conector<br>para la primera condición la palabra AND. |
| Componente | Seleccionar el componente que se va a condicionar, se muestra una lista de<br>los componentes del documento/saldos/movimientos. |
| Operador | Seleccionar el operador de la lista. Los operadores disponibles son:<br>> mayor que<br>>= mayor igual que<br>< menor que<br><= menor igual que<br>= Igual |

<!-- Page 44 -->

HOJA 
44 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Etiqueta 
Descripción

!= 
diferente

Like 
que contenga

Not like 
que no contenga

Between 
entre

Not betwen 
que no esté entre

In 
que esté en la lista

Not in 
que no esté en la lista

Proporcionar el valor para la condición.

1) Para el caso de like y not like, la persona usuaria debe poner el valor

encerrado entre apóstrofes y el “%” donde lo requiera. Ejemplo: ‘%ABC’ 
o ‘ABC%’ o ‘A%B%C’. 
2) Para el caso de between y not between se tiene que proporcionar un

valor inicial y uno final. 
3) Para el caso de in y not in se tiene que proporcionar la lista de valores.

Valor 1

Valor 2

La persona usuaria debe poner los apóstrofes que encierren cada valor 
y las comas de separación cuando se trate de valores tipo fecha o 
caracteres alfanuméricos. Ejemplo: ‘valor1’, ‘valor2’, ‘valor3’. 
4) La persona usuaria también debe poner las fechas en formato correcto

“dd/mm/yyyy”. 
5) Para el caso que una condición se quiera dejar con un valor variable el

cual sea solicitado al momento de ejecución de la extracción, se debe 
poner únicamente el carácter “?” en el campo del valor.

( )

Es posible poner paréntesis de apertura y cierre para agrupar las condiciones 
según la prioridad en que se requiera se ejecuten.

En la pestaña Orden de Columnas, se indica el orden en el que aparecerán los nombres de las 
columnas en el encabezado del archivo de salida. 
 
La pantalla muestra todas las columnas seleccionadas en las pestañas de Columnas y 
Catálogos, para ordenarlas existen dos formas:

1. Use las flechas arriba o abajo que se encuentran a la derecha de la lista.

2. Seleccione una columna con el botón izquierdo del mouse y arrástrela a la

posición deseada.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 44 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 44 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 44 (vía pdfplumber)

| Etiqueta | Descripción |
| -------- | ----------- |
|  | != diferente<br>Like que contenga<br>Not like que no contenga<br>Between entre<br>Not betwen que no esté entre<br>In que esté en la lista<br>Not in que no esté en la lista |
| Valor 1<br>Valor 2 | Proporcionar el valor para la condición.<br>1) Para el caso de like y not like, la persona usuaria debe poner el valor<br>encerrado entre apóstrofes y el “%” donde lo requiera. Ejemplo: ‘%ABC’<br>o ‘ABC%’ o ‘A%B%C’.<br>2) Para el caso de between y not between se tiene que proporcionar un<br>valor inicial y uno final.<br>3) Para el caso de in y not in se tiene que proporcionar la lista de valores.<br>La persona usuaria debe poner los apóstrofes que encierren cada valor<br>y las comas de separación cuando se trate de valores tipo fecha o<br>caracteres alfanuméricos. Ejemplo: ‘valor1’, ‘valor2’, ‘valor3’.<br>4) La persona usuaria también debe poner las fechas en formato correcto<br>“dd/mm/yyyy”.<br>5) Para el caso que una condición se quiera dejar con un valor variable el<br>cual sea solicitado al momento de ejecución de la extracción, se debe<br>poner únicamente el carácter “?” en el campo del valor. |
| ( ) | Es posible poner paréntesis de apertura y cierre para agrupar las condiciones<br>según la prioridad en que se requiera se ejecuten. |

<!-- Page 45 -->

HOJA 
45 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

La pestaña Orden de Datos, permite definir el orden en el que aparecerán las columnas de los 
renglones en el archivo de salida.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 45 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 45 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 46 -->

HOJA 
46 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Para el caso de los documentos por default, se presentan seleccionados el Ramo, Unidad 
creadora y el Folio del documento [2], no pueden deseleccionarse. 
 
Pase de la lista de la izquierda a la derecha las columnas por las cuales quiera ordenar los datos, 
con el siguiente botón 
 . 
 
La lista de datos seleccionados se puede ordenar por columna de forma ascendente o 
descendente dando clic en los botones que están debajo de la lista. Una vez que termine de 
definir su extracción dé clic en el botón Validar y Guardar. 
 
Si la extracción es correcta y está completa dé clic en Liberar, aparece una pantalla en la cual 
debe seleccionar los roles a los cuales les permite ejecutar las extracciones ya liberadas.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 46 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 46 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 47 -->

HOJA 
47 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.3.2 BOTONES DEL EXTRACTOR DE INFORMACIÓN

Botón 
Descripción

Nuevo. Crea una nueva plantilla de extracción de información.

Copiar. Permite copiar la configuración de la extracción que se 
tenga en pantalla a otra extracción con diferente nombre. Para 
realizar la copia es necesario que la extracción se encuentre en 
estatus LIBERADO. La copia queda en estatus EN DEFINICIÓN.

Borrar. Permite eliminar la extracción que se tenga en pantalla, 
previa confirmación.

Suspender. Cambia el estatus de la extracción a SUSPENDIDO, 
para lo cual el estatus original debe ser LIBERADO. Una vez que 
se suspende la extracción ya no se puede ejecutar.

Validar. Arma la consulta con todos los datos capturados y la 
ejecuta en la base de datos para verificar que es correcta, cualquier 
error que se presente se muestra en pantalla.

Guardar. Almacena la configuración realizada en la extracción, aun 
cuando tenga errores de validación. El estatus es EN DEFINICIÓN. 
Cuando se encuentra EN DEFINICIÓN, no se puede ejecutar.

Liberar. Valida y guarda la configuración realizada, si existen 
errores los presenta en pantalla; pero si no hay errores le cambia el 
estatus a LIBERADO a la extracción y ya no se puede realizar 
cambios, además se presenta una pantalla con la lista de roles 
disponibles para que seleccione que roles tienen privilegios de 
ejecución de la extracción definida.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 47 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 47 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 47 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Nuevo. Crea una nueva plantilla de extracción de información. |  |  |
|  |  |  | Copiar. Permite copiar la configuración de la extracción que se<br>tenga en pantalla a otra extracción con diferente nombre. Para<br>realizar la copia es necesario que la extracción se encuentre en<br>estatus LIBERADO. La copia queda en estatus EN DEFINICIÓN. |  |  |
|  |  |  | Borrar. Permite eliminar la extracción que se tenga en pantalla,<br>previa confirmación. |  |  |
|  |  |  | Suspender. Cambia el estatus de la extracción a SUSPENDIDO,<br>para lo cual el estatus original debe ser LIBERADO. Una vez que<br>se suspende la extracción ya no se puede ejecutar. |  |  |
|  |  |  | Validar. Arma la consulta con todos los datos capturados y la<br>ejecuta en la base de datos para verificar que es correcta, cualquier<br>error que se presente se muestra en pantalla. |  |  |
|  |  |  | Guardar. Almacena la configuración realizada en la extracción, aun<br>cuando tenga errores de validación. El estatus es EN DEFINICIÓN.<br>Cuando se encuentra EN DEFINICIÓN, no se puede ejecutar. |  |  |
|  |  |  | Liberar. Valida y guarda la configuración realizada, si existen<br>errores los presenta en pantalla; pero si no hay errores le cambia el<br>estatus a LIBERADO a la extracción y ya no se puede realizar<br>cambios, además se presenta una pantalla con la lista de roles<br>disponibles para que seleccione que roles tienen privilegios de<br>ejecución de la extracción definida. |  |  |

<!-- Page 48 -->

HOJA 
48 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.3.3 EJECUTAR UN PROCESO DE EXTRACCIÓN 
 
La extracción permite generar un archivo de texto en formato .CVS, con la información de los 
diversos procesos que son registrados en el SICOP. 
 
Para generar las extracciones se debe seleccionar en el Menú Principal la opción de Extractor 
de Información y Ejecución.

Al ingresar en ejecución, aparece un listado de las extracciones habilitadas para el rol de la 
persona usuaria que ingresó.

Para ejecutar, damos clic sobre la extracción que sea de nuestro interés, después de 
seleccionarla se muestra la siguiente pantalla, en la que registran los parámetros obligatorios 
para la generación:

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 48 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 48 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 49 -->

HOJA 
49 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Los componentes de la pantalla indican lo siguiente: 
 
• 
Clave: corresponde a la nomenclatura de la extracción que se desea generar. 
• 
Nombre del archivo: colocar un nombre al archivo que se va a extraer (sin espacios, 
caracteres “raros”, no muy largo). 
• 
Tipo de archivo: seleccionar que sea .CSV. 
• 
Valor1: parámetro para el rango inicial a descargar. 
• 
Valor2: parámetro para el rango final a descargar. 
• 
Para ese ejemplo, se indica un rango de número de solicitudes a descargar. 
• 
Ejecutar: acción para iniciar la ejecución de la extracción, generando un número de ticket. 
• 
Ticket No.: corresponde al número asignado por el sistema al ejecutar la extracción, anotarlo 
para realizar la descarga posterior al dar clic en Aceptar.

Al dar clic en el botón Aceptar, nos regresa a la página donde se encuentra el listado de las

extracciones, por lo tanto, hay que dar clic en el botón 
 para ingresar a la opción 
“Estado de ticket”. 
 
• 
Número de ticket: colocar no. de ticket de la extracción (168512, sin la coma) 
• 
Dar clic en Aceptar (1). 
• 
Esperar a que indique TERMINADO (2) y aparezca la liga “azul rey” para descargar el archivo 
(3).

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 49 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 49 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 50 -->

HOJA 
50 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

• 
Abre una ventana donde pregunta “Abrir con” o “Guardar archivo”, la persona usuaria indicará 
la opción requerida y dará clic al botón “Aceptar” (4).

1

2

3

4

• 
Posteriormente la persona usuaria debe dar doble clic sobre el archivo.CSV (5) para abrir 
directo en EXCEL.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 50 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 50 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 51 -->

HOJA 
51 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.4 CONSULTAS

 
En esta carpeta se pueden visualizar dos opciones: Consulta General del Presupuesto. 
Muestra el estado del ejercicio de una clave presupuestaria. 
 
Consulta de Envío SIAFF – WEB.

4.4.1 CONSULTA GENERAL DEL PRESUPUESTO 
 
Se presenta a manera de ejemplo los pasos para la ejecución de la consulta General del 
Presupuesto. Al dar clic a la consulta el sistema presenta la pantalla “Consulta al presupuesto 
asignado”, en la parte superior de la pantalla se capturan los criterios de búsqueda y en la parte 
inferior se muestra el resultado.

En la parte superior de la pantalla, se solicita el Ramo el cual se presenta por default de acuerdo 
con el Ramo de la persona usuaria en sesión; la Unidad requerida y todos los componentes que 
forman la clave presupuestaria se presentan en forma de campos de captura (1). 
 
Así mismo, se debe capturar al menos un valor adicional a la cuenta para realizar la búsqueda. 
Si no selecciona clave de la cuenta, por default se asigna: A.2.1.04.06 - Disponible con trámite 
(2).

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 51 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 51 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 52 -->

HOJA 
52 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

2

1

Capturados los datos de búsqueda, dé clic en el botón “Buscar”. Se presenta en la parte media 
de la pantalla en la sección “Claves presupuestales” el resultado de la búsqueda. 
 
Al seleccionar el botón “Descripción EP” el sistema muestra la descripción de la clave 
presupuestal (3).

3

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 52 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 52 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 53 -->

HOJA 
53 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Después de haber generado las claves presupuestarias, se puede consultar desglose por mes, 
unidad, clave programática e importe mensual, basta con que elija en la lista de selección la 
cuenta (4) requerida para que la tabla de resultados (5) se actualice.

4

5

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 53 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 53 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 54 -->

HOJA 
54 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

Para generar la consulta, la persona usuaria debe dar clic en el botón “Certificación saldos” y el

sistema emite el siguiente reporte (en formato PDF) para descargar 
 o imprimir
, según se 
requiera.

Recuerde que únicamente puede ver la información a la cual tenga acceso según la configuración 
de su rol.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 54 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 54 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 55 -->

HOJA 
55 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.4.2 BOTONES PARA CONSULTA GENERAL DEL PRESUPUESTO

Botón 
Descripción

Borrar. Limpia los criterios de búsqueda agregados.

Buscar. Obtiene y muestra en la parte media de la pantalla las 
claves presupuestarias que estén dentro del nivel de consulta y 
filtros de la persona usuaria en sesión.

Descripción EP. Muestra una pantalla con el significado de cada 
uno de los elementos que conforman la clave presupuestaria 
seleccionada.

Certificación saldos. Muestra el reporte con los saldos de los 
diferentes momentos presupuestarios para la cuenta seleccionada. 
Se puede consultar, descargar o imprimir.

4.4.3 CONSULTA DE ENVÍO SIAFF – WEB 
 
Para consultar el envío correspondiente del documento a SIAFF, seleccione la opción de 
Consultas en su Menú Principal y dé clic a “Consulta Envío SIAFF – WEB”. 
 
El sistema muestra la pantalla “Envío SIAFF”, a través de la cual se puede consultar el estatus 
del envío del documento. La consulta se puede realizar ingresando el ticket de carga (1), número 
de proceso (2) o seleccionando el documento (3) que se requiere consultar, sin embargo, lo 
importante es indicar las fechas (4) en que se realizó la operación para que el sistema realice la 
búsqueda con los parámetros indicados.

1

2

3
4

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 55 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 55 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 55 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Borrar. Limpia los criterios de búsqueda agregados. |  |  |
|  |  |  | Buscar. Obtiene y muestra en la parte media de la pantalla las<br>claves presupuestarias que estén dentro del nivel de consulta y<br>filtros de la persona usuaria en sesión. |  |  |
|  |  |  | Descripción EP. Muestra una pantalla con el significado de cada<br>uno de los elementos que conforman la clave presupuestaria<br>seleccionada. |  |  |
|  |  |  | Certificación saldos. Muestra el reporte con los saldos de los<br>diferentes momentos presupuestarios para la cuenta seleccionada.<br>Se puede consultar, descargar o imprimir. |  |  |

<!-- Page 56 -->

HOJA 
56 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

En caso de no indicar las fechas se corre el riesgo de que la información que recupere el sistema 
no sea correcta, ya que el sistema por default establece los últimos 4 días hábiles y en caso de 
que la consulta no se ejecutara en ese periodo la respuesta puede ser errónea. 
 
Por ejemplo, si se requiere consultar un envío a SIAFF por proceso se ingresa el número (5), se 
selecciona el periodo en que se realizó el proceso (6) y se da clic en el botón “Buscar” (7).

El sistema muestra el documento que se requiere consultar, dar clic en el botón 
 (8) y el 
sistema despliega el detalle de la operación. Cuando en la sección “Estado” (9) se muestra la 
leyenda “…, estado: COPIADO A OPERACIÓN” indica que el envío fue exitoso.

7

5 
6

8

9

La ventana de “Detalle” muestra los siguientes datos: ticket de carga cuando la búsqueda del 
envío al SIAFF se realice con ese número, fecha de envío indica la fecha y hora en que se realizó 
el envío, número del Ramo y de unidad, cuando la consulte se realice con número de proceso, 
documento consultado, folio de la operación, estado del envío y en su caso errores. 
 
 
Cuando el sistema muestre en la ventana de “Detalle”, en la sección de “Errores” información, 
significa que el envío no se realizó e indica el motivo (10). Para el presente ejemplo, el error 
especifica que la fecha propuesta de pago no se capturó en el documento y es un campo 
requerido (11).

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 56 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 56 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 57 -->

HOJA 
57 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

11

10

Por otra parte, es importante mencionar que corresponde al o la configurador(a) del Ramo 
asignar los permisos a la persona usuaria para utilizar esta consulta.

4.4.4 BOTONES PARA CONSULTA EL ENVÍO SIAFF - WEB

Botón 
Descripción

Borrar. Limpia los criterios de búsqueda agregados. La 
persona usuaria debe dar clic en el botón para borrar los 
registros.

Buscar. Realiza búsqueda de la consulta del documento 
enviado a SIAFF conforme a los criterios solicitados. La 
persona usuaria debe dar clic en el botón para solicitar la 
consulta.

Actualiza información. Permite refrescar la información de 
los registros. La persona usuaria debe dar clic en el botón 
para actualizar la información.

Consulta de detalle. Muestra el detalle del documento 
enviado a SIAFF, el mensaje puede ser exitoso o erróneo. La 
persona usuaria debe dar clic en el botón para obtener el 
detalle de la consulta.

Aceptar. Cierra el detalle de la consulta.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 57 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 57 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 57 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Borrar. Limpia los criterios de búsqueda agregados. La<br>persona usuaria debe dar clic en el botón para borrar los<br>registros. |  |  |
|  |  |  | Buscar. Realiza búsqueda de la consulta del documento<br>enviado a SIAFF conforme a los criterios solicitados. La<br>persona usuaria debe dar clic en el botón para solicitar la<br>consulta. |  |  |
|  |  |  | Actualiza información. Permite refrescar la información de<br>los registros. La persona usuaria debe dar clic en el botón<br>para actualizar la información. |  |  |
|  |  |  | Consulta de detalle. Muestra el detalle del documento<br>enviado a SIAFF, el mensaje puede ser exitoso o erróneo. La<br>persona usuaria debe dar clic en el botón para obtener el<br>detalle de la consulta. |  |  |
|  |  |  | Aceptar. Cierra el detalle de la consulta. |  |  |

<!-- Page 58 -->

HOJA 
58 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.5 CONFIGURADOR(A)

Las actividades para la funcionalidad de “Configurador” son las siguientes: 
 
• 
Solicitar a la UCG los formatos actualizados de la Carta Responsiva para el Configurador 
del Sistema de Contabilidad y Presupuesto (Ejemplo 1) y la Carta Responsiva para la 
Persona Usuaria del Sistema de Contabilidad y Presupuesto (Ejemplo 2). 
• 
Requisitar y enviar escaneada a la UCG la Carta Responsiva para el Configurador del 
Sistema de Contabilidad y Presupuesto (Ejemplo 1). 
• 
Administrar a las personas usuarias del SICOP (alta, baja o modificación a los privilegios del 
sistema). 
• 
Proporcionar, recabar y resguardar la Carta Responsiva para la Persona Usuaria del Sistema 
de Contabilidad y Presupuesto (Ejemplo 2) de las personas usuarias que registren, en 
conjunto con el formato que manejen para la administración de usuarios del SICOP. 
• 
Actualizar o depurar los catálogos del SICOP para el Ramo (no centrales). 
• 
Configuración de la cobertura operativa, nivel de consulta, perfiles y roles. 
• 
Asesorar a las personas usuarias del SICOP para la operación de los flujos de trabajo. 
• 
Primer filtro del Ramo ante una inconsistencia del sistema. 
• 
Preparación de la instancia antes de comenzar un Ejercicio Fiscal:

• 
Catálogos de relación para la clave presupuestaria oficial. 
• 
Catálogos locales para el manejo de clave ampliada. 
• 
Carga y aplicación del Presupuesto Aprobado (esta actividad se encuentra en 
conjunto con el área de presupuesto). 
• 
Depuración del catálogo de usuarios. 
• 
Activación de usuarios. 
• 
Apertura oficial de la instancia para el inicio de las operaciones (esta actividad se 
encuentra en conjunto con el área de presupuesto).

• 
En algunos Ramos, son los encargados de dar seguimiento a las incidencias registradas en 
la Mesa de Ayuda a Soluciones. 
• 
Fungir como enlace de temas referentes a SICOP ante la UCG.

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 58 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 58 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 59 -->

HOJA 
59 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.5.1 EJEMPLO 1

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 59 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 59 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

<!-- Page 60 -->

HOJA 
60 DE 60

Secretaría de Hacienda y Crédito Público 
Unidad de Contabilidad Gubernamental

FECHA 
ACTUALIZACIÓN 
01/01/2025

MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP)

4.5.2 EJEMPLO 2

El presente manual es para uso exclusivo de los usuarios del Sistema de Contabilidad y Presupuesto.

### Tabla — página 60 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 60 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |


## Tablas Auxiliares


### Tabla — página 2 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 2 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 3 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 3 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 4 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 4 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 5 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 5 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 6 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 6 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 7 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 7 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 8 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 8 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 9 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 9 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | ------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 10 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 10 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 11 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 11 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 12 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 12 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 13 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 13 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 14 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 14 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 15 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 15 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 16 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 16 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 17 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 17 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 17 (vía pdfplumber)

|  | Nombre |  |  | Descripción |  |
| - | ------ | - | - | ----------- | - |
| Componente |  |  | Es un campo de captura, que puede derivar de un catálogo, fecha,<br>selección de valores o texto.<br>Ejemplo:<br>Concepto<br>La persona usuaria debe capturar el concepto en relación al flujo de trabajo. |  |  |
| * |  |  | Significa que el dato es obligatorio. |  |  |
| Encabezado |  |  | Sección que permite realizar el registro general de información. Los<br>componentes que corresponden al encabezado. (1) |  |  |
| Filtros |  |  | Sección que funciona como un buscador de datos para facilitar el llenado<br>de la sección Multilínea. (2) |  |  |
| Multilínea |  |  | Sección que permite visualizar el detalle de las claves presupuestarias,<br>según los criterios colocados en los filtros. (3) |  |  |

### Tabla — página 18 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 18 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 18 (vía pdfplumber)

|  | Botones/Encabezado |  |  | Descripción |  |
| - | ------------------ | - | - | ----------- | - |
|  |  |  | Fechas. Para incorporar la fecha requerida (Inicial, final,<br>etc.), dar clic en el triángulo invertido y se muestra el<br>calendario del mes actual permitiendo cambiarlo de mes<br>con flechas adelante-atrás y seleccionar el día. (1) |  |  |
|  |  |  | Componentes con lista de valores predefinidos. Al dar<br>clic al triángulo invertido, se muestra una lista de selección<br>(combo box) con los valores permitidos para el campo. No<br>es posible capturar algún otro valor. (2) |  |  |
|  |  |  | Componentes con valores por default. Al abrir un<br>documento es probable que aparezcan datos pre-<br>capturados, esto es porque:<br> Son valores asignados por default que siempre<br>van asociados al documento.<br> Se ejecutó un proceso previo al abrir el<br>documento que los llenó. |  |  |
| * |  |  | Componentes obligatorios. Los componentes del<br>encabezado que tengan un asterisco a la izquierda deben<br>capturarse para poder avanzar. |  |  |
|  |  |  | Texto de ayuda. En la parte superior de la pantalla del<br>documento (debajo de los íconos) se presenta un renglón<br>con fondo amarillo en el cual se muestra la ayuda asociada<br>a cada componente, indicando el significado de éste. La<br>persona usuaria debe colocarse en el componente<br>requerido y el sistema en la parte superior define la ayuda.<br>(3) |  |  |

### Tabla — página 19 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 19 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 19 (vía pdfplumber)

|  | Botones/Encabezado |  |  | Descripción |  |
| - | ------------------ | - | - | ----------- | - |
|  |  |  | Ventana de catálogo. Para algunos componentes del se<br>muestra el ícono con una lupa a la derecha, significa que<br>abren un “submenú” para poder seleccionar la opción que<br>debe capturarse. Dar clic en el ícono para que se<br>desplieguen los datos del catálogo. Seleccionar el dato<br>deseado y dar clic en el botón aceptar. (4) |  |  |

### Tabla — página 20 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 20 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 20 (vía pdfplumber)

|  | Botones /Multilínea |  |  | Descripción |  |
| - | ------------------- | - | - | ----------- | - |
|  |  |  | Selecciona los registros. Permite seleccionar toda la<br>información que se encuentren en el multilínea. La persona<br>usuaria debe dar clic en el botón y el sistema selecciona<br>toda la información (1). Para seleccionar / quitar una o más<br>líneas dar clic en el recuadro de lado izquierdo del<br>multilínea, como se muestra en el siguiente ejemplo. |  |  |
|  |  |  | Actualiza información. Permite refrescar la información<br>del multilínea. La persona usuaria debe dar clic en el botón<br>para actualizar la información en el multilínea. |  |  |
|  |  |  | Borra información. Elimina reglón seleccionado en el<br>multilínea. La persona usuaria debe dar clic en el botón<br>para borrar la información previamente seleccionada en el<br>multilínea. |  |  |
|  |  |  | Edita los registros. Permite editar el renglón del<br>multilínea. La persona usuaria debe seleccionar el<br>elemento que requiere modificar y en el momento se<br>encuentre resaltado en azul, dar clic en el botón para<br>realizar los cambios, se muestra la ventana de captura.<br>Ver imagen (2). |  |  |
|  |  |  | Copiar. Copia reglón seleccionado en el multilínea.<br>Seleccione el renglón del detalle a copiar, dando clic en el<br>recuadro que aparece a la izquierda del registro.<br>Oprima el botón para copiar, se mostrará el renglón<br>copiado al final del multilínea. Ver imagen (3). |  |  |

### Tabla — página 21 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 21 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 21 (vía pdfplumber)

|  | Botones /Multilínea |  |  | Descripción |  |
| - | ------------------- | - | - | ----------- | - |
|  |  |  | Busca información. Realiza la búsqueda de la<br>información con los criterios insertados en los filtros,<br>cerrando el proceso y no permitiendo el acceso hasta<br>que la información se encuentre completa. La persona<br>usuaria debe dar clic en el botón para obtener la<br>información requerida en el multilínea, una vez<br>establecidos los criterios de búsqueda en los filtros. El<br>sistema envía el siguiente mensaje, dar clic al botón<br>aceptar.<br>M ensaje de S istem a |  |  |
|  |  |  | Busca información. Realiza la búsqueda de la<br>información con los criterios insertados en los filtros,<br>buscando la información en el momento sin cerrar el<br>proceso. Al dar clic en este botón se recuperan los<br>registros en el multilínea con datos indicados en los filtros,<br>delimitando la búsqueda. El sistema envía el siguiente<br>mensaje.<br>E s p e re m ie s n tra s s e eje c u ta el s ig u ie n te p ro c es o ... |  |  |

### Tabla — página 22 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 22 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 23 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 23 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 24 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 24 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 24 (vía pdfplumber)

| Botón | Descripción |
| ----- | ----------- |
|  | Regresa al menú principal. Regresa al menú inicial del<br>sistema, al dar clic al botón. Si capturó/modificó datos y no los<br>guardó pide confirmación para salir. |
|  | Regresa al menú anterior. Cierra la pantalla del documento<br>al dar clic y muestra nuevamente la pantalla anterior. En caso<br>de captura o cambio, el sistema solicita confirmación antes de<br>salir. Los datos no guardados se pierden. |
|  | Valida campos requeridos. Verifica que los datos<br>obligatorios de los componentes hayan sido capturados o<br>seleccionados del catálogo correspondiente, mostrando la<br>lista de datos faltantes e indicando si pertenecen al<br>encabezado o al multilínea.<br>El documento no avanza al siguiente paso mientras no se<br>capturen todos los datos obligatorios. |
|  | Guarda captura/cambios. Válida y guarda los datos<br>capturados/modificados. Además de validar, guarda cambios<br>capturados, en su caso, señala omisiones de captura<br>obligatoria. |
|  | Valida datos. Valida datos de la pantalla y cálculo de<br>fórmulas (reglas) asociadas al documento. Al ejecutar está<br>acción el sistema guarda los datos capturados y regresa a la<br>pantalla anterior. Para avanzar el documento es necesario<br>volver a ingresar y en caso de que existan errores el sistema<br>los muestra. |
|  | Envía a ... Envía el documento al siguiente paso; por ejemplo:<br>de captura a revisor o de revisor a autorizador<br>. |

### Tabla — página 25 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 25 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 25 (vía pdfplumber)

| Botón | Descripción |
| ----- | ----------- |
|  | Suspende. Al suspender el proceso no continúa y la acción<br>solo aplica cuando el proceso aún no tiene afectación<br>presupuestaria. |
|  | Informe de captura. Presenta un reporte de la captura<br>realizada, al dar clic. Así mismo, se puede descargar o<br>imprimir. |
|  | Adjunta documentos. Al dar clic el sistema muestra la ruta<br>para adjuntar el archivo y permite agregar información del<br>archivo anexo.<br>A rch ivo s a d ju n to s |

### Tabla — página 26 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 26 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 27 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 27 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 28 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 28 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 29 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 29 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 29 (vía pdfplumber)

| Botón | Descripción |
| ----- | ----------- |
|  | Regresa al menú anterior. Cierra la pantalla del catálogo, al dar clic y muestra<br>nuevamente la pantalla anterior. Si capturó/modificó datos y no los guardó, el<br>sistema pide confirmación para salir. Los datos no guardados se pierden. |
|  | Guarda captura/cambios. Valida y guarda los datos capturados/modificados.<br>Además de validar, guarda cambios capturados, en su caso, señala omisiones<br>de captura obligatoria. |
|  | Filtra. Filtra la información utilizando uno o más criterios de búsqueda. |
|  | Selecciona los componentes. Permite seleccionar toda la información que se<br>encuentren en el catálogo. La persona usuaria debe dar clic en el botón y el<br>sistema selecciona toda la información. Para seleccionar / quitar una o más<br>líneas dar clic en el recuadro de lado izquierdo del catálogo, como se muestra<br>en el siguiente ejemplo. |
|  | Actualiza información. Permite refrescar la información de los registros. La<br>persona usuaria debe dar clic en el botón para actualizar la información. |
|  | Agrega. Permite a la persona usuaria la captura de un nuevo registro. El<br>sistema despliega la pantalla para captura de datos. |
|  | Borra información. Elimina renglón seleccionado en el catálogo. La persona<br>usuaria debe dar clic en el botón para borrar la información previamente<br>seleccionada en los registros. |
|  | Edita los registros. Permite editar el renglón del catálogo. La persona usuaria<br>debe seleccionar el elemento que requiere editar y en el momento que se<br>encuentre resaltado en azul, dar clic en el botón para acceder realizar los<br>cambios. |
|  | Copiar. Copia el renglón seleccionado en el catálogo. La persona usuaria debe<br>seleccionar el renglón a copiar, dando clic en el recuadro que aparece a la<br>izquierda del registro, posteriormente dar clic en el botón para copiar y el<br>sistema muestra el renglón copiado al final de los registros. |

### Tabla — página 30 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 30 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 31 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 31 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 32 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 32 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 33 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 33 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 34 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 34 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 35 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 35 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 35 (vía pdfplumber)

|  | Estado |  |  | Descripción |  |
| - | ------ | - | - | ----------- | - |
| En proceso |  |  | Indica que el archivo aún se está validando. Debe consultar nuevamente<br>su estado. |  |  |
| Terminado |  |  | Indica que el archivo se terminó de validar, que los datos fueron correctos<br>y que puede proceder con la copia de los datos hacia las tablas de<br>operación. |  |  |
| Terminado con<br>Errores |  |  | Indica que el archivo se validó y se muestran en la pantalla la lista de<br>errores.<br>En caso de error, debe corregir su archivo de datos e iniciar un nuevo<br>proceso de carga (un nuevo ticket). |  |  |

### Tabla — página 36 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 36 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 37 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 37 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 38 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 38 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 38 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Enviar consulta. Abre el reporte con los parámetros solicitados, en<br>formato PDF. |  |  |
|  |  |  | Restablecer. Limpia los parámetros modificados, por los que arroja<br>el sistema por default. |  |  |

### Tabla — página 39 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 39 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 40 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 40 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 41 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 41 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 41 (vía pdfplumber)

| Etiqueta | Descripción |
| -------- | ----------- |
| Clave | Es una clave única que identifica a la extracción. |
| Descripción | Es la definición de manera general de la extracción. |
| Documento/saldos/movimientos | Muestra el nombre del documento. |
| Estado | Los estados posibles son:<br>1) En definición: es posible modificar/copiar/borrar.<br>2) Liberado: la extracción ya se encuentra en uso por algún<br>rol y no es posible modificarlo.<br>3) Suspendido: la extracción ya no está siendo usada, pero<br>tampoco es posible modificarla ni borrarla, dado que ya<br>existe registro de su uso. |

### Tabla — página 42 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 42 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 43 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 43 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 43 (vía pdfplumber)

| Etiqueta | Descripción |
| -------- | ----------- |
| Conector | Seleccionar el conector (AND u OR). Es obligatorio seleccionar como conector<br>para la primera condición la palabra AND. |
| Componente | Seleccionar el componente que se va a condicionar, se muestra una lista de<br>los componentes del documento/saldos/movimientos. |
| Operador | Seleccionar el operador de la lista. Los operadores disponibles son:<br>> mayor que<br>>= mayor igual que<br>< menor que<br><= menor igual que<br>= Igual |

### Tabla — página 44 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 44 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 44 (vía pdfplumber)

| Etiqueta | Descripción |
| -------- | ----------- |
|  | != diferente<br>Like que contenga<br>Not like que no contenga<br>Between entre<br>Not betwen que no esté entre<br>In que esté en la lista<br>Not in que no esté en la lista |
| Valor 1<br>Valor 2 | Proporcionar el valor para la condición.<br>1) Para el caso de like y not like, la persona usuaria debe poner el valor<br>encerrado entre apóstrofes y el “%” donde lo requiera. Ejemplo: ‘%ABC’<br>o ‘ABC%’ o ‘A%B%C’.<br>2) Para el caso de between y not between se tiene que proporcionar un<br>valor inicial y uno final.<br>3) Para el caso de in y not in se tiene que proporcionar la lista de valores.<br>La persona usuaria debe poner los apóstrofes que encierren cada valor<br>y las comas de separación cuando se trate de valores tipo fecha o<br>caracteres alfanuméricos. Ejemplo: ‘valor1’, ‘valor2’, ‘valor3’.<br>4) La persona usuaria también debe poner las fechas en formato correcto<br>“dd/mm/yyyy”.<br>5) Para el caso que una condición se quiera dejar con un valor variable el<br>cual sea solicitado al momento de ejecución de la extracción, se debe<br>poner únicamente el carácter “?” en el campo del valor. |
| ( ) | Es posible poner paréntesis de apertura y cierre para agrupar las condiciones<br>según la prioridad en que se requiera se ejecuten. |

### Tabla — página 45 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 45 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 46 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 46 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 47 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 47 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 47 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Nuevo. Crea una nueva plantilla de extracción de información. |  |  |
|  |  |  | Copiar. Permite copiar la configuración de la extracción que se<br>tenga en pantalla a otra extracción con diferente nombre. Para<br>realizar la copia es necesario que la extracción se encuentre en<br>estatus LIBERADO. La copia queda en estatus EN DEFINICIÓN. |  |  |
|  |  |  | Borrar. Permite eliminar la extracción que se tenga en pantalla,<br>previa confirmación. |  |  |
|  |  |  | Suspender. Cambia el estatus de la extracción a SUSPENDIDO,<br>para lo cual el estatus original debe ser LIBERADO. Una vez que<br>se suspende la extracción ya no se puede ejecutar. |  |  |
|  |  |  | Validar. Arma la consulta con todos los datos capturados y la<br>ejecuta en la base de datos para verificar que es correcta, cualquier<br>error que se presente se muestra en pantalla. |  |  |
|  |  |  | Guardar. Almacena la configuración realizada en la extracción, aun<br>cuando tenga errores de validación. El estatus es EN DEFINICIÓN.<br>Cuando se encuentra EN DEFINICIÓN, no se puede ejecutar. |  |  |
|  |  |  | Liberar. Valida y guarda la configuración realizada, si existen<br>errores los presenta en pantalla; pero si no hay errores le cambia el<br>estatus a LIBERADO a la extracción y ya no se puede realizar<br>cambios, además se presenta una pantalla con la lista de roles<br>disponibles para que seleccione que roles tienen privilegios de<br>ejecución de la extracción definida. |  |  |

### Tabla — página 48 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 48 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 49 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 49 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 50 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 50 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 51 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 51 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 52 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 52 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 53 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 53 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 54 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 54 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 55 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 55 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 55 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Borrar. Limpia los criterios de búsqueda agregados. |  |  |
|  |  |  | Buscar. Obtiene y muestra en la parte media de la pantalla las<br>claves presupuestarias que estén dentro del nivel de consulta y<br>filtros de la persona usuaria en sesión. |  |  |
|  |  |  | Descripción EP. Muestra una pantalla con el significado de cada<br>uno de los elementos que conforman la clave presupuestaria<br>seleccionada. |  |  |
|  |  |  | Certificación saldos. Muestra el reporte con los saldos de los<br>diferentes momentos presupuestarios para la cuenta seleccionada.<br>Se puede consultar, descargar o imprimir. |  |  |

### Tabla — página 56 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 56 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 57 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 57 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 57 (vía pdfplumber)

|  | Botón |  |  | Descripción |  |
| - | ----- | - | - | ----------- | - |
|  |  |  | Borrar. Limpia los criterios de búsqueda agregados. La<br>persona usuaria debe dar clic en el botón para borrar los<br>registros. |  |  |
|  |  |  | Buscar. Realiza búsqueda de la consulta del documento<br>enviado a SIAFF conforme a los criterios solicitados. La<br>persona usuaria debe dar clic en el botón para solicitar la<br>consulta. |  |  |
|  |  |  | Actualiza información. Permite refrescar la información de<br>los registros. La persona usuaria debe dar clic en el botón<br>para actualizar la información. |  |  |
|  |  |  | Consulta de detalle. Muestra el detalle del documento<br>enviado a SIAFF, el mensaje puede ser exitoso o erróneo. La<br>persona usuaria debe dar clic en el botón para obtener el<br>detalle de la consulta. |  |  |
|  |  |  | Aceptar. Cierra el detalle de la consulta. |  |  |

### Tabla — página 58 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 58 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 59 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 59 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |

### Tabla — página 60 (vía pdfplumber)

|  | Secretaría de Hacienda y Crédito Público<br>Unidad de Contabilidad Gubernamental | HOJA | 60 DE 60 |
| - | -------------------------------------------------------------------------------- | ---- | -------- |
|  |  | FECHA<br>ACTUALIZACIÓN | 01/01/2025 |
|  | MANUAL DE USUARIO DEL SISTEMA DE CONTABILIDAD Y PRESUPUESTO (SICOP) |  |  |