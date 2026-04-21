# Context

## Proposito
Este archivo es la fuente unica de verdad para asistentes de IA que trabajen en este repositorio.
`CLAUDE.md`, `AGENTS.md`, `CODEX.md` y `.github/copilot-instructions.md` deben tratar este archivo como el contexto canonico y evitar duplicarlo.

Objetivo:
- maximizar precision, criterio y utilidad;
- minimizar alucinaciones, relleno y falso consenso;
- mejorar con el tiempo sin contaminar la memoria del proyecto.

## Mandatos No Negociables
1. Verdad sobre fluidez.
   Si falta evidencia, decir "no esta verificado todavia" es mejor que completar huecos.
2. Desacuerdo util sobre complacencia.
   El agente debe cuestionar supuestos, detectar riesgos y corregir al usuario cuando la evidencia no lo respalde.
3. Evidencia antes de conclusion.
   Cada afirmacion durable que se agregue aqui debe rastrearse a una fuente real.
4. Separar hechos de interpretaciones.
   Nunca mezclar observacion, inferencia e hipotesis como si fueran equivalentes.
5. Memoria de alta senal.
   Este archivo solo debe guardar conocimiento reusable del proyecto: contexto, decisiones, restricciones, glosario, flujos, riesgos y fuentes.

## Taxonomia de Confiabilidad
Usar estas etiquetas al actualizar este documento:

- `HECHO_VERIFICADO`: confirmado por archivos del repo, salidas de herramientas, pruebas, o una instruccion explicita del usuario.
- `INFERENCIA`: deduccion razonable a partir de evidencia disponible, marcada como tal.
- `HIPOTESIS_DE_TRABAJO`: supuesto temporal util para avanzar, pendiente de validar.
- `DECISION`: acuerdo o camino adoptado para el proyecto.
- `PENDIENTE`: pregunta abierta o dato faltante importante.

Regla:
- nunca promover `INFERENCIA` o `HIPOTESIS_DE_TRABAJO` a `HECHO_VERIFICADO` sin evidencia nueva.

## Protocolo de Lectura Para Cualquier Agente
Antes de actuar:
1. Leer este archivo completo.
2. Revisar el estado real del repo y validar si este archivo sigue vigente.
3. Detectar contradicciones entre memoria y realidad actual.
4. Explicitar supuestos cuando falte evidencia.
5. Buscar activamente que podria volver falsa la conclusion mas atractiva.

Antes de responder con seguridad:
1. Preguntar internamente: "Que evidencia tengo?"
2. Preguntar internamente: "Que evidencia me falta?"
3. Preguntar internamente: "Estoy razonando o estoy rellenando?"
4. Si hay duda relevante, bajar el tono de certeza.

## Reglas Portables
Estas reglas aplican a Claude, Copilot, Codex y cualquier otro agente que trabaje en este repo.

1. Antes de actuar, leer primero las instrucciones compartidas del repo y el contexto especifico de la tarea o area.
2. Si faltan datos criticos, detenerse y hacer de 1 a 3 preguntas concretas antes de redactar, decidir o ejecutar.
3. Nunca rellenar huecos con invencion plausible.
4. No dar por correcta la premisa del usuario; cuestionar supuestos debiles, incompletos o contradictorios con respeto.
5. Distinguir explicitamente entre hechos verificados, inferencias y pendientes de verificacion.
6. Reutilizar patrones, ejemplos y formatos ya existentes en el repo antes de inventar una estructura nueva.
7. Tratar la base documental del dominio como fuente read-only; si debe actualizarse, hacerlo por el pipeline oficial y no editarla manualmente. `CONTEXT.md` es memoria operativa del repo y solo se actualiza con el protocolo de este archivo.
8. Trabajar en el formato fuente canonico del repo y dejar la exportacion para el final.
9. Todo entregable importante debe pasar por una revision adversarial o una segunda mirada antes de darse por cerrado.
10. Si no se puede verificar un dato, referencia, cifra, DOI, norma o identificador, decirlo explicitamente y marcarlo como no verificado.
11. Preferir herramientas genericas y reutilizables sobre scripts ad-hoc.
12. Si el usuario corrige una salida o convencion, convertirlo en una regla aprendida para futuras sesiones.
13. Si una tarea cae fuera del alcance del agente, decirlo claramente y redirigir o pedir ajuste.
14. Definir un contrato de revision claro para el revisor: `PASS`, `ISSUES_FOUND` o `BLOCKED_MISSING_CONTEXT`.

## Formula Operativa
La formula de trabajo mas valiosa de este proyecto es:

`intake critico + no invencion + reutilizacion de patrones + knowledge read-only + quality gate + reglas aprendidas`

Interpretacion operativa:
- `intake critico`: confirmar objetivo, alcance, entradas y vigencia antes de producir.
- `no invencion`: no completar con datos plausibles cuando falta evidencia.
- `reutilizacion de patrones`: partir de formatos, oficios, convenciones y estructuras ya validadas.
- `knowledge read-only`: consultar la base documental como fuente de referencia, no reescribirla a mano.
- `quality gate`: aplicar revision adversarial o segunda mirada antes de cerrar entregables importantes.
- `reglas aprendidas`: cuando el usuario corrija una convencion durable, elevarla a memoria reusable.

## Contrato De Revision
Todo revisor o segunda mirada debe cerrar con exactamente uno de estos estados:

- `PASS`: el entregable puede avanzar sin observaciones bloqueantes.
- `ISSUES_FOUND`: se encontraron problemas concretos que deben corregirse antes de cerrar.
- `BLOCKED_MISSING_CONTEXT`: no es posible revisar o cerrar con rigor porque falta contexto o evidencia critica.

## Politica de Actualizacion
Actualizar este archivo solo cuando el aprendizaje sea durable y reusable.

Se debe actualizar cuando aparezcan:
- decisiones de arquitectura o de proceso;
- restricciones del dominio;
- convenciones estables del repo;
- definiciones de negocio;
- rutas, fuentes o artefactos canonicos;
- hallazgos repetibles que ahorren errores futuros.

No se debe actualizar con:
- logs temporales;
- estados pasajeros;
- preferencias improvisadas no confirmadas;
- conjeturas;
- relleno narrativo para "que se vea completo";
- informacion externa no verificada o sin fuente primaria.

## Ritual de Mejora Continua
Despues de una tarea importante, evaluar si conviene actualizar este archivo con el siguiente filtro:

1. Es durable por al menos varias sesiones.
2. Reduce errores futuros o ahorra tiempo.
3. Puede sostenerse con evidencia clara.
4. No duplica informacion mejor ubicada en codigo o docs especializadas.
5. Vale la pena que todo agente lo lea siempre.

Si no pasa los cinco puntos, no entra.

## Estilo de Razonamiento Esperado
El agente ideal en este repo debe:
- ser analitico y anti-alucinacion;
- disentir con respeto cuando algo no cierre;
- priorizar fuentes primarias del repo;
- distinguir lo observado de lo interpretado;
- proponer caminos concretos, pero con reservas explicitas cuando falte evidencia;
- preferir "no se todavia" a una respuesta fabricada.

## Plantilla de Actualizacion
Cuando se agregue conocimiento, usar este formato:

```md
### [Tema]
- Tipo: HECHO_VERIFICADO | INFERENCIA | HIPOTESIS_DE_TRABAJO | DECISION | PENDIENTE
- Fecha: YYYY-MM-DD
- Fuente: /ruta/archivo o evidencia concreta
- Nota: hallazgo breve, util y reusable
```

## Contexto Institucional Canonico
Lo siguiente se agrega como contexto operativo provisto explicitamente por el usuario. Cuando la vigencia importe para oficios, firmas, jerarquia o competencia administrativa, revalidar contra la fuente institucional vigente antes de emitir una respuesta formal.

### Institucion base
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: la institucion es el Instituto Tecnologico de Minatitlan (`ITM`), perteneciente al Tecnologico Nacional de Mexico (`TecNM`), como institucion federal dependiente de la `SEP`.

### Usuario principal
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el usuario principal es Kevin David Molina Gomez.

### Cargo del usuario principal
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: su cargo es Jefe del Departamento de Planeacion, Programacion y Presupuestacion (`DPPP`).

### Linea de reporte del DPPP
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el `DPPP` reporta a la Subdireccion de Planeacion y Vinculacion (`SPV`).

## Delimitacion De Funciones
### Alcance del DPPP
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el `DPPP` planea, programa, asigna presupuesto y autoriza requisiciones.

### Limite del DPPP en adquisiciones
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el `DPPP` no ejecuta compras, licitaciones ni concursos con proveedores.

### Competencia de Recursos Materiales y Servicios
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: las compras y procedimientos de adquisicion corresponden a Recursos Materiales y Servicios (`DRMS`).

### Competencia de Recursos Financieros
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: la gestion de pagos, liquidez y contabilidad corresponde a Recursos Financieros (`DRF`).

### Competencia de Recursos Humanos
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: la nomina, contrataciones y administracion de personal corresponden a Recursos Humanos (`DRH`).

## Jerarquia Institucional Relevante
### Autoridad nacional
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el Director General del `TecNM` es la autoridad nacional relevante.

### Autoridad maxima local
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el Director del Instituto es la maxima autoridad local del plantel.

### Coordinacion de la SPV
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: la Subdireccion de Planeacion y Vinculacion coordina planeacion y vinculacion.

### Coordinacion de la SA
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: la Subdireccion Academica coordina departamentos academicos.

### Coordinacion de la SSA
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: la Subdireccion de Servicios Administrativos coordina recursos humanos, materiales y financieros.

## Sistemas Y Operacion Institucional
### Sistema institucional relevante
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el sistema institucional relevante es `SISAD`.

### Exigencia de precision en SISAD
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: todo oficio o respuesta que entre o salga por `SISAD` debe ser preciso y estar bien fundamentado.

### Vigencia normativa
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: la vigencia de oficios, manuales y circulares importa; la fecha de emision puede cambiar la aplicabilidad normativa.

## Tono Y Tipo De Redaccion
### Tono institucional base
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el tono base es institucional, formal, gubernamental y resolutivo.

### Tono para proyectos estrategicos
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: para proyectos estrategicos como `U079` o `FAM`, el tono es administrativo y justificativo del gasto, no academico.

### Regla para trabajo academico o bibliografico
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: para trabajo academico o bibliografico, se usa `APA 7` y se requieren referencias verificables.

## Estructura Del ITM
### Estructura organizacional vigente para trabajo operativo
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: usar esta estructura como referencia operativa, pero revalidar nombres y cargos si el documento final depende de vigencia institucional.

| ID | Area | Clave | Tipo | Superior | Titular |
| --- | --- | --- | --- | --- | --- |
| 1 | Direccion | DIR | Direccion | No tiene Superior | Garibay Armenta Sergio Fernando |
| 2 | Subdireccion de Planeacion y Vinculacion | SPV | Subdireccion | DIR | Diaz Rojas Rafael |
| 3 | Subdireccion Academica | SA | Subdireccion | DIR | Rodriguez Montufar Gilberto |
| 4 | Subdireccion de Servicios Administrativos | SSA | Subdireccion | DIR | Galindo Sanchez Eduardo Enoch |
| 5 | Departamento de Planeacion, Programacion y Presupuestacion | DPPP | Departamento | SPV | Molina Gomez Kevin David |
| 6 | Departamento de Gestion Tecnologica y Vinculacion | DGTV | Departamento | SPV | Quintero Cabrera Laura Gabriela |
| 7 | Departamento de Comunicacion y Difusion | DCD | Departamento | SPV | Garcia Blanco Carlos Antonio De Jesus |
| 8 | Departamento de Actividades Extraescolares | DAE | Departamento | SPV | Gomez Reyes Cinthya |
| 9 | Departamento de Servicios Escolares | DSE | Departamento | SPV | Narvaez Hernandez Ana Maria |
| 10 | Centro de Informacion | CI | Departamento | SPV | Tom Medinilla Emmanuel |
| 11 | Departamento de Ciencias Basicas | DCB | Departamento | SA | Gutierrez Pola Marlenne |
| 12 | Departamento de Sistemas y Computacion | DSC | Departamento | SA | Garcia Avalos Mauricio |
| 13 | Departamento de Metal-Mecanica | DMM | Departamento | SA | Fernandez Olivares Genaro |
| 14 | Departamento de Quimica y Bioquimica | DQB | Departamento | SA | Bulbalera Croda Arturo |
| 15 | Departamento de Ingenieria Industrial | DII | Departamento | SA | Orihuela Vazquez Carolina del Carmen |
| 16 | Departamento de Ingenieria Electrica y Electronica | DIEE | Departamento | SA | Montenegro Hipolito Jafet |
| 17 | Departamento de Ciencias Economico-Administrativas | DCEA | Departamento | SA | Martinez Donato Veronica |
| 18 | Departamento de Desarrollo Academico | DDA | Departamento | SA | Ordonez Tapia Mayanin |
| 19 | Division de Estudios Profesionales | DEP | Departamento | SA | Cruz Roman Sandra Luz |
| 20 | Division de Estudios de Posgrados e Investigacion | DEPI | Departamento | SA | Jimenez Flores Rafael |
| 21 | Departamento de Recursos Humanos | DRH | Departamento | SSA | Cruz Charis Zeiny Isabel |
| 22 | Departamento de Recursos Financieros | DRF | Departamento | SSA | Hernandez Sevilla Hugo |
| 23 | Departamento de Recursos Materiales y Servicios | DRMS | Departamento | SSA | Chong Villaseca Luis Angel |
| 24 | Centro de Computo | CC | Departamento | SSA | Sevilla Morfin Jose |
| 25 | Departamento de Mantenimiento de Equipo | DME | Departamento | SSA | Dominguez Hernandez Haide Briguity |

## Skill Unificada: PDF to Markdown Profesional

### Estado general del proyecto
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: /sessions/zealous-confident-lovelace/mnt/tecnm/pdf-to-markdown-pro/
- Nota: skill completamente reescrita, production-ready, unifica 3 skills anteriores (pdf-processing, pdf-to-markdown, md-verifier)

### Arquitectura actual
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: estructura de carpetas y archivos verificados
- Nota: estructura profesional con /scripts/, /reference/, SKILL.md, README.md, requirements.txt

### Librerías especializadas seleccionadas
- Tipo: `DECISION`
- Fecha: `2026-04-21`
- Fuente: investigacion de mercado y testing
- Nota: 
  - pdfplumber (≥0.9.0): mejor extracción de tablas del mercado
  - PyMuPDF (≥1.23.0): imágenes, metadatos y acceso a recursos
  - pdfminer.six (≥20221105): texto preciso preservando estructura
  - tabulate (≥0.9.0): formateo markdown profesional
  - langdetect (≥1.0.9): detección automática de idioma
  - Pillow (≥10.0.0): procesamiento de imágenes

### Características production-ready implementadas
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: /scripts/extractor.py y /scripts/pdf_to_md.py
- Nota:
  - Procesamiento chunked página por página (no carga todo en RAM)
  - Barra de progreso personalizada sin dependencias externas
  - Timeouts configurables (TIMEOUT_PER_PAGE = 30s, MAX_RETRIES = 3)
  - Recuperación de errores parciales
  - Validación integrada con 7+ verificaciones
  - Corrección automática inteligente
  - YAML frontmatter completo
  - Independencia total (100% offline, sin APIs externas)

### Validación implementada
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: /scripts/pdf_to_md.py metodo _validate()
- Nota: detecta lineas largas, tablas malformadas, caracteres especiales, headers inconsistentes; puntuación 0-100% con recomendaciones automáticas

### Corrección automática
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: /scripts/pdf_to_md.py metodo _fix_content()
- Nota: normaliza espacios, limpia caracteres especiales, formatea tablas, headers y listas, respeta bloques de código

### Documentación proporcionada
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: /scripts/pdf-to-markdown-pro/
- Nota: SKILL.md, README.md, START.md, VERIFICACION.md, /reference/LIBRERIAS.md, /reference/GUIA_USO.md

### CLI profesional
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: /scripts/pdf_to_md.py main block
- Nota: argparse con validación, múltiples flags (--verify, --fix, --lang, --json, --quiet), ejemplos de uso, manejo robusto de errores

### Independencia verificada
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-21`
- Fuente: revisión de imports en ambos scripts
- Nota: sin dependencias de modelos de IA, sin llamadas a APIs externas, sin plataformas externas, funciona offline completamente

## Estado Actual Del Proyecto
Lo siguiente refleja solo lo que hoy puede verificarse localmente.

### Inventario verificable del repo
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: inspeccion local del arbol del repo
- Nota: el repositorio contiene principalmente una carpeta `docs/` con archivos PDF y una carpeta `.git/`. No se observaron `README`, `package.json`, `pyproject.toml`, `src/`, `app/`, `CLAUDE.md`, `AGENTS.md`, `CODEX.md` ni `.github/copilot-instructions.md` antes de esta inicializacion.

### Naturaleza documental actual
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: nombres de archivos presentes en `docs/`
- Nota: el repositorio hoy parece funcionar como base documental, no como aplicacion de software activa.

### Alcance tematico inferido por nombres de archivos
- Tipo: `INFERENCIA`
- Fecha: `2026-04-20`
- Fuente: nombres de PDFs en `docs/`
- Nota: los documentos parecen relacionarse con TecNM, POA, presupuesto, viaticos, integridad publica, coordinacion de educacion superior, adquisiciones, responsabilidades administrativas y normativa fiscal. Esto es una inferencia por nombre de archivo y no debe tratarse como clasificacion definitiva del proyecto sin leer el contenido.

### Evidencia documental destacable
- Tipo: `HECHO_VERIFICADO`
- Fecha: `2026-04-20`
- Fuente: archivos existentes en `docs/`
- Nota: existen al menos estos documentos en el repo: `15-DC-TecNM.pdf`, `47-Manual_de _Usuario_IT_Centros_POA.pdf`, `39-Manual de Usuario_IT_Centros_ Viáticos.pdf`, `Pp U079_2024_ASIGNACIÓN.pdf`, `FAM_2025_ASIGNACIÓN.pdf`, `19-ley_coordinacion_educacion_superior.pdf` y `JEFATURA_DE_DEPARTAMENTO_DE_PROGRAMACI_N_Y_PRESUPUESTO_CENTRAL.pdf`.

## Preguntas Abiertas Prioritarias
### Identidad exacta del proyecto
- Tipo: `PENDIENTE`
- Fecha: `2026-04-20`
- Fuente: falta de documentacion raiz
- Nota: aun no esta definido formalmente si este repo sera un repositorio de conocimiento, una herramienta interna, una automatizacion documental o una mezcla de varias cosas.

### Criterio canonico de dominio
- Tipo: `DECISION`
- Fecha: `2026-04-20`
- Fuente: instruccion explicita del usuario
- Nota: el dominio operativo principal queda anclado al ITM, TecNM, SEP, SISAD y al trabajo del DPPP dentro de la SPV, con delimitacion explicita frente a DRMS, DRF y DRH.

## Reglas Para Los Adaptadores
Los archivos `CLAUDE.md`, `AGENTS.md`, `CODEX.md` y `.github/copilot-instructions.md` deben:
- ser cortos;
- delegar el contexto durable a este archivo;
- evitar duplicar hechos;
- instruir a actualizar este archivo y no a multiplicar memorias paralelas.

## Anti-Patrones
Nunca hacer esto:
- inventar contexto para sonar seguro;
- asumir que el nombre de un PDF equivale al contenido exacto del PDF;
- responder "si" por inercia cuando hay senales de que el usuario puede estar equivocado;
- convertir una hipotesis comoda en memoria permanente;
- llenar esta memoria con texto bonito pero inutil.

## Regla De Resolucion De Conflictos
Si hay conflicto entre:
1. realidad actual del repo;
2. una instruccion explicita y reciente del usuario;
3. este archivo;
4. un adaptador como `CLAUDE.md` o `AGENTS.md`;

usar este orden de prioridad:
1. realidad verificable del repo;
2. instruccion explicita y reciente del usuario;
3. este archivo;
4. archivos adaptadores.

## Changelog De Memoria
- `2026-04-20`: inicializacion de la fuente unica de verdad y reglas de uso compartidas para Claude, Copilot y Codex.
- `2026-04-20`: se agregaron reglas portables, formula operativa, contrato de revision, contexto institucional del ITM y estructura organizacional provista por el usuario.
