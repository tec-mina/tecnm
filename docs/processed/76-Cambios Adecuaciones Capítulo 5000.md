---
source: 76-Cambios Adecuaciones Capítulo 5000.pdf
pages: 7
file_size_mb: 0.47
extraction_date: "2026-04-21T16:41:01.048850+00:00"
language: unknown
tables_found: 0
has_images: true
has_scanned_pages: false
features_used: ["markdown_llm", "text_fast"]
extraction_time_sec: 7.1
quality_score: 97.0
quality_label: "excellent"
is_valid: true
from_cache: false
warnings: []
---
<!-- Page 1 -->

Cambios Adecuaciones Capítulo 5000

Liberación de Montos para transferir.

1.- 
Es 
necesario 
 
primero 
 
insertar 
el 
registro 
de 
la 
adecuación. 
POA/Operación/Adecuaciones, en el botón de insertar.

2.- Para poder transferir montos del capítulo 5000 primero se deberá liberar 
presupuesto 
 
del 
módulo 
de 
Partidas 
RestringiDAS 
Capítulo 
5000: 
POA/Operación/Restringidas/Partidas Restringidas Capítulo 5000.

En este apartado se encuentra la gestión de subpresupuestos. Hay dos opciones para 
liberar los montos a transferir:

• Eliminando todo el subpresupuesto, es decir se liberará el monto total 
asignado a la partida, área y acción del subpresupuesto y quedará libre para 
tranferirse al área, acción, partida que se requiera. Esto se realizará con el 
botón de eliminar (Tache rojo). Una vez eliminado, todo el monto del 
subpresupuesto estará disponible para transferencia.

<!-- Page 2 -->

# **Cambios Adecuaciones Capítulo 5000** 

## **Liberación de Montos para transferir.** 

1.Es necesario primero insertar el registro de la adecuación. POA/Operación/Adecuaciones, en el botón de insertar. 

2.- Para poder transferir montos del capítulo 5000 primero se deberá liberar presupuesto del módulo de Partidas RestringiDAS Capítulo 5000: POA/Operación/Restringidas/Partidas Restringidas Capítulo 5000. 

En este apartado se encuentra la gestión de subpresupuestos. Hay dos opciones para liberar los montos a transferir: 

- Eliminando todo el subpresupuesto, es decir se liberará el monto total asignado a la partida, área y acción del subpresupuesto y quedará libre para tranferirse al área, acción, partida que se requiera. Esto se realizará con el botón de eliminar (Tache rojo). Una vez eliminado, todo el monto del subpresupuesto estará disponible para transferencia.

<!-- Page 3 -->

- Editando el subpresupuesto con el botón de edición (Lápiz). En el apartado de edición se podrá editar el costo unitario y/o cantidad de artículos del subpresupuesto de tal forma de poder liberar monto para transferir según sea la necesidad. Es importante recalcar que no se podrá liberar más del disponible total del subpresupuesto considerando también las requisiciones ya realizadas, además el subpresupuesto deberá estar en estatus de captura. 

En el ejemplo anterior el Presupuesto disponible para el subpresupuesto es de 50,000, el cuál se está utilizando completamente en el subpresupuesto ya que se están adquiriendo 5 artículos de 10,000.00 cada uno. Si solo se requiere transferir una parte del subpresupuesto se deberá ajustar cantidad y/o costo unitario. Supongamos que solo se requieren 3 artículos, entonces se liberará un monto de 20,000.00 para transferir. Importante mencionar que debe de llenar todos los campos en rojo, incluyuendo fecha propuesta de adquisición para que les permita guardar. 

Para verificar el monto disponible que se podrá transferir, en la vista que se mostrará a continuación y que se encuentra en POA/Operación/Restringidas/Partidas

<!-- Page 4 -->

Restringidas Capítulo 5000, habrá una columna marcada como Disponible para Transferir para que se tenga control de los montos que se van liberando para transferencia. 

# **Transferencias de capítulo 5000** 

Cual sea la opción a elegir para liberar monto, una vez liberado montos de los Partidas Restringidas capítulo 5000 ya se podrá realizar transferencias sobre el área, acción y partida en cuestión. 

Las transferencias de capítulo 5000 para el caso de Origen de Recurso “IP”, ya se podrán realizar en la opción de POA/Operación/Transferencias/Transferencias Generales, o bien en los apartados de Incremento de Capítulo 5000 o Reducción Capítulo 5000, ya que se estará abriendo la misma vista de Transferencias Generales. 

En el apartado de Transferencias generales como se ha venido realizando con las demás partidas, deberán elegir Origen y destino final del monto a transferir, ya aparecerán las partidas 5000 tanto para origen como destino, siempre y cuando esté permitido dicho capítulo en la acción elegida, además de que previamente se haya liberado monto para transferir de Partidas Restringidas Capítulo 5000 . 

En el ejemplo se liberaron 20,000.00 de: 

**Área: Departamento de Servicios Escolares 2.2.2-4-1 - Encaminar los esfuerzos institucionales para contribuir en la atención a la Acción: matrícula de licenciatura, así como la medición de la variación del número de alumnos inscritos por semestre. Partida: 51101 – MOBILIARIO**

<!-- Page 5 -->

En Transferencias Generales se podrá verificar que se tendrá disponible para transferir dicha cantidad. 

Se deberá definir todos los campos para realizar la transferencia, tanto com del Origen de la Transferencia como del Destino. Podrá ser el destino un mismo capítulo 5000 si así se requiere. 

Si el monto liberado fue eliminando todo el registro de la Partida Restringida Capítulo 5000, entonces se podrá ver como disponible en la transferencia el monto total del registro eliminado. 

# **Definición de cambios en artículos y montos dentro de la adecuación** 

Una vez terminadas todas las transferencias para la adecuación, se sigue el procedimiento ya conocido para agregar las transferencias a la adecuación en POA/Operación/Adecuaciones 

Previamente en el ejemplo se liberó el monto total de un Subprespuesto eliminando el registro ( DCEA, acción ET.5.1-14-1, partida 51101 por un monto de 43,400.00), además del monto liberado por medio de edición de cantidad de artículos de 20,000.00 anteriormente explicado. 

Una vez agregadas las transferencias, se procede a entrar en el apartado de Ver Adecuación, y en la pestaña de Capítulo 5000 para realizar los movimientos en cuanto a artículos para que el monto modificado empate con los artículos a comprar.

<!-- Page 6 -->

Es importante dar click en botón Cargar 5000 para que se realice la actualización de los movimientos realizados. 

Como se puede ver en la imagen anterior, en rojo estará el registro en el área, acción y partida del cual se transfirieron 20,000.00 y por tanto se debe ajustar dicha justificación de bien a adquirir, eso se realizará en el botón de editar. 

Como se muestra en la imagen anterior, hay un presupuesto disponible para justificar, lo cuál se deberá ajustar para que se permita guardar. Además en el botón de editar, también se pueden cambiar la descripción del bien si así se requiere o los demás datos. Es en esta pantalla donde se deberá realizar los cambios de descripción si así se desea. 

En el caso de que se haya liberado por completo un subpresupuesto, es decir que se haya eliminado como se explicó anteriormente para liberar todo el monto y poder transferirlo, en ésta pantalla se permitirá eliminar dicho registro para poder cuadrar las justificaciones de bienes con los movimientos de la adecuación.

<!-- Page 7 -->

Como se observa en la imagen anterior, solo permitirá eliminar aquel registro que fue liberado por completo de Partidas Restringidas 5000. Los demás registros solo tienen habilitado el botón de editar por si se requiere cambiar la descripción del bien u otro dato como, taller, población beneficiada, Riesgos, etc. 

Si fuera el caso en el que se transfirió algún monto de una partida y el destino final fue un 5000 que no estaba contemplado en el POA Original o el último modificado autorizado, entonces también se puede insertar un nuevo registro para cuadrar la justificación de dicho movimiento por medio del botón de insertar. En la pantalla se tendrá que definir el nuevo bien con la información del área, acción y partida y demás información requerida acorde a la/s transferencia/s que lo generó. 

Para ejemplificar, se realizó una transferencia a un área, partida 51201 y acción que originalmente no se encontraba en el POA original. 

Y se debe de insertar una nueva justificación de bien en el botón de insertar mencionado anteriormente.