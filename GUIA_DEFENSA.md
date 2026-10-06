# Guía para defender el proyecto de OSE

Esta guía resume qué hicimos en cada sección, por qué, y con qué números lo sostenemos. Todas las cifras salen de las salidas de `entrega_reclamos_ose.ipynb`. No reemplaza entender el código: en la defensa le pueden preguntar a cualquiera de los cuatro por cualquier celda.

Las cifras de validación cruzada son sobre los 2.883 reclamos de desarrollo y se informan como media ± desvío entre folds. Las de la prueba reservada (721 reclamos) se marcan como «prueba».

## Presentación de un minuto

> Cuando entra un reclamo, OSE tiene que decidir si manda una cuadrilla prioritaria. Unimos los datos abiertos de 2024 con el complemento de la cátedra y auditamos la tabla antes de modelar: había tiempos negativos, distancias cargadas en metros y reclamos copiados. Usamos solo lo que se sabe al ingresar el reclamo; si metiéramos datos del cierre, el AUC pasaría de 0,77 a 0,97 y sería mentira. Para estimar el tiempo de resolución, los modelos lineales mejoran poco sobre predecir la media, porque unos pocos reclamos de meses dominan el error. Para priorizar, la regresión logística ordena bien el riesgo (AUC 0,77), y el umbral lo sacamos de los costos: como dejar pasar un incumplimiento cuesta seis veces más que mandar una cuadrilla de más, conviene priorizar desde un 14,3 % de probabilidad. En la prueba reservada eso detecta 92 de 116 incumplimientos y cuesta USD 22,91 por reclamo, contra USD 43,44 sin priorizar: unos USD 8 millones al año. Es una proyección con los supuestos del ejercicio, no un ahorro demostrado.

## Cómo está armado el código

Conviene que los cuatro puedan explicar estas cuatro piezas, porque se usan en todo el notebook:

- **`flujo(modelo, escalar=True)`** arma el `Pipeline`: primero el `ColumnTransformer` (mediana + indicador de ausencia + escalado para las numéricas; «sin dato» + one-hot para las categóricas) y después el modelo. Es el mismo esquema del lab 4.
- **`validar_regresion` y `validar_clasificacion`** hacen la validación cruzada a mano, como el bucle del lab 4. En cada fold entrenan el pipeline completo con cuatro partes y miden en la quinta. Devuelven las métricas de cada fold y la predicción de cada reclamo hecha por un modelo que no lo vio (lo que se usa después para los costos).
- **`cv_reg` y `cv_clas`** son los folds: `KFold` y `StratifiedKFold`, 5 particiones, semilla 42. Se crean una vez y todos los modelos usan los mismos.
- **`costo_por_reclamo(y, priorizar)`** cuenta falsos positivos y falsos negativos y devuelve `(45·FP + 270·FN) / n`.

## 1. Datos, unión y auditoría

**Unión.** 390.886 filas de OSE, 3.964 del complemento, 3.964 después de filtrar y 3.964 después de unir. Lo garantizan los identificadores únicos en las dos tablas, `validate="one_to_one"` en el `merge` y los `assert` del final.

**Defectos que encontramos y qué hicimos:**

- **331 tiempos negativos** (10 con el código −1 de «sin dato» y 321 imposibles). Los excluimos porque no se puede saber si cumplieron el plazo. No los pasamos a cero ni los imputamos: eso es inventar la respuesta. Ojo: 291 de los 321 están entre −24 h y 0, y esto es lo que discutimos en la autocrítica.
- **21 distancias mayores a 1000 km** (máximo 87.510). Las dividimos por 1000. La prueba de que estaban en metros es que, divididas, quedan en el rango de su departamento: las de Montevideo entre 2,5 y 8,7 km, con mediana departamental 7,0.
- **32 reclamos copiados** (idénticos salvo el identificador). Se quitan antes de particionar para que una copia no quede en entrenamiento y la otra en validación.
- **Códigos de «sin dato»** que los metadatos documentan: fechas 1900, centro técnico −1, «SIN DATOS». Se pasan a faltante.
- **Cola larga del tiempo**: asimetría 16,5, media 66,6 h y mediana 18,7 h.

Las cuentas no suman directo (3.964 − 32 − 331 = 3.601) porque 3 reclamos son a la vez copia y tiempo negativo. Por eso quedan **3.604 válidos**.

**Faltantes.** MCAR: la ausencia no depende de nada. MAR: depende de algo que sí vemos. MNAR: depende del valor que falta. Hicimos lo del lab 11: chi-cuadrado contra categóricas y test t contra numéricas.

- **Conexiones** (255 faltantes): la ausencia se asocia con el tipo de reclamo (p = 0,001) y con la demora (p = 0,010), así que no es MCAR. Entre MAR y MNAR no se puede decidir sin conocer el valor que falta. Imputamos con la mediana (no la media, porque la media es 44 y la mediana 27 por la cola) y agregamos el indicador de ausencia.
- **Calificación** (464): cuando falta, la demora mediana es 49,7 h contra 17,3 h. Quien esperó mucho no contesta. MNAR plausible. Igual se excluye porque la encuesta es posterior al cierre.
- **Centro técnico y orden** (319): faltan en las mismas filas; son reclamos cerrados sin orden de trabajo.

## 2. Preparación

Entran 11 columnas conocidas al ingresar: distancia, conexiones y hora (numéricas); departamento, tipo, complejidad, ausencia de agua, baja presión, inundación, mes y día (categóricas). Mes y día van como categorías porque diciembre no es «doce veces» enero.

Las exclusiones tienen tres motivos distintos, y conviene no mezclarlos:

- **Es la respuesta o la contiene:** el tiempo y las fechas de resolución (resuelto menos ingreso da el tiempo).
- **Disponibilidad:** centro técnico, estado, tipo y grupo de orden, encuesta. Se conocen al cerrar.
- **Otros:** región (redundante con departamento), año (constante), identificador.

Ninguna se excluyó por desempeño. Lo que va antes del pipeline son reglas fijas (unidades, códigos, copias, etiqueta); lo que aprende de los datos (mediana, escala, categorías) va adentro y se reajusta en cada fold.

## 3. Líneas base

- **Regresión:** predecir siempre la media. MAE 82,89 ± 5,98 h y RMSE 279,32 ± 85,87 h. El RMSE va de 209 h a 409 h según el fold: depende de qué reclamos extremos le tocan.
- **Clasificación:** probabilidad constante igual a la prevalencia. AUC 0,500 y AP 0,161. A umbral 0,5 nunca prioriza y aun así tiene 83,9 % de accuracy; por eso no la usamos.

Todo lo que viene después se compara contra estas dos.

## 4. Regresión lineal

**Horas o logaritmo.** En log el MAE baja de 89,66 a 58,84 h pero el RMSE sube de 274,49 a 282,51 h. Elegimos horas porque el uso es planificar carga, que es una suma de horas. El modelo en log, al volver a horas, predice cerca de la mediana: en desarrollo suma 63.553 h cuando las reales son 192.041 h (subestima un 67 %). El de horas suma 193.496 h.

**Coeficientes, en unidades del caso:** cada km más suma 1,1 h y cada conexión más 0,28 h, con todo lo demás fijo. Montevideo suma 104 h frente a Artigas; reposición y señalización, 302 h frente a calidad del agua. Son asociaciones, no causas.

**Contra la base:** el RMSE baja 4,8 h y el MAE sube 6,8 h, con un desvío entre folds de 85 h. Además, 449 de 2.883 predicciones son negativas. Sirve para carga total, no para el plazo de cada reclamo.

## 5. Ridge y Lasso

Ridge achica los coeficientes; Lasso puede dejarlos en cero. λ se elige por validación cruzada con una grilla logarítmica de 25 valores entre 0,001 y 100.000. Ridge eligió **46,4** y Lasso **2,15**, los dos dentro de la grilla (si caían en un borde había que ampliarla).

| Modelo | MAE (h) | RMSE (h) |
|---|---|---|
| Base | 82,89 | 279,32 |
| Mínimos cuadrados | 89,66 | 274,49 |
| Ridge | 84,01 | 272,90 |
| Lasso | 80,22 | 272,62 |

**Qué anula Lasso (43 de 54):** la hora, todos los días y 9 de 11 meses; 15 de 18 departamentos (quedan Montevideo y Canelones); casi todos los tipos (queda reposición y señalización). Conserva distancia, conexiones, el indicador de conexiones faltantes y la ausencia de agua.

**¿Aporta la penalización?** Para predecir, no: Lasso baja el RMSE en 1,86 ± 3,39 h por fold, menos que su propio desvío. La regularización sirve cuando hay pocos datos por coeficiente, y acá hay 53. El error lo domina la cola. Lo que sí aporta Lasso es simplicidad: 11 coeficientes en vez de 54 con el mismo error.

## 6. Regresión logística

Da una probabilidad de incumplir. No ponderamos ni remuestreamos clases, para que las probabilidades se puedan usar directo con el umbral de costos.

AUC **0,771 ± 0,028** y AP **0,403 ± 0,044** (la base: 0,500 y 0,161). A umbral 0,5 la matriz es TN 2.385, FP 34, FN 419, TP 45: detecta 45 de 464. El modelo ordena bien; el que falla es el umbral 0,5, porque casi ningún reclamo pasa del 50 %.

- **AUC:** qué tan bien ordena por riesgo. No es «77 % de aciertos».
- **AP:** precisión y recall para la clase minoritaria; se compara con la prevalencia.
- **La que manda es el costo,** porque los errores no cuestan lo mismo.

## 7. Validación cruzada

Cinco folds, estratificados en clasificación, los mismos para todos. La validación envuelve al pipeline completo. Antes de particionar hay que: quitar copias, excluir tiempos negativos y crear la etiqueta (sin etiqueta no se puede estratificar), convertir unidades y códigos, y decidir qué columnas existen al ingresar. Son reglas fijas, así que hacerlas antes no filtra información.

## 8. Leakage

Mismo modelo, misma preparación, mismos folds; solo se agregan las columnas de cierre (encuesta, centro, estado, tipo y grupo de orden).

| Flujo | AUC | AP |
|---|---|---|
| Honesto | 0,771 ± 0,028 | 0,403 ± 0,044 |
| Contaminado | 0,974 ± 0,004 | 0,896 ± 0,012 |
| Brecha | +0,202 ± 0,026 | +0,493 ± 0,042 |

Esa brecha es lo que el modelo aparentaría en validación y no tendría en producción, porque al ingresar esas columnas están vacías. El tiempo y las fechas no se agregan porque son la respuesta: con ellos el AUC llega a 0,997 y no mide nada interesante.

Si preguntan «¿la validación cruzada no evita el leakage?»: no. Evita entrenar con la fila que se valida, pero no detecta que una columna traiga información del futuro.

## 9. Umbral por costos

Priorizar cuesta en promedio 45·(1 − p); no priorizar, 270·p. Conviene priorizar cuando p > 45 / (45 + 270) = **1/7 ≈ 0,143**. Si los costos fueran iguales, el umbral sería 0,5.

En validación cruzada, con el umbral 0,143 se prioriza el 44 % y el costo es USD 23,65 ± 2,48 por reclamo. Con 0,5 es USD 39,77; priorizando todo, 37,76; sin priorizar, 43,45.

**Prueba reservada (721 reclamos):**

| Política | FP | FN | USD por reclamo | USD por año |
|---|---:|---:|---:|---:|
| Umbral 0,143 | 223 | 24 | 22,91 | 8.933.218 |
| Umbral 0,5 | 6 | 102 | 38,57 | 15.042.857 |
| Priorizar todos | 605 | 0 | 37,76 | 14.726.422 |
| No priorizar | 0 | 116 | 43,44 | 16.941.470 |

La cuenta a mano: (223 × 45 + 24 × 270) / 721 = 16.515 / 721 = **USD 22,91**. Detecta 92 de 116 (79 %) y prioriza 315 reclamos (44 %), con una precisión de 92/315 = 29 %. Esa precisión baja se acepta porque el error contrario es seis veces más caro.

## 10. Tres familias bajo el mismo defecto

Lineal, k vecinos y árbol, con y sin escalado, y con la distancia en km o en metros. k y la profundidad se eligen por MAE (con RMSE el árbol se quedaba en profundidad 1, el borde de la grilla, por culpa de la cola). Ningún valor elegido quedó en un borde.

Cuánto se mueven las predicciones al cambiar una sola cosa:

| Cambio | Lineal | k vecinos | Árbol |
|---|---:|---:|---:|
| Quitar el escalado | 0 h | 36,7 h | 0 h |
| Pasar a metros, con escalado | 0 h | 0,003 h | 0 h |
| Pasar a metros, sin escalar | 0,22 h | 17,3 h | 0 h |

- **k vecinos** compara distancias entre reclamos, así que manda la variable con números más grandes. En metros, la distancia tapa todo lo demás. El k elegido salta de 81 a 151 y a 601. Escalar lo arregla.
- **Lineal:** el coeficiente se ajusta a la unidad (1,1 h por km = 0,0011 h por metro).
- **Árbol:** corta según el orden de los valores, y ese orden no cambia.

## 11. Reglas

Árbol de profundidad 3 (hasta 8 reglas de 3 condiciones) y al menos 30 reclamos por hoja, fijados por legibilidad. Sin escalar, para leer los cortes en km y horas.

Las reglas que sirven: **con agua, en Montevideo y a más de 8,1 km** (388 reclamos, 47,7 % incumple, tres veces la prevalencia) y **con agua, en el interior, y entra un viernes** (184 reclamos, 32,6 %, probablemente porque cruza el fin de semana). Las de falta de agua casi nunca incumplen (0,4 % a 2,7 %). Dos hojas quedan a menos de 2 puntos de la prevalencia: son la media disfrazada.

Contra la logística: AUC 0,757 contra 0,771, y USD 27,10 contra 23,65 por reclamo (unos USD 1,35 millones más al año). A cambio, el operador puede aplicar la regla en segundos, sin sistema, con datos que ya tiene.

## 12. Autocrítica

La decisión más frágil es **haber excluido los tiempos negativos** (sección 1). 291 de los 321 están entre −24 h y 0: probablemente son reclamos resueltos rápido y que cumplieron. Al sacarlos, la prevalencia sube de 14,79 % a 16,09 % y el modelo cree que el riesgo es mayor de lo que es. Cambiarían el AUC y el AP de la sección 7, los costos de la sección 9 y el ahorro de la sección 13. La corrección: etiquetarlos como «no incumple» en la clasificación, volver a correr, y ver si el costo cambia más que su desvío (USD 2,48).

## 13. Recomendación y límites

**Recomendación:** logística con umbral 0,143. En la prueba: AUC 0,784, USD 22,91 por reclamo, ahorro de USD 20,53 por reclamo frente a no priorizar (unos USD 8,0 millones al año) y de USD 14,85 frente a priorizar todos (unos 5,8 millones). Para el tiempo, Lasso (prueba: MAE 76,57 h contra 82,95 de la base), solo para la carga total de cada centro.

**Lo que no se puede concluir:**

- No es un diagnóstico de OSE: distancia, conexiones y calificación son didácticas.
- El ahorro es una proyección: supone que priorizar evita el incumplimiento y que hay cuadrillas para el 44 % de los reclamos (unos 172.000 al año).
- No sabemos nada de los reclamos excluidos.
- Es un solo año, con particiones al azar: no sabemos cómo rinde en 2025.
- Los coeficientes son asociaciones, no causas.

## Preguntas para practicar

**¿Qué es un falso positivo acá?** Priorizar un reclamo que no iba a superar las 72 h: USD 45. **¿Y un falso negativo?** No priorizar uno que sí las supera: USD 270.

**¿Qué pasa con un reclamo que tarda exactamente 72 h?** Cumple, porque el caso dice «superar».

**¿Por qué no usar la encuesta si predice tan bien?** Porque se responde después del cierre. Manda la disponibilidad.

**¿Por qué dividiste las distancias por 1000 y no las borraste?** Porque divididas caen justo en el rango de su departamento. Borrarlas tiraba información correcta.

**¿Por qué mediana y no media para imputar conexiones?** Porque tiene cola: media 44, mediana 27. La media queda arrastrada por los valores grandes.

**¿Por qué no `class_weight="balanced"`?** Porque cambia las probabilidades y el umbral de costos ya no se podría aplicar directo. El recall se ajusta con el umbral.

**¿Por qué el AUC es bueno pero el recall a 0,5 es malo?** El AUC mira el orden de todas las probabilidades; el recall a 0,5 depende de un solo corte, y casi ningún reclamo llega al 50 %.

**¿Para qué la prueba reservada si ya hay validación cruzada?** La validación cruzada se usó para elegir (λ, k, profundidad, regresor). La prueba mide esa elección con reclamos que no participaron.

**¿Por qué no Random Forest o boosting?** La consigna no los pide y no suman puntos.

## Antes de entregar

1. Que cada uno pueda explicar cómo se construye la etiqueta y por qué se excluye la información del cierre.
2. Rehacer a mano la cuenta de USD 22,91.
3. Explicar con la tabla de la sección 10 por qué k vecinos cambia y el árbol no.
4. Abrir el notebook y comprobar que estas cifras aparecen en las salidas.
5. Entregar por Moodle: GitHub no reemplaza la entrega.

## Fuentes

- Consigna: `consigna-proyecto-reclamos-ose.pdf`.
- [Repositorio de la cátedra UCU](https://github.com/ucudal/Machine-Learning---Ingenieria-en-IA-y-CD).
- [Datos y metadatos de OSE](https://datos.ose.com.uy/dataset/reclamos-operativos).
- [scikit-learn: errores comunes y leakage](https://scikit-learn.org/stable/common_pitfalls.html).
