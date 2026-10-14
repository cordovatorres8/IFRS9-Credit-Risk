# Modelado de la Probabilidad de Incumplimiento (PD)

## Descripción general

Este módulo desarrolla un marco de modelado de la Probabilidad de Incumplimiento (PD, por sus siglas en inglés) como parte fundamental del cálculo de provisiones bajo IFRS 9, dentro de un proyecto educativo de riesgo crediticio.

El objetivo es estimar la probabilidad de que un prestatario experimente un evento de morosidad grave (90+ días de retraso) dentro de un horizonte de predicción definido (12 a 24 meses).

El flujo de trabajo sigue un proceso completo de desarrollo de modelos de riesgo de crédito que incluye:

- Análisis exploratorio de datos (EDA)
- Evaluación de la calidad de los datos y detección de duplicados
- Ingeniería de características con estricto control de fuga de información (leakage-safe)
- Desarrollo de un modelo base interpretable
- Desarrollo de un modelo retador
- Validación del modelo
- Evaluación de la calibración
- Monitoreo mediante el Índice de Estabilidad Poblacional (PSI)


---

## Conjunto de datos

## Conjunto de datos

El ejercicio utiliza el conjunto de datos público **Give Me Some Credit** (150.000 observaciones).

La variable objetivo (*target*) es:

`SeriousDlqin2yrs`

donde:
- `1` = morosidad grave de 90 o más días en un plazo de dos años.
- `0` = cumplimiento sin morosidad grave en el horizonte de dos años.

La tasa de incumplimiento global de la cartera es de aproximadamente **6,68%**.

Los datos originales y procesados se encuentran excluidos del control de versiones mediante `.gitignore`.

---

## Estrategia de modelado

Se desarrollaron dos modelos comparativos:

### 1. Regresión logística — Modelo campeón
La regresión logística fue seleccionada como modelo campeón por su:
- **Interpretabilidad total y transparencia**: permite auditar el impacto marginal de cada variable crediticia.
- **Cumplimiento de estándares de gobierno de modelos**: facilita la construcción de scorecards bancarios estándar.
- **Robustez y estabilidad**: menor sensibilidad al sobreajuste frente a cambios estructurales de cartera.

El modelo fue entrenado utilizando transformaciones e imputaciones estimadas exclusivamente en la muestra de entrenamiento (*leakage-safe*).

### 2. XGBoost — Modelo retador
Se entrenó un modelo no lineal basado en árboles de gradiente (*Gradient Boosted Trees*) para evaluar el margen de ganancia predictiva frente al enfoque lineal.

---

## División de los datos

La muestra se dividió mediante una partición estratificada por la variable objetivo (80/20, semilla fija):

| Muestra | Observaciones | Tasa de incumplimiento observada |
|---|---:|---:|
| **Entrenamiento (Train)** | 120.000 | 6,68% |
| **Validación (Test)** | 30.000 | 6,68% |

---

## Variables predictoras

El conjunto final de modelado cuenta con 14 variables de comportamiento y solvencia:
- Edad del titular (`age`)
- Razón de endeudamiento (`DebtRatio`)
- Utilización de líneas revolventes (`RevolvingUtilizationOfUnsecuredLines`)
- Ingreso mensual (`MonthlyIncome`)
- Número de dependientes (`NumberOfDependents`)
- Líneas de crédito abiertas y préstamos (`NumberOfOpenCreditLinesAndLoans`)
- Préstamos hipotecarios o líneas con garantía inmobiliaria (`NumberRealEstateLoansOrLines`)
- Frecuencia histórica de morosidades leves (30-59 días) y moderadas (60-89 días)
- Morosidades graves pasadas (90+ días)
- Indicadores derivados de carga y severidad de atrasos
- Ratio de ingresos por línea crediticia activa
- Total de pagos atrasados
- Máximo número de pagos atrasados
- Severidad de los pagos atrasados
- Carga de pagos atrasados
- Ingreso por línea de crédito

---

## Desempeño de los modelos

La discriminación se evaluó mediante el Área bajo la Curva ROC (AUC-ROC), el coeficiente Gini y el estadístico Kolmogorov-Smirnov (KS):

| Módulo / Modelo | AUC | Gini | KS |
|---|---:|---:|---:|
| **Regresión Logística (Champion)** | **0.8628** | **0.7257** | **0.5685** |
| **XGBoost (Challenger)** | **0.8700** | **0.7401** | **0.5835** |

XGBoost obtuvo un desempeño predictivo ligeramente superior en las tres métricas de discriminación. Sin embargo, la mejora fue moderada frente a la pérdida de transparencia, por lo que la regresión logística se mantiene como modelo campeón y XGBoost se conserva como modelo retador.


> **Se ratifica la Regresión Logística como Modelo Champion para gobernanza y reporte IFRS 9, reteniendo a XGBoost como Challenger de validación.**

> **Se ratifica la Regresión Logística como Modelo Champion para gobernanza y reporte IFRS 9, reteniendo a XGBoost como Challenger de validación.**

---

## Calibración y bondad de ajuste

La calibración de probabilidades se evaluó mediante el **Brier Score** y el análisis por deciles de probabilidad predicha:

| Modelo | Brier Score | Calibración global |
|---|---:|---|
| **Regresión Logística** | 0.049421 | Adecuada y monotónica |
| **XGBoost** | 0.048588 | Ligeramente más compacta |

### Ordenamiento de riesgo por deciles
La cartera fue segmentada en 10 tramos de riesgo ordenados por la probabilidad predicha:

| Modelo | Tasa de default en decil 1 (bajo riesgo) | Tasa de default en decil 10 (alto riesgo) | Capacidad de ordenamiento |
|---|---:|---:|---|
| **Regresión Logística** | 0,30% | 35,97% | Excelente gradación |
| **XGBoost** | 0,40% | 37,20% | Excelente gradación |

---

## Monitoreo de estabilidad (PSI)

Se calculó el Índice de Estabilidad Poblacional (*Population Stability Index* - PSI) para evaluar posibles derivas de distribución entre la muestra de desarrollo y la muestra de validación o monitoreo:

* $\text{PSI} < 0.10$: Distribución estable.
* $0.10 \le \text{PSI} < 0.25$: Cambio moderado.
* $\text{PSI} \ge 0.25$: Deriva significativa (requiere recalibración).

### Estabilidad de la PD

| Modelo | PSI | Interpretación |
|---|---:|---|
| Regresión logística | 0.000519 | Estable |
| XGBoost | 0.000215 | Estable |

> **Nota:** En este ejercicio, las muestras de referencia y monitoreo provienen de una partición aleatoria del mismo conjunto de datos. Por lo tanto, el análisis PSI muestra estabilidad entre muestras, pero no una estabilidad temporal real. En un entorno de producción, el PSI debería calcularse con datos de una partición temporal o de una cartera reciente.


---

## Monitoreo de Estabilidad (PSI)

## Monitoreo de estabilidad (PSI)

Se calculó el Índice de Estabilidad Poblacional (*Population Stability Index* - PSI) para evaluar posibles derivas de distribución entre el conjunto de desarrollo y la muestra de validación:

* $\text{PSI} < 0.10$: Distribución estable.
* $0.10 \le \text{PSI} < 0.25$: Cambio moderado.
* $\text{PSI} \ge 0.25$: Deriva significativa (requiere recalibración).

### Resultados de estabilidad
* **Variables del modelo**: Las 14 variables presentaron valores de PSI inferiores a `0.001` (máximo: `income_per_credit_line_clean` con `0.000891`).
* **Estabilidad del score (PD)**:
  * Regresión Logística: $\text{PSI} = 0.000519$ (Estable).
  * XGBoost: $\text{PSI} = 0.000215$ (Estable).

---

## Cuadernos del módulo

| Cuaderno | Enfoque | Contenido principal |
|---|---|---|
| [`01_eda.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/01_eda.ipynb) | Exploración | Distribuciones, bivariados, correlaciones y detección de atípicos |
| [`02_data_quality.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/02_data_quality.ipynb) | Calidad de datos | Auditoría de valores nulos, registros duplicados y reglas de saneamiento |
| [`03_feature_engineering.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/03_feature_engineering.ipynb) | Ingeniería de features | Transformaciones no lineales y preprocesamiento sin fuga (*leakage-safe*) |
| [`04_logistic_pd.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/04_logistic_pd.ipynb) | Modelo campeón | Regresión logística, análisis de coeficientes e interpretabilidad |
| [`05_xgboost_challenger.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/05_xgboost_challenger.ipynb) | Modelo retador | Modelo de árboles con aumento de gradiente y validación cruzada |
| [`06_validation.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/06_validation.ipynb) | Validación | Curvas ROC, Gini, estadístico KS y calibración por deciles |
| [`07_monitoring.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/07_monitoring.ipynb) | Monitoreo | Cálculo de PSI por variable y por distribución de score |

---

## Conclusiones principales

El ejercicio de modelado de PD muestra que:

1. La ingeniería de características que evita la fuga de información mejora considerablemente el desempeño predictivo.
2. La regresión logística ofrece una sólida capacidad de discriminación y mantiene la interpretabilidad necesaria para auditorías y comités de riesgo.
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

