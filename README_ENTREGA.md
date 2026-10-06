# Priorización de reclamos operativos de OSE

Entrega académica con las 13 secciones de la consigna, sobre la plantilla oficial. El notebook está ejecutado con los datos abiertos de OSE y el complemento didáctico de la cátedra. La guía de defensa explica cada decisión con los resultados del notebook.

## Archivos

- `entrega_reclamos_ose.ipynb`: notebook completo, ejecutado, con todas las salidas visibles.
- `entrega_reclamos_ose_template.ipynb`: plantilla oficial, sin modificar.
- `GUIA_DEFENSA.md`: decisiones, alternativas descartadas, resultados y preguntas para practicar la defensa oral.
- `consigna-proyecto-reclamos-ose.pdf` y `enunciado.pdf`: la consigna (el segundo es el nombre que cita la plantilla).
- `data/`: ZIP oficial de OSE 2024, metadatos y complemento. El CSV se extrae antes de ejecutar.
- `requirements.txt`: versiones verificadas.
- `preparar_datos.py`: extrae el CSV oficial del ZIP versionado, sin descargar nada.
- `ejecutar_notebook.py`: ejecuta el notebook completo desde un kernel nuevo.

## Reproducir

En macOS o Linux, desde la carpeta del repo:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python ejecutar_notebook.py
```

En Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -X utf8 ejecutar_notebook.py
```

También se puede correr `python preparar_datos.py`, abrir el notebook en Jupyter o VS Code, elegir el entorno `.venv` como kernel, reiniciarlo y ejecutar todas las celdas. Las rutas de los archivos se declaran solo en la primera celda de código. La ejecución completa tarda alrededor de un minuto y medio.

## Evaluación

3.604 reclamos válidos: 2.883 para desarrollo y 721 de prueba reservada, estratificada. Cinco folds con semilla 42, los mismos para todos los modelos. El pipeline completo se ajusta dentro de cada fold. Los únicos hiperparámetros que se buscan son λ de Ridge y Lasso, k de k vecinos y la profundidad del árbol. La prueba reservada no se usa para elegir hiperparámetros ni umbral: se usa una sola vez, en la sección 13.

## Entrega

La cátedra recibe la entrega por Moodle, con el notebook ejecutado y las salidas visibles. Subir el repo a GitHub no la reemplaza. Antes de subir, conviene que los cuatro integrantes revisen la guía de defensa.

## Alcance

La distancia, las conexiones afectadas y la calificación de atención son columnas construidas por la cátedra con fines didácticos. Este trabajo no constituye un diagnóstico de la gestión de OSE. Los costos y el ahorro anual son proyecciones bajo los supuestos del ejercicio, no un presupuesto ni un efecto causal demostrado.

Autores: Marcos Devincenzi, Facundo Díaz, Santiago Alba y Domingo Leiva. UCU, Ingeniería en Inteligencia Artificial y Ciencia de Datos.
