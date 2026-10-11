# Modelado de la Probabilidad de Incumplimiento (PD)

## Descripción general

Este módulo desarrolla un marco de modelado de la Probabilidad de Incumplimiento (PD, por sus siglas en inglés) como parte de un proyecto educativo de riesgo de crédito bajo IFRS 9.

El objetivo es estimar la probabilidad de que un prestatario presente un evento de morosidad grave dentro de un horizonte de predicción definido.

El flujo de trabajo sigue un proceso de desarrollo de modelos de riesgo de crédito que incluye:

- Análisis exploratorio de datos (EDA)
- Evaluación de la calidad de los datos
- Ingeniería de características
- Desarrollo de un modelo base interpretable
- Desarrollo de un modelo retador
- Validación del modelo
- Evaluación de la calibración
- Monitoreo mediante el Índice de Estabilidad Poblacional (PSI)

---

## Conjunto de datos

El ejercicio utiliza el conjunto de datos público **Give Me Some Credit**.

El conjunto contiene información de crédito por prestatario y la variable objetivo:

`SeriousDlqin2yrs`

Donde:

- `1` = morosidad grave dentro de los dos años siguientes
- `0` = ausencia de morosidad grave dentro de los dos años siguientes

El conjunto original contiene 150.000 observaciones.

La tasa general de incumplimiento es aproximadamente **6,68 %**.

Los datos brutos y procesados están excluidos del control de versiones mediante `.gitignore`.

---

## Estrategia de modelado

Se desarrollaron dos modelos:

### 1. Regresión logística — Modelo campeón

La regresión logística fue seleccionada como modelo campeón por su:

- Interpretabilidad
- Transparencia
- Aplicabilidad a casos de riesgo de crédito
- Facilidad para explicar la relación entre los predictores y la probabilidad de incumplimiento

El modelo se desarrolló mediante ingeniería de características que evita la fuga de información. Los parámetros de transformación se estimaron exclusivamente con la muestra de entrenamiento.

### 2. XGBoost — Modelo retador

XGBoost se desarrolló como modelo retador para evaluar si un enfoque de aprendizaje automático no lineal podía mejorar el desempeño predictivo.

El modelo retador ofrece una mayor capacidad de discriminación, aunque es menos interpretable que la regresión logística.

---

## División de los datos

El conjunto de datos se dividió en muestras de entrenamiento y prueba mediante una partición estratificada:

| Muestra | Observaciones |
|---|---:|
| Entrenamiento | 120.000 |
| Prueba | 30.000 |

La tasa de incumplimiento se mantuvo aproximadamente en **6,68 %** en ambas muestras.

---

## Variables predictoras

El conjunto final de modelado, preparado para evitar la fuga de información, contiene 14 variables, entre ellas:

- Edad
- Relación entre deuda e ingresos
- Utilización del crédito
- Ingreso mensual
- Número de dependientes
- Líneas de crédito y préstamos abiertos
- Préstamos inmobiliarios
- Total de pagos atrasados
- Máximo número de pagos atrasados
- Indicador de atrasos de 90 días o más
- Indicador de cualquier pago atrasado
- Severidad de los pagos atrasados
- Carga de pagos atrasados
- Ingreso por línea de crédito

---

## Desempeño de los modelos

El desempeño se evaluó mediante el área bajo la curva ROC (AUC-ROC), el coeficiente de Gini y el estadístico de Kolmogórov-Smirnov (KS).

| Modelo | AUC | Gini | KS |
|---|---:|---:|---:|
| Regresión logística | 0.8628 | 0.7257 | 0.5685 |
| XGBoost | 0.8700 | 0.7401 | 0.5835 |

XGBoost obtuvo un desempeño predictivo ligeramente superior en las tres métricas de discriminación.

Sin embargo, la mejora fue moderada, mientras que la regresión logística ofrece una interpretabilidad considerablemente mayor.

Por lo tanto:

> **La regresión logística se mantiene como modelo campeón y XGBoost se conserva como modelo retador.**

---

## Calibración

La calibración de los modelos se evaluó mediante:

- El puntaje de Brier
- Curvas de calibración
- Tasas de incumplimiento predichas y observadas por decil

### Puntaje de Brier

| Modelo | Puntaje de Brier |
|---|---:|
| Regresión logística | 0.049421 |
| XGBoost | 0.048588 |

Ambos modelos mostraron una calibración razonable. Según el puntaje de Brier, XGBoost tuvo un resultado ligeramente mejor.

---

## Ordenamiento del riesgo

Las probabilidades predichas se evaluaron en diez deciles de riesgo.

El decil de mayor riesgo tuvo tasas observadas de incumplimiento considerablemente superiores a las del decil de menor riesgo.

Por ejemplo:

| Modelo | Decil de mayor riesgo | Decil de menor riesgo |
|---|---:|---:|
| Regresión logística | 35,97 % de incumplimiento observado | 0,30 % |
| XGBoost | 37,20 % de incumplimiento observado | 0,40 % |

Esto demuestra una sólida capacidad de discriminación y un ordenamiento significativo de los prestatarios según su riesgo.

---

## Monitoreo de estabilidad

Se calculó el Índice de Estabilidad Poblacional (PSI) para las variables del modelo y las distribuciones de PD predichas.

Umbrales de referencia:

| PSI | Interpretación |
|---:|---|
| < 0.10 | Estable |
| 0.10–0.25 | Cambio moderado |
| > 0.25 | Cambio significativo |

### Estabilidad de las variables

Las 14 variables monitoreadas tuvieron valores de PSI inferiores a 0.001.

El PSI más alto fue:

`income_per_credit_line_clean = 0.000891`

Este resultado indica una estabilidad muy alta entre las muestras de referencia y monitoreo.

### Estabilidad de la PD

| Modelo | PSI | Interpretación |
|---|---:|---|
| Regresión logística | 0.000519 | Estable |
| XGBoost | 0.000215 | Estable |

No se detectó un cambio material en las distribuciones.

> **Nota:** En este ejercicio, las muestras de referencia y monitoreo provienen de una partición aleatoria del mismo conjunto de datos. Por lo tanto, el análisis PSI muestra estabilidad entre muestras, pero no una estabilidad temporal real. En un entorno de producción, el PSI debería calcularse con datos de una partición temporal o de una cartera reciente.

---

## Notebooks

| Notebook | Descripción |
|---|---|
| `01_eda.ipynb` | Análisis exploratorio de datos |
| `02_data_quality.ipynb` | Evaluación de la calidad de los datos |
| `03_feature_engineering.ipynb` | Ingeniería de características y transformaciones que evitan la fuga de información |
| `04_logistic_pd.ipynb` | Modelo de PD con regresión logística |
| `05_xgboost_challenger.ipynb` | Modelo retador XGBoost |
| `06_validation.ipynb` | Validación y calibración del modelo |
| `07_monitoring.ipynb` | Monitoreo de estabilidad mediante PSI |

---

## Conclusiones principales

El ejercicio de modelado de PD muestra que:

1. La ingeniería de características que evita la fuga de información mejora considerablemente el desempeño predictivo.
2. La regresión logística ofrece una sólida capacidad de discriminación y mantiene la interpretabilidad.
3. XGBoost alcanza un desempeño predictivo moderadamente superior.
4. Ambos modelos ordenan a los prestatarios de manera significativa según su riesgo en los distintos deciles.
5. Ambos modelos muestran una calibración razonable.
6. No se detectó una inestabilidad significativa en la distribución de la muestra de validación.
7. La regresión logística se selecciona como **modelo campeón** y XGBoost se conserva como **modelo retador**.

---

## Aviso

Este proyecto es una implementación educativa y de portafolio inspirada en prácticas de modelado de riesgo de crédito bajo IFRS 9.

No pretende representar una implementación regulatoria completa de un modelo.

Un marco IFRS 9 de producción también requeriría elementos como:

- Consideraciones *point-in-time* y *through-the-cycle*
- Escenarios macroeconómicos
- Información prospectiva
- Pérdida crediticia esperada ponderada por probabilidad
- Gobierno del modelo
- Validación independiente
- Pruebas retrospectivas
- Gobierno de ajustes manuales
- Monitoreo con datos de cartera de períodos posteriores
