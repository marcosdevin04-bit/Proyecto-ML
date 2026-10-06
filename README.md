# Priorización de reclamos operativos de OSE

Proyecto académico de Machine Learning orientado a analizar solicitudes y reclamos operativos de OSE para apoyar la priorización del despacho de cuadrillas.

El trabajo integra problemas de **regresión** y **clasificación**, desde la exploración y preparación de los datos hasta la evaluación de modelos y la toma de decisiones basada en costos.

## Objetivos

- Construir un flujo reproducible de carga, auditoría y preparación de datos.
- Prevenir fugas de información mediante pipelines correctamente definidos.
- Desarrollar y comparar modelos de regresión y clasificación.
- Evaluar el rendimiento mediante validación cruzada y métricas apropiadas.
- Analizar regularización, escalado y selección de hiperparámetros.
- Definir criterios de priorización considerando el costo de las decisiones.
- Favorecer la interpretación de los resultados y de las reglas obtenidas.

## Contenidos principales

- Análisis exploratorio y control de calidad de los datos.
- Ingeniería y transformación de variables.
- Modelos base y comparación de alternativas.
- Regresión lineal y regularizada.
- Clasificación y ajuste del umbral de decisión.
- k vecinos más cercanos y árboles de decisión.
- Validación cruzada y prevención de *data leakage*.
- Interpretación de métricas y resultados.

## Documentación

- [Consigna del proyecto](consigna-proyecto-reclamos-ose.pdf)
- [Notebook completo y ejecutado](entrega_reclamos_ose.ipynb)
- [Template oficial](entrega_reclamos_ose_template.ipynb)
- [Guía para defender decisiones y resultados](GUIA_DEFENSA.md)
- [Instrucciones de ejecución y alcance](README_ENTREGA.md)

## Reproducir el análisis

Se verificó con Python 3.12. Desde la raíz del repo, en macOS o Linux:

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

El ejecutor extrae el CSV de OSE desde `data/ose_2024.zip` y corre el notebook desde un kernel nuevo. El CSV de 114 MB queda fuera de Git; su ZIP oficial sí está versionado. Para abrir el notebook en Jupyter o VS Code, correr antes `python preparar_datos.py` y elegir como kernel el entorno `.venv`.

## Resultados principales

- La unión conserva los 3.964 reclamos del complemento. Tras quitar 32 copias y 331 tiempos negativos quedan 3.604 reclamos válidos, con un 16,1 % de incumplimientos.
- Validación cruzada de cinco folds (estratificada en clasificación) y una prueba reservada de 721 reclamos que se usa una sola vez.
- Tiempo de resolución: la mejora sobre predecir la media es chica. Lasso queda en un MAE de 80,2 h contra 82,9 h de la base, y el error está dominado por unos pocos reclamos muy largos.
- Priorización: la regresión logística logra un AUC de 0,771 ± 0,028. La fuga de información inflaría ese valor a 0,974.
- Con el umbral derivado de los costos (45 / (45 + 270) = 0,143), en la prueba reservada se detectan 92 de 116 incumplimientos y el costo baja a USD 22,91 por reclamo, contra USD 43,44 sin priorizar: unos USD 8,0 millones al año sobre 390.000 reclamos.

Distancia, conexiones afectadas y calificación de atención son columnas construidas por la cátedra con fines didácticos. Los resultados **no constituyen un diagnóstico de la gestión de OSE**. Los costos anuales son proyecciones bajo los supuestos del caso, no ahorro causal demostrado ni presupuesto operativo completo.

## Estado

Las 13 secciones están completas sobre la plantilla oficial, con el notebook ejecutado de punta a punta y todas las salidas visibles. Se incluyen la guía de defensa, los datos comprimidos y las dependencias para reproducirlo. La entrega de la cátedra se realiza por **Moodle**; subir el repo no sustituye esa entrega.

## Autores

- Marcos Devincenzi
- Facundo Díaz
- Santiago Alba
- Domingo Leiva

Estudiantes de Ingeniería en Inteligencia Artificial y Ciencia de Datos en la Universidad Católica del Uruguay.
