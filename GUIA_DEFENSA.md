# Guía para defender el proyecto de OSE

Esta guía explica la implementación y sus resultados reales. Se apoya en `entrega_reclamos_ose.ipynb` y los CSV de `resultados/`. No sustituye comprender el código: cualquier integrante puede ser consultado sobre cualquier sección. Las cifras de CV son sobre desarrollo; las de test se identifican explícitamente.

## Presentación de un minuto

> Buscamos apoyar una decisión al ingresar un reclamo: estimar su tiempo de resolución y su riesgo de superar 72 horas. Unimos los datos reales de OSE con el complemento didáctico y auditamos la calidad antes de modelar. Excluimos datos que solo se conocen al cierre para evitar fuga de información. Comparamos los modelos pedidos con referencias simples, usando pipelines y validación cruzada. La predicción de horas mejora poco y tiene mucha variabilidad; la clasificación distingue riesgos mejor que la prevalencia. Como dejar pasar un incumplimiento cuesta seis veces más que priorizar innecesariamente, derivamos un umbral del 14,3%. En el test reservado, esa política detectó 92 de 116 incumplimientos y tuvo un costo de USD 22,84 por reclamo bajo los costos del ejercicio. No presentamos esa proyección como ahorro real demostrado en OSE.

## 1. Datos, unión y calidad: qué hicimos y por qué

**Procedimiento:** leímos 390.886 filas de OSE, filtramos por los 3.964 identificadores del complemento y unimos uno a uno. Las claves son únicas y todos los identificadores encuentran correspondencia. El metadato confirma que el tiempo está en minutos, que -1 significa ausencia y que 1900 en fechas es un centinela. Convertimos minutos a horas y etiquetamos incumplimiento solo después de verificar la validez del tiempo.

**Justificación:** una unión puede correr y ser incorrecta. Si una clave aparece repetida en ambas tablas, puede multiplicar filas y dar más peso a ciertos reclamos. Por eso usamos `validate='one_to_one'`, comprobamos cobertura y mostramos conteos.

**Hallazgos y decisiones:**

- 331 tiempos negativos: excluidos de las dos tareas. No tomamos valor absoluto ni los convertimos en cero: inventaría el resultado. Tampoco imputamos el objetivo con la media. El cierre en sistema puede ser posterior a la resolución real, así que no sustituimos un objetivo por el otro.
- 32 copias exactas salvo ambos identificadores: quitamos una copia antes de dividir. La coincidencia de todo el registro y el complemento es evidencia de posible duplicación; no es prueba absoluta de que fueran el mismo incidente. Reclamos reales simultáneos pueden coincidir, y lo reconocemos.
- Hay 3 filas que son a la vez copias excluidas y tienen tiempo negativo. Por eso el total final es **3.964 − 32 − 331 + 3 = 3.604**, no 3.601. Los defectos pueden superponerse.
- 21 distancias fuera de [0, 1.000] km: invalidamos el valor y mantenemos el reclamo. Valores de miles de kilómetros no son plausibles para una cuadrilla local. Dividir por 1.000 podría corregir metros anotados como kilómetros, pero no está confirmado: descartamos esa corrección automática. El corte es una decisión de plausibilidad del trabajo, no un umbral oficial de OSE.
- Los tres tiempos cero y distancias de 400 km se conservan. Un extremo no es automáticamente un error. Tiempo cero puede reflejar resolución inmediata a precisión de minutos; no hay evidencia suficiente para asignar otra demora.
- Faltan 255 valores de conexiones y 464 de encuesta en la tabla unida original; además aparecen ausencias codificadas como centinelas. No alcanza con `isna()` sobre el archivo crudo.

**Mecanismos de faltantes:** MCAR significa independencia del resto del registro, MAR dependencia de información observada y MNAR dependencia del valor no observado. No asignamos mecanismos por intuición. Usamos indicadores de ausencia y contrastes con variables observadas. En conexiones, la mediana de demora pasa de 18,31 h con dato a 21,02 h sin dato (p≈0,0074, efecto de rangos pequeño). En encuesta pasa de 17,12 h a 49,80 h (p≈2,7×10⁻³⁷). Hay evidencia exploratoria contra independencia, pero **no podemos distinguir definitivamente MAR y MNAR**. La demora se utiliza para auditar el histórico, nunca como entrada honesta. Los p son exploratorios y hay múltiples contrastes; no establecen causa.

Si preguntan «¿por qué no eliminar todas las filas con faltantes?»: perderíamos reclamos, y la ausencia puede estar asociada con el proceso. Imputar conserva casos, pero tampoco elimina automáticamente el sesgo. El objetivo es distinto de una entrada: sin una respuesta válida no podemos entrenar ni evaluar ese reclamo.

## 2. Preparación: qué aprende cada paso

**Numéricas:** distancia, conexiones y hora. Mediana con indicadores de ausencia; luego StandardScaler. La mediana resiste la cola de conexiones y distancias corruptas mejor que la media como criterio de reconstrucción simple. Comparamos media y mediana en los mismos folds; no declaramos que mediana gana siempre por una frase de buena práctica.

**Categóricas:** departamento, tipo, complejidad, agua, presión, inundación, mes y día. One-hot evita darles un orden artificial. Mes y día son categorías porque diciembre no implica necesariamente doce veces el efecto de enero. El encoder omite una categoría de referencia y admite categorías desconocidas. Una categoría desconocida queda con todas las dummies en cero, como la referencia: eso es un límite, no una garantía de generalización.

**Pipeline y ColumnTransformer:** ColumnTransformer dirige cada tipo de variable a su preparación; Pipeline encadena preparación y modelo. Las medianas, escalas y categorías se aprenden solo del entrenamiento de cada fold. Preparar toda la tabla antes de CV filtraría información de validación.

**Disponibilidad temporal:** excluimos tiempo, fechas de resolución, centro que atendió, orden final, resultado de cierre y encuesta. Aunque mejoraran las métricas, no existen al ingresar. Excluimos además identificadores porque no son atributos generalizables; año porque es constante; región por redundancia observada con departamento. Son motivos diferentes y se justifican columna por columna en el notebook.

## 3. Referencias: qué significa aportar valor

La base de regresión predice la media del entrenamiento de cada fold. Tiene MAE de CV 82.89 h y RMSE 279.32 h. La base clasificadora devuelve prevalencia constante: AUC 0,5 y AP aproximadamente 0,161.

La proporción de incumplimiento es **16.09%**. Si predigo siempre «no incumple», obtengo aproximadamente 84% de accuracy y **recall cero**. Por eso accuracy sola no prueba utilidad. La prevalencia como probabilidad base también permite evaluar Brier; no es únicamente una etiqueta de mayoría.

## 4. Regresión lineal y distribución del objetivo

Mínimos cuadrados minimiza errores cuadrados y busca una relación aditiva entre entradas y tiempo. Interpretamos coeficientes después de volver a las unidades originales: en este ajuste, un km adicional se asocia con **1,048 h** más y una conexión adicional con **0,279 h** más, manteniendo las otras entradas. No significa que aumentar físicamente distancia o conexiones cause exactamente esa demora.

La respuesta tiene cola derecha. Comparamos tiempo directo con `log1p` y evaluamos ambos otra vez en horas. El log baja MAE de 90,32 a 58,83 h, pero eleva RMSE de 275,36 a 282,21 h. Elegimos directo para planificación de carga y prioridad a RMSE. **Si el objetivo fuera el error del caso típico, la alternativa log merecería otra elección.** No afirmamos que directo gane en todas las métricas. Invertir un ajuste log con `expm1` tampoco recupera automáticamente una media condicional en horas.

MAE es promedio del error absoluto; RMSE penaliza mucho más errores grandes. R² mide variación explicada y puede ser negativo. Una mejora en RMSE con MAE peor indica un compromiso entre cola y caso típico, no un error del cálculo. No truncamos las predicciones negativas para mejorar las métricas: las mostramos como límite del modelo.

## 5. Ridge y Lasso

**Ridge** penaliza cuadrados de coeficientes y los reduce. **Lasso** penaliza valores absolutos y puede dejar ceros. El escalado evita que penalizar dependa arbitrariamente de unidades numéricas. Se mantiene la preparación entre mínimos cuadrados, Ridge y Lasso.

Alpha se eligió por CV, con grillas logarítmicas, no a mano. Ridge eligió **51.7947** y Lasso **1.0000**; ambos quedaron dentro de la grilla. Sus normalizaciones de función objetivo son diferentes: esos alpha no se comparan como si midieran lo mismo.

En CV: RMSE lineal 275,36 h; Ridge 273,80 h; Lasso 273,57 h; base 279,32 h. La dispersión entre folds ronda 85–87 h. La mejora existe, pero es pequeña y no alcanza para presentar una predicción precisa de demoras. En MAE de CV ninguno de los tres mejora la base. Penalizar controla flexibilidad, no inventa la información que falta al ingreso ni elimina la cola larga.

Lasso anula **27 de 55 coeficientes** codificados, incluida hora, varias categorías de departamento, algunos tipos, complejidades, meses y una categoría de día. Un cero en una dummy significa que no añade desplazamiento sobre la referencia en este ajuste penalizado; no demuestra que el departamento o el tipo sean causalmente irrelevantes. La lista completa está en el notebook y `resumen.json`.

## 6. Logística: probabilidad y decisión son cosas distintas

La logística convierte una combinación de entradas en probabilidad de incumplimiento entre 0 y 1. Usamos regularización L2 por defecto (`C=1`), sin buscar ese hiperparámetro. Conservamos clases naturales, sin SMOTE ni ponderación; no queremos introducir descalibración por cambiar prevalencias antes de aplicar el umbral económico.

En CV obtiene AUC **0.770 ± 0,027** y AP **0.401 ± 0,043**. A umbral 0,5 el recall es solo 9,7%: ordena riesgos razonablemente, pero ese umbral deja pasar muchos incumplimientos.

AUC evalúa ordenamiento, no significa «77% de aciertos». AP resume precisión-recall y se compara con prevalencia. Brier mide error de probabilidades. Recall cuantifica incumplimientos detectados y precision qué fracción de priorizados realmente incumplía. F1 equilibra precision y recall pero **no incorpora costos 45/270**. Para escoger política manda el costo.

## 7. Evaluación y por qué este orden

Después de limpieza fija, reservamos **721 reclamos** como test y usamos **2.883** para desarrollo. Elegimos cinco folds por equilibrio entre tamaño de entrenamiento, estabilidad y costo de ejecución. Semilla 42 permite reproducir particiones; no es un valor óptimo aprendido. Clasificación usa estratificación para conservar proporciones de clases; no convierte la muestra en 50/50.

Cada predicción OOF viene de un modelo que no entrenó con ese reclamo. Esas predicciones permiten matrices y costos de desarrollo sin medir sobre entrenamiento. Reportamos media y desvío por fold: el desvío es variación, no intervalo de confianza ni una prueba de significancia.

Claves, copias, unidades, centinelas y etiqueta válida se resuelven antes de dividir. Imputación, escalado y categorías después, dentro de cada entrenamiento. Las CV de alpha y de evaluación usan los mismos folds: admitimos sesgo de selección y usamos test reservado para comprobar la elección. No hacemos CV anidada porque queda fuera del alcance.

## 8. Experimento de leakage

El honesto usa información de ingreso. El contaminado agrega futuro; conserva logística, reglas de preparación y folds. AUC pasa aproximadamente de **0,770 a 0,997**, una brecha de **0.227 ± 0,027**. El futuro mejora artificialmente la validación, aunque cada fila esté fuera de su entrenamiento.

Incluimos tiempo de resolución, que determina la etiqueta: es fuga directa. Por eso la brecha mide el conjunto de columnas futuras, no cuánto aporta por sí sola la encuesta. Nunca metemos `incumple_72h` como entrada ni usamos el contaminado para recomendar una política.

Respuesta a «si hago CV, ¿ya evito leakage?»: no. CV evita entrenar en la fila de validación; no corrige que las columnas revelen el resultado futuro.

## 9. Umbral económico y números que tenés que entender

Si p es riesgo de incumplir, priorizar cuesta 45(1−p) en esperanza; no priorizar cuesta 270p. Igualando: 45−45p=270p, por lo que p=45/315=**1/7=14,29%**. Por arriba conviene priorizar. Con costos iguales sería 50%; acá dejar pasar cuesta seis veces más.

**Test reservado, 721 reclamos:**

| Política | Falsos positivos | Falsos negativos | USD por reclamo | USD anuales proyectados |
|---|---:|---:|---:|---:|
| Umbral 14,3% | 222 | 24 | 22,84 | 8.908.877 |
| Umbral 50% | 6 | 102 | 38,57 | 15.042.857 |
| Priorizar todos | 605 | 0 | 37,76 | 14.726.422 |
| No priorizar ninguno | 0 | 116 | 43,44 | 16.941.470 |

Para el umbral económico: (222×45 + 24×270)/721 = **USD 22,84 por reclamo**. Multiplicamos por 390.000 para la proyección anual, cifra indicada por el caso; no por las 390.886 filas del archivo.

Detecta **92/116 = 79,3%** de incumplimientos; prioriza **314/721 = 43,6%** de los reclamos; precisión **92/314 = 29,3%**. Esa baja precisión no invalida por sí sola la política: toleramos más falsas alarmas porque el error opuesto es más caro. Accuracy baja a 65,9%, aunque el costo mejora: cada métrica responde una pregunta distinta.

Frente a priorizar todos, la mejor política constante elegida en desarrollo, la proyección ahorra **USD 5,817,545 anuales**. Frente a 0,5 ahorra aproximadamente USD 6,13 millones. Son proyecciones bajo la matriz simplificada, representatividad y probabilidades útiles; **no ahorro real probado, no presupuesto completo y no causalidad**. Sin capacidad suficiente para priorizar 43,6%, habría que incorporar esa restricción a una decisión nueva.

## 10. Escalado y unidades: qué demuestra el experimento

Probamos lineal, KNN y árbol con/sin escalado y distancia en km/m. Son 12 combinaciones, mismos datos, imputación, codificación y folds. Solo buscamos vecinos y profundidad.

- **KNN:** usa distancias. Con escalado elige 101 vecinos y da RMSE 276,05 h en km y metros. Sin escalar, pasar a metros cambia el mejor k de 101 a 401. La primera grilla terminaba en 401; ampliamos hasta 803 y 1.605, y 401 quedó interior. Eso permite defender que no cortamos el barrido justo en el óptimo aparente.
- **Árbol:** elige profundidad 1 por RMSE en las cuatro ramas y obtiene 275,82 h. Uno es límite físico inferior; no existe profundidad positiva menor. Escalar o convertir unidades preserva el orden y los cortes posibles. En esta ejecución sus predicciones coinciden.
- **Lineal sin penalización:** predicciones prácticamente invariantes al escalado positivo; coeficientes compensan unidades. En metros sin escalado aparece una pequeña diferencia por condicionamiento numérico y empates/rango de matriz. Con escalado la diferencia máxima de predicciones por conversión es aproximadamente 1,5×10⁻¹² h.

No decimos «escalar siempre mejora todo». KNN cambia geometría; el árbol usa orden; mínimos cuadrados puede reparametrizar. El propósito es explicar sensibilidad, no elegir ganador.

## 11. Reglas: quién puede aplicarlas y qué se pierde

El árbol de clasificación tiene profundidad 3, máximo ocho hojas, y mínimo 30 reclamos por hoja. Son valores fijados por legibilidad y soporte; no se buscaron por AUC. Usamos numéricas sin escalar para leer cortes en sus unidades.

Su AUC de CV es **0.758**, frente a **0,770** de logística. Gana rapidez de lectura: hasta tres condiciones, aplicables por un supervisor con información de ingreso. Pierde flexibilidad, y las tasas por hoja dependen de los reclamos usados para construirlo. Las tasas de las reglas siguientes son de desarrollo, no una validación independiente de cada hoja.

- Hoja 3: **situación de agua no es «CON AGUA» Y distancia desde el centro (km) ≤ 5.580 Y hora de ingreso ≤ 14.825**. 253 reclamos, incumple 0.4%; diferencia frente a prevalencia -15.7 puntos; acción económica: Cola normal.
- Hoja 4: **situación de agua no es «CON AGUA» Y distancia desde el centro (km) ≤ 5.580 Y hora de ingreso > 14.825**. 60 reclamos, incumple 3.3%; diferencia frente a prevalencia -12.8 puntos; acción económica: Cola normal.
- Hoja 6: **situación de agua no es «CON AGUA» Y distancia desde el centro (km) > 5.580 Y departamento no es «MONTEVIDEO»**. 547 reclamos, incumple 2.7%; diferencia frente a prevalencia -13.4 puntos; acción económica: Cola normal.
- Hoja 7: **situación de agua no es «CON AGUA» Y distancia desde el centro (km) > 5.580 Y departamento es «MONTEVIDEO»**. 228 reclamos, incumple 11.4%; diferencia frente a prevalencia -4.7 puntos; acción económica: Cola normal.
- Hoja 10: **situación de agua es «CON AGUA» Y departamento no es «MONTEVIDEO» Y día de semana (0=lunes, 6=domingo) no es «4»**. 887 reclamos, incumple 14.3%; diferencia frente a prevalencia -1.8 puntos; acción económica: Priorizar.
- Hoja 11: **situación de agua es «CON AGUA» Y departamento no es «MONTEVIDEO» Y día de semana (0=lunes, 6=domingo) es «4»**. 184 reclamos, incumple 32.6%; diferencia frente a prevalencia +16.5 puntos; acción económica: Priorizar.
- Hoja 13: **situación de agua es «CON AGUA» Y departamento es «MONTEVIDEO» Y distancia desde el centro (km) ≤ 8.085**. 334 reclamos, incumple 14.4%; diferencia frente a prevalencia -1.7 puntos; acción económica: Priorizar.
- Hoja 14: **situación de agua es «CON AGUA» Y departamento es «MONTEVIDEO» Y distancia desde el centro (km) > 8.085**. 390 reclamos, incumple 47.4%; diferencia frente a prevalencia +31.3 puntos; acción económica: Priorizar.

Las hojas 10 y 13 quedan cerca de la prevalencia general (16,1%): no son segmentaciones fuertes, aunque su tasa supere el umbral económico. La hoja 14, por ejemplo, tiene 390 casos y 47,4% de incumplimiento, casi tres veces la prevalencia; eso es un contraste operativo visible, pero depende de columnas didácticas y no diagnostica zonas de OSE.

El dibujo del árbol muestra clase mayoritaria con umbral 0,5; por eso todas las hojas pueden decir «No incumple». La tabla de acciones usa 0,143 y sí prioriza algunas. No confundir etiqueta mayoritaria con política por costos. Para valores faltantes, se aplican medianas del entrenamiento publicadas en la sección; no se inventan datos manualmente.

## 12. Autocrítica que se puede defender

Elegimos una fragilidad concreta: **particiones aleatorias como aproximación a reclamos futuros independientes**. Diferentes reclamos pueden pertenecer a la misma rotura o corte y compartir resolución. Eliminar copias exactas no resuelve eso. Sin identificador de incidente no sabemos separar episodios.

Si la hipótesis falla, AUC/AP y ahorro anual pueden estar sobreestimados. El test también es aleatorio: no corrige esa fragilidad. Proponemos conseguir agrupación por incidente/ubicación y validar un período posterior. Una caída confirmaría dependencia de esa decisión; estabilidad en episodios y meses nuevos la debilitaría. No decimos «puede haber overfitting» sin identificar qué decisión y qué números cambiarían.

## 13. Recomendación y límites

Recomendamos estudiar logística honesta con umbral económico bajo los supuestos del ejercicio. El modelo de horas elegido en desarrollo es Lasso. En test tiene MAE **78.70 h** frente a 82,95 h de base, y RMSE **204.70 h** frente a 217,94 h. Son mejoras acotadas; la CV es muy variable por la cola. No presentamos eso como una estimación precisa por reclamo.

No podemos afirmar: que esas cifras representen exactamente a toda OSE; que las columnas didácticas describan su operación real; que los excluidos tengan igual riesgo; que MAR esté probado; que una cuadrilla reduzca causalmente tiempos como predice el histórico; que hay capacidad para todas las prioridades; ni que la proyección económica sea ahorro observado.

## Preguntas rápidas para practicar

**¿Qué es FP acá?** Priorizar un reclamo que no iba a superar 72 horas: USD 45. **¿FN?** No priorizar uno que sí iba a superarlas: USD 270.

**¿Qué pasa exactamente a las 72 horas?** No incumple, porque el caso dice superar. **¿Y -1?** No es «cumple», es objetivo ausente o inválido y se excluye antes de etiquetar.

**¿Por qué no usar satisfacción, si predice bien?** Se conoce después; su exclusión temporal manda sobre desempeño.

**¿Por qué no Random Forest o boosting?** No se piden; priorizamos todas las secciones obligatorias. No hay desempeño mínimo.

**¿Por qué reservar test si ya hay CV?** CV sirve para elegir y comparar; test estima la elección con reclamos no usados para esa selección. No elimina todos los sesgos del caso.

**¿Por qué no class_weight='balanced'?** Queremos probabilidades de la prevalencia original para aplicar costos sin una corrección adicional; recall se modifica con umbral, no necesariamente alterando entrenamiento.

**¿Por qué mejora AUC pero casi no accuracy a 0,5?** AUC usa ordenamiento de todas las probabilidades; accuracy usa una decisión puntual. La mayoría de los riesgos no llega a 50%.

**¿Qué entendemos por reproducible?** Rutas centralizadas, datos originales y hashes, semilla fija, dependencias, ingesta y unión visibles, pipeline y notebook ejecutable desde un kernel limpio.

**¿Qué aprendió el trabajo?** Que prevenir fuga y elegir política por costos puede importar más que perseguir una métrica alta. También que es válido concluir que una tarea aporta poco si lo demostramos.

## Qué revisar entre los cuatro antes de entregar

1. Cada integrante debe explicar cómo se construye la etiqueta y por qué se excluye información futura.
2. Rehacer a mano la cuenta de USD 22,84 y explicar por qué accuracy baja cuando cambia el umbral.
3. Leer sección 12 y distinguir estimación histórica, datos didácticos, proyección anual y efecto causal.
4. Abrir el notebook ejecutado y comprobar que estas cifras aparecen en sus salidas. Entregar por Moodle: GitHub no sustituye esa entrega.

## Fuentes

- Consigna del grupo: `consigna-proyecto-reclamos-ose.pdf` (incluida junto al notebook).
- [Repositorio de la cátedra UCU](https://github.com/ucudal/Machine-Learning---Ingenieria-en-IA-y-CD): complemento y condiciones de uso del material; entrega por Moodle.
- [Datos y metadatos oficiales de OSE](https://datos.ose.com.uy/dataset/reclamos-operativos).
- [scikit-learn: preparación y leakage](https://scikit-learn.org/stable/common_pitfalls.html).
- [scikit-learn: validación cruzada](https://scikit-learn.org/stable/modules/cross_validation.html).
