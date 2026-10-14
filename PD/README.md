# Modelado de Probabilidad de Incumplimiento (PD)

## Visión General

Este módulo desarrolla un marco de estimación de la **Probabilidad de Incumplimiento (*Probability of Default* - PD)** como parte fundamental del cálculo de provisiones bajo **IFRS 9**.

El objetivo es cuantificar la probabilidad de que un prestatario experimente un evento de mora grave (90+ días de retraso) dentro de un horizonte temporal definido (12 a 24 meses).

El flujo de trabajo cubre el ciclo de vida completo de un modelo de riesgo crediticio:

- Análisis Exploratorio de Datos (EDA)
- Evaluación de calidad de datos y detección de duplicados
- Ingeniería de características con estricto control de fuga de datos (*leakage*)
- Modelo Champion interpretable (Regresión Logística / Scorecard)
- Modelo Challenger avanzado (XGBoost)
- Validación cuantitativa (Curvas ROC, discriminación, matrices de confusión)
- Calibración por deciles de riesgo y Brier Score
- Monitoreo de estabilidad poblacional mediante el Índice de Estabilidad Poblacional (PSI)

---

## Dataset

El ejercicio utiliza el dataset público **Give Me Some Credit** (150.000 observaciones).

La variable objetivo (*target*) es:

`SeriousDlqin2yrs`

donde:
- `1` = mora grave de 90 o más días en un plazo de dos años.
- `0` = cumplimiento sin mora grave en el horizonte de dos años.

La tasa de incumplimiento global de la cartera es de aproximadamente **6,68%**.

Los datos originales y procesados se encuentran excluidos del control de versiones mediante `.gitignore`.

---

## Estrategia de Modelado

Se desarrollaron dos modelos comparativos:

### 1. Regresión Logística — Modelo Champion
La Regresión Logística fue seleccionada como el modelo Champion definitivo debido a:
- **Interpretabilidad total y transparencia**: Permite auditar el impacto marginal de cada variable crediticia.
- **Cumplimiento de estándares de gobierno de modelos**: Facilita la construcción de tarjetas de puntuación (*scorecards*) bancarias estándar.
- **Robustez y estabilidad**: Menor sensibilidad al sobreajuste frente a cambios estructurales de cartera.

El modelo fue entrenado utilizando transformaciones e imputaciones estimadas exclusivamente en el conjunto de entrenamiento (*leakage-safe*).

### 2. XGBoost — Modelo Challenger
Se entrenó un modelo no lineal basado en árboles de gradiente (*Gradient Boosted Trees*) para evaluar el margen de ganancia predictiva frente al enfoque lineal.

---

## Partición de Datos

La muestra se dividió mediante una partición estratificada por la variable objetivo (80/20, semilla fija):

| Muestra | Observaciones | Tasa de Incumplimiento Observada |
|---|---:|---:|
| **Entrenamiento (Train)** | 120.000 | 6,68% |
| **Validación (Test)** | 30.000 | 6,68% |

---

## Variables Predictoras

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

---

## Rendimiento de los Modelos

La discriminación se evaluó mediante el Área bajo la Curva ROC (AUC-ROC), el Coeficiente Gini y el estadístico Kolmogorov-Smirnov (KS):

| Módulo / Modelo | AUC | Gini | KS |
|---|---:|---:|---:|
| **Regresión Logística (Champion)** | **0.8628** | **0.7257** | **0.5685** |
| **XGBoost (Challenger)** | **0.8700** | **0.7401** | **0.5835** |

XGBoost logró un desempeño discriminante ligeramente superior en las tres métricas (+0,72% en AUC). Sin embargo, dada la magnitud moderada de la ganancia frente a la pérdida de transparencia:

> **Se ratifica la Regresión Logística como Modelo Champion para gobernanza y reporte IFRS 9, reteniendo a XGBoost como Challenger de validación.**

---

## Calibración y Bondad de Ajuste

La calibración de probabilidades se evaluó mediante el **Brier Score** y el análisis por deciles de probabilidad predicha:

| Modelo | Brier Score | Calibración Global |
|---|---:|---|
| **Regresión Logística** | 0.049421 | Adecuada y monotónica |
| **XGBoost** | 0.048588 | Ligeramente más compacta |

### Ordenamiento de Riesgo por Deciles
La cartera fue segmentada en 10 tramos de riesgo ordenados por la probabilidad predicha:

| Modelo | Tasa de Default en Decil 1 (Bajo Riesgo) | Tasa de Default en Decil 10 (Alto Riesgo) | Capacidad de Ordenamiento |
|---|---:|---:|---|
| **Regresión Logística** | 0,30% | 35,97% | Excelente gradación |
| **XGBoost** | 0,40% | 37,20% | Excelente gradación |

---

## Monitoreo de Estabilidad (PSI)

Se calculó el Índice de Estabilidad Poblacional (*Population Stability Index* - PSI) para evaluar posibles derivas de distribución entre el conjunto de desarrollo y la muestra de validación:

* $\text{PSI} < 0.10$: Distribución estable.
* $0.10 \le \text{PSI} < 0.25$: Cambio moderado.
* $\text{PSI} \ge 0.25$: Deriva significativa (requiere recalibración).

### Resultados de Estabilidad
* **Variables del Modelo**: Las 14 variables presentaron valores de PSI inferiores a `0.001` (máximo: `income_per_credit_line_clean` con `0.000891`).
* **Estabilidad del Score (PD)**:
  * Regresión Logística: $\text{PSI} = 0.000519$ (Estable).
  * XGBoost: $\text{PSI} = 0.000215$ (Estable).

---

## Cuadernos del Módulo

| Cuaderno | Enfoque | Contenido Principal |
|---|---|---|
| [`01_eda.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/01_eda.ipynb) | Exploración | Distribuciones, bivariados, correlaciones y detección de atípicos |
| [`02_data_quality.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/02_data_quality.ipynb) | Calidad de Datos | Auditoría de valores nulos, registros duplicados y reglas de saneamiento |
| [`03_feature_engineering.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/03_feature_engineering.ipynb) | Ingeniería de Features | Transformaciones no lineales y preprocesamiento sin fuga (*leakage-safe*) |
| [`04_logistic_pd.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/04_logistic_pd.ipynb) | Modelo Champion | Regresión Logística, análisis de coeficientes e interpretabilidad |
| [`05_xgboost_challenger.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/05_xgboost_challenger.ipynb) | Modelo Challenger | Modelo de árboles con aumento de gradiente y validación cruzada |
| [`06_validation.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/06_validation.ipynb) | Validación | Curvas ROC, Gini, estadístico KS y calibración por deciles |
| [`07_monitoring.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/PD/notebooks/07_monitoring.ipynb) | Monitoreo | Cálculo de PSI por variable y por distribución de score |

---

## Conclusiones Clave

1. El preprocesamiento y la ingeniería de variables sin fuga de información aumentan significativamente la robustez del modelo.
2. La Regresión Logística proporciona una capacidad de discriminación sobresaliente ($\text{AUC} = 0.8628$) a la vez que preserva la interpretabilidad necesaria para auditorías y comités de riesgo.
3. El ordenamiento monotónico de las tasas de mora observadas a lo largo de los 10 deciles confirma la validez del modelo para segmentar la cartera.
4. Las pruebas de estabilidad poblacional descartan derivas muestrales de corto plazo.