# Priorización de reclamos operativos de OSE

Entrega académica con las 13 secciones de la consigna. Notebook ejecutado con datos oficiales de OSE y complemento didáctico de la cátedra; guía de defensa con resultados reales y justificaciones.

## Archivos

- `entrega_reclamos_ose.ipynb`: notebook completo con salidas visibles.
- `GUIA_DEFENSA.md`: explicación de decisiones, alternativas, resultados y preguntas de defensa.
- `consigna-proyecto-reclamos-ose.pdf`: enunciado fuente.
- `data/`: ZIP oficial de OSE 2024, metadatos y complemento; el CSV se extrae antes de ejecutar. El paquete de entrega incluye el CSV ya extraído.
- `resultados/`: métricas de CV/test, políticas económicas, reglas y auditoría.
- `requirements.txt`: versiones verificadas en esta ejecución.
- `ejecutar_notebook.py`: ejecución reproducible desde kernel nuevo.
- `preparar_datos.py`: extrae el CSV oficial del ZIP versionado, sin una descarga adicional.

## Reproducir en Windows

Abrir PowerShell en la carpeta que contiene el notebook:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -X utf8 ejecutar_notebook.py
```

También se puede ejecutar `python preparar_datos.py`, abrir el notebook en Jupyter o VS Code, seleccionar ese entorno, reiniciar kernel y ejecutar todas las celdas. Las rutas se declaran en la primera celda de código; no dependen de la ruta personal del autor. Se necesita Python 3.12 para reproducir las versiones verificadas. El notebook trae los resultados ya ejecutados.

## Evaluación

Conjunto válido de 3.604 reclamos; 2.883 en desarrollo y 721 en test reservado. Cinco folds, clasificación estratificada, semilla 42. Pipeline completo dentro de cada fold; selección acotada de alpha, vecinos y profundidad. No se usa test para elegir hiperparámetros ni umbral. Toda la ingesta y unión está en el notebook.

## Entrega

La cátedra indica entrega por Moodle, con salidas visibles. Revisar comprensión entre los cuatro integrantes antes de subir. La versión final está adaptada a `entrega_reclamos_ose_template.ipynb`, aportado por el usuario: conserva literalmente las consignas de las 13 secciones y completa los espacios de respuestas. Se incluye el template original y `enunciado.pdf`, nombre referenciado por ese template.

## Alcance

Las columnas distancia, conexiones y calificación fueron construidas por la cátedra con fines didácticos. Este trabajo no constituye un diagnóstico de la gestión de OSE. Costos y ahorro anual son proyecciones bajo los supuestos del ejercicio, no presupuesto total ni efecto causal demostrado.

Autores: Marcos Devincenzi, Facundo Díaz, Santiago Alba y Domingo Leiva. UCU, Ingeniería en IA y Ciencia de Datos.
