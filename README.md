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
- [Resultados exportados](resultados/)
- [Paquete completo para la entrega](OSE_entrega_completa.zip)

## Reproducir el análisis

Se verificó con Python 3.12. Desde la raíz del repo, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -X utf8 ejecutar_notebook.py
```

El ejecutor extrae automáticamente el CSV de OSE desde `data/ose_2024.zip` y ejecuta el notebook desde un kernel nuevo. El CSV de 114 MB queda excluido de Git; su ZIP oficial sí está versionado. Para abrir el notebook en Jupyter o VS Code, ejecutar antes `python preparar_datos.py` y seleccionar el entorno instalado.

## Resultados principales

- Unión validada de 3.964 reclamos del complemento; conjunto válido final de 3.604 después de resolver copias y objetivos imposibles.
- Cinco folds, clasificación estratificada y test reservado de 721 reclamos.
- Logística honesta: AUC de validación 0,770 ± 0,027.
- Umbral económico: 45 / (45 + 270) = 14,29 %.
- En test, esa política detecta 92 de 116 incumplimientos y cuesta USD 22,84 por reclamo, frente a USD 38,57 con umbral 0,5, según los costos del ejercicio.
- La regresión de horas ofrece mejoras limitadas; la cola del tiempo genera mucha variabilidad entre folds.

Distancia, conexiones afectadas y calificación de atención son columnas construidas por la cátedra con fines didácticos. Los resultados **no constituyen un diagnóstico de la gestión de OSE**. Los costos anuales son proyecciones bajo los supuestos del caso, no ahorro causal demostrado ni presupuesto operativo completo.

## Estado

Las 13 secciones están completas sobre el template oficial, con el notebook ejecutado y resultados visibles. Se incluyen la guía de defensa, los datos comprimidos y las dependencias para reproducirlo. La entrega de la cátedra se realiza por **Moodle**; subir el repo no sustituye esa entrega.

## Autores

- Marcos Devincenzi
- Facundo Díaz
- Santiago Alba
- Domingo Leiva

Estudiantes de Ingeniería en Inteligencia Artificial y Ciencia de Datos en la Universidad Católica del Uruguay.
