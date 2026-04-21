---
source: 59-Manual de Usuario_IT_Centros_Procedimiento de Compras.pdf
pages: 22
file_size_mb: 5.94
extraction_date: "2026-04-21T21:55:05.092858+00:00"
language: es
tables_found: 0
has_images: true
has_scanned_pages: false
features_used: ["text_fast"]
extraction_time_sec: 2.25
quality_score: 92.0
quality_label: "excellent"
is_valid: true
from_cache: false
warnings: ["camelot-py not installed; tables_camelot skipped", "tabula-py not installed; tables_tabula skipped"]
---
<!-- Page 1 -->

TECNOLÓGICO NACIONAL DE MÉXICO

Sistema de Administración

Manual de Usuario

Procedimiento de Compras

ç

<!-- Page 2 -->

SISAD

Índice

1. 
Introducción ........................................................................................................................................ 3

2. 
Acceso al Sistema .............................................................................................................................. 4

3. 
Área del IT/Centro ............................................................................................................................... 5

4. 
Requisición ......................................................................................................................................... 5

4.1 
Elaboración de Requisición ........................................................................................................... 5

4.2 
Envió de Requisición ..................................................................................................................... 8

4.3 
Seguimiento de Requisición .......................................................................................................... 9

5. 
Orden de Compra ............................................................................................................................. 10

5.1 
Elaboración de Orden de Compra ............................................................................................... 10

5.2 
Envió de la Orden de Compra ..................................................................................................... 13

5.3 
Abrir Orden de Compra ............................................................................................................... 14

6. 
Entrada y Salida Simultánea de Almacén ...................................................................................... 14

6.1 
Elaboración de Entrada y Salida simultánea de Almacén ........................................................... 14

6.2 
Envió de la Entrada y Salida Simultánea de Almacén ................................................................ 17

6.3 
Abrir Entrada y Salida Simultánea de Almacén ........................................................................... 18

7. 
Liberación Servicios ......................................................................................................................... 18

7.1 
Captura de Servicios ................................................................................................................... 18

7.2 
Envió del Servicios ...................................................................................................................... 21

7.3 
Abrir Servicios ............................................................................................................................. 22

Página 2 de 22

<!-- Page 3 -->

SISAD

Manual de Usuario

1. Introducción

El Sistema Integral de Planeación, ha solucionado la problemática que se tenía en la Planeación, 
Programación y Control del Ejercicio Presupuestal en los IT/Centros, los cuales actualmente se encuentran 
gestionados en este sistema.

Actualmente en diversos institutos del país se han hecho esfuerzos por solucionar esta problemática 
atacándola desde diferentes puntos de vista, propiciando que las diferentes soluciones que se han 
desarrollado tengan diversas plataformas de desarrollo provocando la subutilización de recursos, así como 
de la infraestructura de telecomunicaciones con la que cuentan los Institutos Tecnológicos; con este 
sistema se ha homogenizado esta plataforma de desarrollo teniendo con esto una gran trasparencia entre 
las aplicaciones que se desarrollan y así poder optimizar el uso de los recursos de TIC´s.

Como generador, operador y/o compilador de la información que se genera en los diferentes 
departamentos de los IT/Centros se detectó la urgente necesidad de realizar este proyecto cuyo resultado 
es eficientar los tiempos de trabajo de las diversas tareas las cuales generan información que hay que 
presentar de diferente manera para diferentes organismos que la solicitan.

En el marco de la planeación estratégica, en específico en lo concerniente a la modernización de los 
procesos sustantivos y adjetivos, se otorga al Tecnológico Nacional de México una Licencia sin costo para 
la utilización del SIPlan, el cual operan bajo el nombre de SISAD.

El mencionado sistema cuenta con la habilitación de los siguientes módulos que son sujetos a revisiones 
y adecuaciones.

Programa de Trabajo Anual (PTA)

Captura de PTA 
Seguimiento de PTA 
Carga de POA

Adecuaciones Presupuestales 
Requisiciones 
Viáticos 
 
Captura de Viáticos 
 
Comprobación de Viáticos 
Compras 
 
Orden de Compras 
 
Entrada y Salida Simultánea de Almacén 
Servicios 
 
Solicitud de Pago 
Procedimiento Capítulo 1000 
Procedimiento Partida 33401 
Procedimiento Partidas de Mantenimiento 
Subpresupuestos 
Reportes 
Evaluación Programática Presupuestal 
Estructura Educativa 
 
 
 
Este sistema aplica para los Institutos Tecnológicos Federales y Centros del Tecnológico Nacional de 
México (TecNM).

Página 3 de 22

<!-- Page 4 -->

SISAD

2. Acceso al Sistema

El sistema se encuentra alojado en un servidor del TecNM, al cual accedemos con la siguiente dirección 
de Internet (url):

https://administracion2.tecnm.mx/

Al darle Enter se nos desplegará una pantalla que nos pedirá seleccionar el Año al que se requiere acceder, 
como se muestra a continuación:

Al darle Click en el año se nos desplegará una pantalla que nos pedirá un Usuario, Contraseña, así como 
Ingresar el Código dentro de la Imagen, como se muestra a continuación, después deberá dar Click en 
validar para poder acceder al sistema:

Este Usuario y Contraseña son proporcionados previamente por el Administrador Local del IT/Centro.

Página 4 de 22

<!-- Page 5 -->

SISAD

3. Área del IT/Centro

El Área del IT/Centro deberán verificar que en la parte superior esté direccionado al Año y Origen de 
Recurso del cual requieren realizar dicho procedimiento.

En el caso de no encontrarse ubicado en los requeridos se dirigen a la pestaña del Menú Principal 
Utilerías -> Cambio de Año para seleccionar la opción requerida.

Origen del Recurso 
Año

4. Requisición

4.1 Elaboración de Requisición 
 
El Área del IT/Centro que requiera realizar una Requisición de Capítulo 2000 ó 3000 deberá acceder al 
Menú principal en Áreas/Operación-> Requisición -> Capturar Requisición como se visualiza en la 
siguiente pantalla. 
 
 
 
 
 
 
 
 
 
 
 
Para el Ejemplo de Requisición se utilizará la Partida 21401.

Página 5 de 22

<!-- Page 6 -->

SISAD

En está pantalla visualizará las requisiciones elaboradas previamente en caso de existir, así como su 
estatus de Autorización y avance de procedimientos en las áreas correspondientes en las columnas de 
PPP hasta RF.

Deberá dar Click en Insertar para iniciar el proceso de Requisición.

Folio: El sistema lo otorga de manera consecutiva por área, la cual se conforma por:

Origen del Recurso / Abreviatura del Área / Año Fiscal / Folio consecutivo

Ejemplo: IP/DPPP/2022/0001 
Fecha de Creación: El sistema asignará la fecha correspondiente al día en que sea insertada la 
requisición y no podrá ser editada, lo anterior debido a la cronología de fechas que debe guardar los 
procesos. 
Fecha de Solicitud: Fecha en que requieren la utilización de los recursos institucionales para realizar la 
solicitud de viáticos. 
Justificación: En este apartado deberán justificar el uso de los recursos los cuales impactan al 
cumplimiento de los indicadores institucionales.

Ejemplo: Se requiere para llevar a cabo la impresión de documentos oficiales emitidos por 
el Departamento de Planeación.

Quedando de la siguiente manera, al concluir la captura deberá dar Click en Guardar para regresarnos 
a la pantalla de Capturar Requisición.

Página 6 de 22

<!-- Page 7 -->

SISAD

En caso de requerir Editar dar Click en el ícono del 
 y en el ícono de 
 
para eliminar la Requisición, siempre y cuando no exista una captura posterior. 
 
Seguidamente daremos Click en Bienes o Servicios para poder insertar la Partida 
correspondiente al recurso solicitado y obtendremos la siguiente pantalla, en la 
cual deberá de dar Click en Insertar.

Se apertura el siguiente formulario para realizar la captura de los datos que intervienen en el uso de las 
Partidas del Capítulo 2000.

Acción: Deberá seleccionar la Acción Institucional que contenga los recursos para el Ejercicio del 
Capítulo 2000. 
Artículo: Seleccione el Articulo correspondiente a la partida que requiera ejercer, podrá filtrar escribiendo 
el nombre del Artículo en el espacio que permite escritura a un costado del ícono Filtrar. 
Los Artículos requeridos en las partidas correspondientes deben estar Activos en el Catalogó de 
Artículos (Bienes o Servicios) del IT/Centro, el cual puede visualizarse en el Menú Catálogos->Artículos. 
En caso de estar Inactivo o no existente deberá solicitar al área de Recursos Materiales y Servicios su 
habilitación. 
Unidad de Medida: Se llenan automáticamente al seleccionar el Artículo. 
Partida: Se llenan automáticamente al seleccionar el Artículo. 
Monto Disponible: Este campo permite visualizar el recurso disponible de su POA en la acción y partida 
seleccionada. 
Cantidad: Deberá escribir el número que corresponda.

Página 7 de 22

<!-- Page 8 -->

SISAD

Precio Unitario: Deberá capturar el Precio Unitario del Artículo. 
Monto: El sistema hace el cálculo multiplicando el campo de cantidad por el Precio Unitario.

Se refleja el llenado del formulario de la siguiente manera, para lo cual se requiere dar Click en Guardar 
a la información capturada.

Seguidamente podrá visualizar la siguiente pantalla, en el cual podrá aún editar en el ícono del 
 y en 
el ícono de 
 eliminar el artículo añadido en caso de haberse insertado erróneamente.

4.2 Envió de Requisición 
 
En caso de estar correcta la captura de información, deberá dar Click en Enviar para que la Requisición 
inicie su proceso de validación por las Áreas Autorizadas del IT/Centro.

Aparecerá en pantalla el siguiente aviso al cual deberá dar Click en Enviar, y ya no podrá realizar 
modificaciones a la requisición.

Página 8 de 22

<!-- Page 9 -->

SISAD

Seguidamente podrá visualizar la siguiente pantalla una vez enviada la requisición para Autorización. Las 
requisiciones que se elaboren desde los usuarios de las Subdirecciones y Dirección del plantel quedarán 
validadas en automático por su área al dar Click en Enviar, debido a que estás áreas son parte del 
procedimiento de Autorización.

4.3 Seguimiento de Requisición

En el caso que en la siguiente pantalla visualicen en las Columnas: (PPP), (Sup) ó (Dir) la palabra Obs, 
deberá sobreponer el cursor del mouse sobre dicha palabra para visualizar la observación y realizar la 
corrección solicitada dando Click en el ícono del 
 o en el ícono de Bienes y Servicios, según 
corresponda y volver a realizar el proceso de envió descrito en el punto 5.5. 
 
 
 
 
 
 
 
 
 
 
 
 
Una vez autorizada por las Áreas correspondientes podrán visualizar el ícono de Impresora para visualizar 
el formato imprimible de la requisición.

Página 9 de 22

<!-- Page 10 -->

SISAD

5. Orden de Compra

5.1 Elaboración de Orden de Compra

El Departamento de Recursos Materiales y Servicios del IT/Centro, al recibir una requisición autorizada 
para adquisición de bienes o servicios, deberá acceder al Menú principal en Áreas/Operación-> Compras 
-> Orden de Compra->Capturar Orden de Compra como se visualiza en la siguiente pantalla. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Se visualizará la siguiente pantalla, en la cual deberá dar Click en el botón Insertar. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Folio: El sistema lo otorga de manera consecutiva, la cual se conforma por:

Origen del Recurso / Año Fiscal / Folio consecutivo 
Ejemplo: IP / 2022 / 0001 
Fecha: Deberá seleccionar la fecha de Elaboración de la Orden de Compra, que deberá ser posterior a la 
fecha de elaboración de la requisición. 
Proveedor: Deberá seleccionar al Proveedor al que realizará la adquisición de los bienes y/o servicios. 
¿Desglose de Impuestos?: Deberá seleccionar Sí, en el caso que los bienes y/o servicios estén gravados 
por IVA ó selección No, en caso contrario. 
Comentario: Es un campo adicional para añadir información que el DRMyS considere relevante.

Página 10 de 22

<!-- Page 11 -->

SISAD

Al concluir con la captura deberá dar Click en el Botón Guardar para visualizar la pantalla principal de 
Captura Orden de Compra.

En la siguiente ventana podrá realizar las siguientes acciones.

En caso de requerir Editar dar Click en el ícono del 
 y en el ícono de 
 
para eliminar la Orden de Compra, siempre y cuando no exista una captura 
posterior. 
 
Deberá dar Click en el botón Bienes y/o Servicios para añadir la Requisición 
previamente autorizada a la Orden de Compra.

Deberá contar con la cotización previamente a este paso, en caso de 
no contar con el Techo Presupuestal suficiente en la Requisición, 
deberá solicitar su corrección. 
El monto presupuestal de la requisición debe ser igual o superior al 
costo de la adquisición de bienes y/o servicios. 
 
Se visualizará la siguiente pestaña para dar Click en Insertar. 
 
 
 
 
 
 
 
 
 
 
Deberá seleccionar el Área y número de la Requisición que requiere
 
añadir a la Orden de Compra dando Click en Ver Requisición.

Página 11 de 22

<!-- Page 12 -->

SISAD

En la siguiente pantalla deberá dar Click en Todos y seguidamente Click en Agregar.

En caso de existir dato en la Columna Orden de Compra significa que está 
requisición ya está relacionada con otra Orden de Compra, por lo cual no podrá 
añadirla en otra Orden de Compra. 
 
 
Se visualizará la pantalla principal de Captura Orden de Compra-Bienes o Servicios con los datos 
contenidos en la requisición añadida.

En caso de requerir Editar dar Click en el ícono del 
 y en el ícono de 
 
para eliminar la requisición añadida. 
 
Visualizará la siguiente pantalla para poder Editar los montos contenidos en la requisición hasta por el 
monto autorizado en la misma, al concluir la edición deberá dar Click en Guardar para regresar a la pantalla 
anterior y dar Click en Regresar.

Página 12 de 22

<!-- Page 13 -->

SISAD

Se visualizará la siguiente pantalla, en el ícono de Impresora podrá visualizar el formato de Orden de 
Compra.

5.2 
Envió de la Orden de Compra 
 
En la siguiente pantalla deberá dar Click en el botón de la columna RMS para proceder al envió de la 
Orden de Compra y continuar con el proceso de Entrada y Salida Simultánea de Almacén. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Después de haber confirmado el Envió de la Orden de Compra quedará inactiva para Edición.

Página 13 de 22

<!-- Page 14 -->

SISAD

5.3 Abrir Orden de Compra

El Departamento de Recursos Materiales y Servicios del IT/Centro, deberá acceder al Menú principal en 
Áreas/Operación-> Compras -> Orden de Compra->Abrir Orden de Compra como se visualiza en la 
siguiente pantalla. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
En la siguiente pantalla se visualizarán las Ordenes de Compra enviadas en el punto 5.2, deberá 
seleccionar la que requiera aperturar, la cual no debe estar relacionada aún con una Entrada y Salida 
Simultánea de Almacén. 
 
Al dar Click en Abrir podrá realizar el proceso que requiera, motivo por el cual se apertura.

6. Entrada y Salida Simultánea de Almacén

6.1 Elaboración de Entrada y Salida simultánea de Almacén 
 
El Departamento de Recursos Materiales y Servicios del IT/Centro, deberá acceder al Menú principal en 
Áreas/Operación-> Entrada/Salida Simultánea -> Captura Entrada/Salida Simultánea como se 
visualiza en la siguiente pantalla.

Página 14 de 22

<!-- Page 15 -->

SISAD

En la siguiente pantalla deberá dar Click en Insertar y proceder a la captura de los datos relacionados 
con el CFDI emitido por el Proveedor que le proporciono los Bienes. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Folio: El sistema lo otorga de manera consecutiva, la cual se conforma por:

Origen del Recurso / Año Fiscal / Folio consecutivo 
Ejemplo: IP / 2022 / 0001 
Fecha: Deberá seleccionar la fecha del CFDI emitido por la recepción de los Bienes. 
Área: Deberá seleccionar el Área que recibe los Bienes adquiridos. 
Orden de Compra: Deberá seleccionar la Orden de Compra correspondiente a la adquisición de los 
Bienes. 
Factura: Deberá capturar el Folio Interno o Folio Fiscal del CFDI. 
Tipo de Adquisición: Deberá seleccionar el que corresponda al proceso de adquisición elaborado. 
Código Predeterminado en Compranet: Solo aplica para el Tipo de Adquisición de Licitación Pública. 
Comentario: Es un campo adicional para añadir información que el DRMyS considere relevante.

Al concluir con la captura deberá dar Click en Guardar. 
 
 
 
 
 
 
 
 
 
 
En la siguiente podrá relacionar los datos de la Orden de Compra seleccionada anteriormente.

En caso de requerir Editar dar Click en el ícono del 
 y en el ícono de 
 
para eliminar la requisición añadida. 
 
Deberá dar Click en el botón Bienes y/o Servicios para añadir la Requisición 
previamente autorizada a la Orden de Compra.

Página 15 de 22

<!-- Page 16 -->

SISAD

En la siguiente pantalla, deberá dar Click en Insertar para visualizar los datos de la Orden de compra.

Deberá seleccionar los artículos de la Orden de compra para ser añadidos en la 
Entrada y Salida Simultánea de Almacén y seguidamente dar Click en Agregar. 
 
 
 
 
 
 
 
 
 
 
 
Visualizará la siguiente pantalla para poder Editar los montos contenidos hasta por el monto autorizado en 
la requisición, al concluir la edición deberá dar Click en Guardar para regresar a la pantalla anterior y dar 
Click en Regresar. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
En las Columnas PDF y XML deberá cargar el CFDI emitido por el Proveedor de los Bienes adquiridos. 
(El peso de cada archivo no deberá ser Mayor a 500 Kb)

Página 16 de 22

<!-- Page 17 -->

SISAD

6.2 Envió de la Entrada y Salida Simultánea de Almacén

En la siguiente pantalla deberá dar Click en el botón de la columna RMS para proceder al envió de la 
Orden de Compra y continuar con el proceso de Entrada y Salida Simultánea de Almacén. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Después de haber confirmado el Envió de la Entrada y Salida Simultánea de Almacén quedará inactiva 
para Edición, como se muestra a continuación: 
 
 
 
 
 
 
 
 
En el primer ícono de Impresora podrá 
visualizar el formato de Entrada y Salida 
Simultánea de Almacén.

En el segundo ícono de Impresora podrá visualizar el 
formato de Solicitud de Pago emitida por Departamento 
de Recursos Materiales y Servicios al Departamento de 
Recursos Financieros.

Página 17 de 22

<!-- Page 18 -->

SISAD

6.3 Abrir Entrada y Salida Simultánea de Almacén

El Departamento de Recursos Materiales y Servicios del IT/Centro, deberá acceder al Menú principal en 
Áreas/Operación-> Compras -> Entrada/ Salida Simultánea ->Abrir Entrada y Salida Simultánea 
como se visualiza en la siguiente pantalla. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
En la siguiente pantalla se visualizarán las Entradas y Salidas enviadas en el punto 6.2, deberá seleccionar 
la que requiera aperturar. 
 
Al dar Click en Abrir podrá realizar el proceso que requiera, motivo por el cual se apertura.

7. Liberación Servicios

7.1 Captura de Servicios 
 
Después de realizar los procedimientos de los puntos 5.1 y 5.2, el Departamento de Recursos Materiales 
y Servicios del IT/Centro, deberá acceder al Menú principal en Áreas/Operación-> Compras -> Servicios 
-> Capturar Servicios como se visualiza en la siguiente pantalla.

Página 18 de 22

<!-- Page 19 -->

SISAD

En la siguiente ventana deberá dar Click en Insertar para añadir los datos correspondientes al CFDI 
emitido por el Proveedor de Servicios, así como datos del Servicio realizado. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Folio: El sistema lo otorga de manera consecutiva, la cual se conforma por:

Origen del Recurso / Año Fiscal / Folio consecutivo 
Ejemplo: IP / 2022 / 0001 
Fecha: Deberá seleccionar la fecha del CFDI emitido por la recepción de los Bienes. 
Orden de Compra: Deberá seleccionar la Orden de Compra correspondiente a la contratación del servicio. 
Factura: Deberá capturar el Folio Interno o Folio Fiscal del CFDI. 
Tipo de Adquisición: Deberá seleccionar el que corresponda al proceso de adquisición elaborado. 
Código Predeterminado en Compranet: Solo aplica para el Tipo de Adquisición de Licitación Pública. 
Descripción: Deberá realizar la descripción detallada de los servicios prestados por el Proveedor. 
Incio: Deberá seleccionar la fecha de inicio del servicio, la cual deberá ser posterior a la Fecha de Orden 
de Compra. 
Termino: Deberá seleccionar la fecha de inicio del servicio, la cual deberá ser posterior a la Fecha de 
Orden de Compra. 
 
Al concluir deberá dar Click en el botón Guardar para visualizar posteriormente la pantalla de Captura 
Servicio.

En caso de requerir Editar dar Click en el ícono del 
 y en el ícono de 
 
para eliminar el registro, en caso de no existir registros posteriores. 
 
Deberá dar Click en el botón Bienes y/o Servicios para añadir la Requisición 
previamente autorizada a la Orden de Compra.

Página 19 de 22

<!-- Page 20 -->

SISAD

En la siguiente pantalla, deberá dar Click en Insertar para visualizar los datos de la Orden de compra.

Deberá seleccionar los artículos de la Orden de compra para ser añadidos en la 
Captura de Servicios y seguidamente dar Click en Agregar. 
 
 
 
 
 
 
 
 
 
 
Visualizará la siguiente pantalla para poder Editar los montos contenidos hasta por el monto autorizado en 
la requisición, al concluir la edición deberá dar Click en Guardar para regresar a la pantalla anterior y dar 
Click en Regresar. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
En las Columnas PDF y XML deberá cargar el CFDI emitido por el Proveedor de los Servicios adquiridos. 
(El peso de cada archivo no deberá ser Mayor a 500 Kb)

Página 20 de 22

<!-- Page 21 -->

SISAD

7.2 Envió del Servicios

En la siguiente pantalla deberá dar Click en el botón de la columna RMS para proceder al envió de la 
Orden de Compra y continuar con el proceso de Entrada y Salida Simultánea de Almacén. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
Después de haber confirmado el Envió del Servicio quedará inactiva para Edición, como se muestra a 
continuación: 
 
 
 
 
 
 
 
 
En el primer ícono de Impresora podrá 
visualizar el formato de Liberación de 
Servicio.

En el segundo ícono de Impresora podrá visualizar el 
formato de Solicitud de Pago emitida por Departamento 
de Recursos Materiales y Servicios al Departamento de 
Recursos Financieros.

Página 21 de 22

<!-- Page 22 -->

SISAD

7.3 Abrir Servicios

El Departamento de Recursos Materiales y Servicios del IT/Centro, deberá acceder al Menú principal en 
Áreas/Operación-> Compras -> Servicios ->Abrir Servicios como se visualiza en la siguiente pantalla. 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
En la siguiente pantalla se visualizarán las Entradas y Salidas enviadas en el punto 6.2, deberá seleccionar 
la que requiera aperturar. 
 
Al dar Click en Abrir podrá realizar el proceso que requiera, motivo por el cual se apertura.

Página 22 de 22