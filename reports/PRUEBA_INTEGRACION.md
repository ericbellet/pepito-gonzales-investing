# Prueba de integración · Pepito Gonzales

Prueba realizada el 5 de noviembre de 2026 con un alumno ficticio. La copia se creó desde la plantilla en la cuenta `ericbellet`, tal como autorizó el profesor. No se ha creado otra cuenta de GitHub ni se ha probado un fork entre dos cuentas.

- [Leaderboard de Pepito](https://proyectolasalle20262027.vercel.app/leaderboard?student=pepito-gonzales-prueba)
- [API pública](https://pepito-gonzales-investing.vercel.app/api/predictions)
- [Swagger](https://pepito-gonzales-investing.vercel.app/docs)

## Evidencia del recorrido

| Paso | Resultado observado |
|---|---|
| Copia y descarga | Repositorio propio en GitHub y clon local independientes de la base |
| Dependencias | Instaladas con `uv sync --locked --python 3.11`; seis comprobaciones superadas |
| Datos raw | Descarga original conservada con URL, fecha y SHA-256 |
| ETL PySpark | 1.510 precios, diez empresas, 1.510 filas al releer Parquet; corte del 4 de noviembre de 2026 |
| Publicación | Nombre Pepito Gonzales; nueve selecciones: tres por cada horizonte 1W, 1M y 3M |
| API local | HTTP 200; dos consultas devuelven el mismo resultado y fecha |
| API pública | HTTP 200 sin login; mismo resultado en consultas consecutivas |
| Registro del profesor | Alumno `pepito-gonzales-prueba`, habilitado con su URL HTTPS |
| Validación de la plataforma | `healthy`, HTTP 200 y nueve selecciones válidas |
| Recogida | Nueve selecciones guardadas en el ciclo `2026-W45` |
| Página pública | Nombre visible sin filtros; al filtrar, una fila de clasificación y nueve filas de selecciones |
| Navegador | Sin errores de JavaScript en la comprobación |

## Despliegue

- URL: https://pepito-gonzales-investing.vercel.app
- Proyecto: `pepito-gonzales-investing`, equipo Eric's projects
- Entorno: producción del proyecto de prueba
- Estado comprobado: READY
- Framework: FastAPI, Python 3.12 y dependencias instaladas desde uv.lock
- Identificador: `dpl_HAd2dfArovKG21Ryy34KSuDfCNDY`
- Commit que conserva los archivos de la prueba: `6b9b762`
- Compilación: 3 segundos, tras una espera previa del proveedor para descargar los archivos
- Registros de error: la consulta no devolvió entradas; las peticiones comprobadas respondieron HTTP 200
- Drains: no inspeccionados. La verificación es puntual; no configura vigilancia periódica.

## Resultado visible

![Fila real de Pepito Gonzales en el leaderboard](pepito-leaderboard.png)

Las nueve selecciones figuran como pendientes. Pepito tiene cero puntos y estado provisional porque todavía no hay resultados vencidos. No se han inventado aciertos ni modificado las selecciones de otros participantes.

Los detalles de las respuestas y las filas observadas están en [integration.json](integration.json).
