# Procedencia del snapshot incluido

- Fuente: endpoint chart de Yahoo Finance, respuestas JSON originales.
- Acciones de ejemplo: AAPL, MSFT, NVDA, META, GOOGL, AMZN, TSLA, JPM, V y NFLX.
- Periodo solicitado: 1 de abril a 22 de octubre de 2026, ambos incluidos.
- Frecuencia: sesiones diarias. Se utiliza el campo `indicators.quote.close`.
- Contenido: 1.420 cierres reales; 142 sesiones por acción.
- Originales: `lake/raw/yahoo/<descarga>/*.json`. URL, hora de descarga y SHA-256 en su manifiesto.
- Datos derivados: `lake/clean/prices.csv` y `lake/curated/features.csv`.

Las respuestas se conservan sin alterar. La preparación extrae ticker, fecha y cierre; el ETL reconstruye las tablas y las señales. La fecha de descarga no convierte un valor histórico en una cotización actual.

Este snapshot sirve para que la base funcione al clonarla. No demuestra ausencia de revisiones históricas ni constituye un dataset suficiente para validar ML en los tres horizontes. Para RA2 necesitarás investigar histórico, publicaciones y disponibilidad temporal.

Los datos de terceros mantienen sus condiciones de origen. La licencia del código de este repositorio no concede derechos adicionales sobre datos de proveedores. No añadas claves, cookies o datos de una cuenta personal a las descargas versionadas.
