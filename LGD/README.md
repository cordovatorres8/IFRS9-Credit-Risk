# Modelado de Severidad de la Pérdida (LGD)

## Visión General

Este módulo desarrolla un marco integral de estimación de la **Severidad de la Pérdida (*Loss Given Default* - LGD)** bajo los lineamientos de **IFRS 9** (Fase 3 y descuento de flujos recuperados) y **Basilea (IRB Avanzado CRE32)**.

El objetivo es cuantificar el porcentaje económico de pérdida sobre la exposición no recuperado una vez que se produce el incumplimiento:

$$\text{ECL} = \text{PD} \times \text{LGD} \times \text{EAD}$$

donde:

$$\text{LGD} = 1 - \text{Tasa de Recuperación} = \frac{\text{Pérdida Neta Económica}}{\text{Exposición al Incumplimiento (EAD)}}$$

El flujo de trabajo comprende:
- Análisis Exploratorio de Datos (EDA) sobre la distribución bimodal típica de recuperaciones hipotecarias
- Delimitación formal de la población en default (`event == 1`)
- Protocolo riguroso de prevención de fuga de información (*leakage*)
- Transformaciones no lineales de cobertura del colateral ($\text{LTV}$) y segmentación regulatoria
- Modelado múltiple (Línea base, Benchmark OLS, Champion Fractional Logit, Two-Stage Hurdle y Challenger XGBoost)
- Calibración por deciles de LTV y diagnóstico de residuos
- Validación por subgrupos de destino del crédito y sensibilidad a registros duplicados
- Monitoreo de estabilidad poblacional mediante el Índice de Estabilidad Poblacional (PSI)
- Pruebas de estrés macroeconómico y cálculo de **Downturn LGD**

---

## Dataset

Se utiliza la cartera hipotecaria europea del compendio *Credit Risk Analytics* (Baesens, Roesch y Scheule), compuesta por 2.545 contratos de crédito.

Variables principales:

| Variable | Descripción | Rol en el Flujo |
|---|---|---|
| `LTV` | Ratio Préstamo-Valor (*Loan-to-Value*, cobertura de la garantía) | Predictor primario de recuperación |
| `purpose1` | Indicador binario de destino (1 = Alquiler / Comercial, 0 = Vivienda propia) | Predictor secundario y variable de estratificación |
| `Recovery_rate` | Tasa de recuperación observada | Complemento algebraico ($1 - LGD$); excluida de $X$ |
| `lgd_time` | Severidad realizada ($[0, 1]$) | **Variable Objetivo (*Target*)** |
| `event` | Indicador de evento de default/cura (1 = default, 0 = no evento) | Filtro de población; excluido de $X$ |
| `y_logistic`, `lnrr`, `Y_probit` | Transformaciones del outcome | Derivadas posteriores al workout; excluidas |

Los datos crudos y procesados están excluidos de Git mediante `.gitignore`.

---

## Delimitación de Población y Control de Fuga

### 1. Condicionalidad al Default
Siguiendo las directrices internacionales, **la LGD se estima estrictamente sobre los contratos que entraron en default**:
$$\text{Muestra de Modelado} = \{i : \text{event}_i = 1\} \quad (N = 1.817)$$

Los contratos sin default (`event == 0`, 728 cuentas) no experimentan liquidación de garantías; incluirlos sesga artificialmente a la baja la estimación de la severidad.

### 2. Purga de Fuga Post-Default
Las variables derivadas de las recuperaciones posteriores (`Recovery_rate`, `y_logistic`, `lnrr`, `Y_probit`) fueron eliminadas. El conjunto predictivo se restringe a variables conocidas al momento exacto del default.

---

## Partición de Datos

La muestra en default se dividió mediante una partición estratificada por el destino del préstamo (80/20, estratificada por `purpose1`, semilla fija 42):

| Partición | Observaciones | Proporción Alquiler (`purpose1=1`) | LGD Media |
|---|---:|---:|---:|
| **Entrenamiento (Train)** | 1.453 | 8,88% | 32,10% |
| **Validación (Test)** | 364 | 8,79% | 31,62% |

---

## Ingeniería de Características

Para capturar la no linealidad de los costes de liquidación judicial y la pérdida acelerada en garantías deficitarias:
* $\log(\text{LTV})$: Suaviza la asimetría de los valores elevados de LTV.
* $\sqrt{\text{LTV}}$: Modela el rendimiento decreciente de la cobertura.
* $\text{LTV}^2$: Modela la aceleración cuadrática del quebranto en préstamos *underwater* ($\text{LTV} > 1.0$).
* $\text{LTV} \times \text{purpose1}$: Interacción de riesgo para inmuebles de inversión.
* **Tramos Regulatorios de LTV**: Segmentación ($<60\%$, $60-80\%$, $80-100\%$, $>100\%$) que refleja un incremento monotónico de la severidad promedio desde 23,1% hasta 54,2%.

---

## Estrategia de Modelado

Se evaluaron cinco arquitecturas sobre el conjunto de test independiente:

### 1. Fractional Logit GLM — Modelo Champion
El modelo Fraccional Logit (Papke & Wooldridge, 1996) es seleccionado como **Modelo Champion**:
* Utiliza una familia Quasi-Binomial con función de enlace Logit:
  $$E[\text{LGD} \mid X] = \frac{1}{1 + e^{-X\beta}}$$
* **Garantía Matemática**: Las predicciones están acotadas estrictamente en el intervalo $(0, 1)$, eliminando por diseño la posibilidad de predecir pérdidas negativas o superiores al 100%.
* Coeficientes directamente interpretables en términos de *odds ratios*.

### 2. XGBoost Regressor — Modelo Challenger
Modelo no lineal basado en árboles con aumento de gradiente que sirve como cota de referencia de aprendizaje automático.

### 3. Regresión Lineal OLS — Benchmark Lineal
Referencia clásica de mínimos cuadrados ordinarios.

### 4. Two-Stage Hurdle Model — Especialista Bimodal
Modela en dos etapas la masa en cero (créditos recuperados al 100%) y la severidad condicionada:
* Etapa 1: Clasificador logístico para la probabilidad de pérdida positiva ($\text{LGD} > 2\%$).
* Etapa 2: Regresión para la severidad en préstamos con pérdida efectiva.

---

## Rendimiento en el Conjunto de Test

| Modelo | Rol | MAE | RMSE | $R^2$ | MedAE | Predicciones Fuera de Rango |
|---|---|---:|---:|---:|---:|---:|
| **Baseline (Media)** | Benchmark | 0.3005 | 0.3464 | -0.0003 | 0.2810 | 0.0% |
| **Linear Regression** | Benchmark | 0.2645 | 0.3261 | 0.1129 | 0.2198 | 0.0%* |
| **Fractional Logit** | **Champion** | **0.2651** | **0.3266** | **0.1104** | **0.2178** | **0.0% (Garantizado)** |
| **Two-Stage Hurdle** | Alternativo | 0.2628 | 0.3261 | 0.1133 | 0.2180 | 0.0% |
| **XGBoost** | **Challenger** | **0.2612** | **0.3284** | **0.1009** | **0.1930** | 0.0% |

*\*En esta muestra de prueba no hubo predicciones fuera de rango, pero OLS no garantiza dicha cota bajo extrapolación o estrés macroeconómico.*

> **Racional de Selección Champion**: Se selecciona Fractional Logit por ofrecer la misma exactitud que OLS mientras garantiza el cumplimiento de las cotas económicas $[0, 1]$ y máxima transparencia regulatoria.

---

## Calibración por Deciles de LTV

El modelo Champion Fractional Logit presenta una calibración excelente en todos los tramos de cobertura de la garantía:

| Tramo LTV | Rango LTV | LGD Real Observada | LGD Predicha | Desviación Absoluta |
|---|---|---:|---:|---:|
| Decil 1 | $[0.00 - 0.40]$ | 21,4% | 22,1% | +0,7% |
| Decil 2 | $[0.40 - 0.55]$ | 24,8% | 25,3% | +0,5% |
| Decil 3 | $[0.55 - 0.68]$ | 28,1% | 28,4% | +0,3% |
| Decil 4 | $[0.68 - 0.80]$ | 31,9% | 31,5% | -0,4% |
| Decil 5 | $[0.80 - 0.92]$ | 34,2% | 33,9% | -0,3% |
| Decil 6 | $[0.92 - 1.05]$ | 37,6% | 36,8% | -0,8% |
| Decil 7 | $[1.05 - 1.25]$ | 42,1% | 40,5% | -1,6% |
| Decil 8 | $[1.25 - 1.98]$ | 53,4% | 51,8% | -1,6% |

---

## Pruebas de Estrés y Downturn LGD

Para cumplir con las exigencias de provisiones IFRS 9 prospectivas (*forward-looking*) y Basilea Downturn LGD, se simularon caídas en los precios inmobiliarios de las garantías:

| Escenario | Caída del Colateral | LTV Medio Estresado | Créditos en Déficit de Garantía | Downturn LGD | Incremento en Puntos Básicos |
|---|---:|---:|---:|---:|---:|
| **Baseline (Actual)** | 0% | 0,771 | 14,8% | 31,61% | — |
| **Downturn Leve** | -10% | 0,857 | 25,3% | 34,82% | +321 pbs |
| **Downturn Severo** | -20% | 0,964 | 42,0% | 38,41% | +680 pbs |
| **Crisis Extrema** | -30% | 1,101 | 61,5% | 42,65% | +1.104 pbs |

---

## Cuadernos del Módulo

| Cuaderno | Enfoque | Contenido Principal |
|---|---|---|
| [`01_eda.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/LGD/notebooks/01_eda.ipynb) | Exploración | Verificación de identidad $1 - RR$, distribución bimodal de LGD, dispersión LTV vs LGD |
| [`02_target_definition.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/LGD/notebooks/02_target_definition.ipynb) | Target y Población | Filtrado a `event == 1`, protocolo antifuga y partición estratificada 80/20 |
| [`03_feature_engineering.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/LGD/notebooks/03_feature_engineering.ipynb) | Ingeniería de Features | $\log(\text{LTV})$, $\text{LTV}^2$, interacciones y tramos regulatorios de LTV |
| [`04_lgd_model.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/LGD/notebooks/04_lgd_model.ipynb) | Modelado | Baseline, OLS, Fractional Logit (Champion), Two-Stage, XGBoost (Challenger) |
| [`05_validation.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/LGD/notebooks/05_validation.ipynb) | Validación | Calibración por decil, residuos, análisis por segmento y prueba con duplicados |
| [`06_monitoring.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/LGD/notebooks/06_monitoring.ipynb) | Monitoreo y Estrés | PSI de estabilidad y pruebas de estrés macroeconómico para Downturn LGD |

---

## Conclusiones Clave

1. La delimitación muestral a créditos fallidos (`event == 1`) es obligatoria para estimar la severidad real de cobro.
2. El modelo Fractional Logit elimina el riesgo de predecir valores fuera de $[0, 1]$ manteniendo la simplicidad requerida en riesgo de crédito.
3. La cobertura de la garantía inmobiliaria (LTV) explica la mayor parte de la variación de la pérdida.
4. El ejercicio de Downturn LGD demuestra que ante un choque de -20% en las tasaciones inmobiliarias, la provisión de severidad debe ajustarse en +680 puntos básicos.
