# Fuentes de datos

- `ose_2024.zip`: descarga oficial de OSE. Contiene el CSV de 390.886 filas, separado por punto y coma y codificado en UTF-8.
- `metadatos_ose.csv`: diccionario oficial; separado por punto y coma y codificado en Windows-1252.
- `entregas_reclamos_complemento.csv`: complemento didáctico de la cátedra con 3.964 identificadores, distancia, conexiones afectadas y calificación de atención.
- `catalogo_ose.json`: respuesta del catálogo con las URLs y metadatos de los recursos consultados.

Fuentes: [OSE](https://datos.ose.com.uy/dataset/reclamos-operativos) y [repositorio de la cátedra](https://github.com/ucudal/Machine-Learning---Ingenieria-en-IA-y-CD/blob/main/data/entregas_reclamos_complemento.csv).

El CSV descomprimido ocupa 114 MB y no se versiona directamente. Ejecutar `python preparar_datos.py` desde la raíz del repo para extraerlo, o ejecutar `ejecutar_notebook.py`, que realiza esa preparación si hace falta. El paquete `OSE_entrega_completa.zip` incluye el CSV extraído para la entrega.

Los datos de OSE se publican bajo la Licencia de Datos Abiertos del Uruguay. Las tres columnas del complemento son didácticas; los resultados no constituyen un diagnóstico de la gestión de OSE.
