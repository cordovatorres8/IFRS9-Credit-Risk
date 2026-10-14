# Modelado de Factor de Conversión Crediticia (CCF / LEQ) y Exposición al Incumplimiento (EAD)

## Visión General

Este módulo desarrolla un marco completo de estimación del **Factor de Conversión Crediticia (*Credit Conversion Factor* - CCF / LEQ)** y la **Exposición al Incumplimiento (*Exposure at Default* - EAD)** bajo los lineamientos de **IFRS 9 (B5.5.30)** y **Basilea (CRE32)**.

En líneas de crédito revolventes (tarjetas de crédito, sobregiros en cuenta corriente y líneas comerciales), los acreditados disponen del derecho contractual a disponer de fondos adicionales antes de incumplir. Por ende, la exposición no puede asumirse estática:

$$\text{EAD}_T = \text{Saldo}_t + \text{CCF} \times (\text{Límite}_t - \text{Saldo}_t)$$

donde la convención estándar de la industria es el **Loan Equivalent Exposure (LEQ)**:

$$\text{LEQ} = \frac{\text{EAD}_T - \text{Saldo}_t}{\text{Límite}_t - \text{Saldo}_t} = \frac{\Delta \text{Disposición}}{\text{Línea No Utilizada}_t}$$

El flujo de trabajo comprende:
- Auditoría regulatoria de brecha sobre datasets públicos genéricos (p. ej. UCI Credit Card)
- Arquitectura de cartera de crédito revolvente emparejada temporalmente ($t \rightarrow T$)
- Formulación matemática del target (LEQ vs CCF sobre saldo) y prevención de división por cero
- Ingeniería de características de comportamiento pre-default (dinámica de uso, pagos y mora)
- Modelado comparativo (Benchmark Regulatorio de Basilea, Media Histórica, Champion Fractional Logit y Challenger XGBoost)
- Evaluación dual estadística y monetaria (MAE/$R^2$ de LEQ junto con el Sesgo Total en Dólares de EAD)
- Integración completa de la Pérdida Crediticia Esperada bajo IFRS 9 ($\text{ECL} = \text{PD} \times \text{LGD} \times \text{EAD}$)
- Monitoreo de estabilidad (PSI) y cuadro de alertas tempranas de aceleración de disposición

---

## Brecha de Datos Públicos y Cartera Revolvente

### 1. Por qué los Datasets Públicos Genéricos (como UCI) no son Aptos
Los datasets públicos habituales presentan historiales de facturación y morosidad de corto plazo, pero **carecen del saldo y límite en la fecha de observación pre-default emparejados con la exposición real al momento del default**. Emplear valores de facturas arbitrarios como proxy de EAD distorsiona gravemente las estimaciones. El Cuaderno 01 documenta formalmente esta auditoría.

### 2. Cartera Revolvente Emparejada Temporalmente
Para resolver esta deficiencia metodológica, el módulo incorpora una cartera revolvente representativa (`revolving_ccf_portfolio.csv`, 15.000 facilidades):

| Variable | Descripción | Rol en el Pipeline |
|---|---|---|
| `account_id` | Identificador único de la facilidad | Trazabilidad |
| `product_type` | Tipo de producto (`Credit Card`, `Overdraft`, `Revolving Line`) | Estratificación y segmentación |
| `credit_limit` | Límite de crédito contractualmente comprometido en $t$ | Cota máxima de línea |
| `balance_obs` | Saldo utilizado en la fecha de observación pre-default $t$ | Componente dispuesto |
| `utilization_obs` | Tasa de utilización en observación ($B_t / L_t$) | Predictor clave de comportamiento |
| `undrawn_obs` | Línea comprometida no dispuesta ($L_t - B_t$) | Denominador / margen disponible |
| `delinquency_bucket` | Estado de morosidad en $t$ (`0 DPD`, `1-29 DPD`, `30-59 DPD`) | Indicador de deterioro |
| `credit_score` | Puntuación crediticia en observación $t$ | Ordenamiento de solvencia |
| `payment_ratio` | Razón de pagos mensuales sobre saldo | Velocidad de amortización |
| `default_flag` | Incumplimiento a 12 meses (8,37% de tasa de default en cartera) | Filtro de población |
| `ead_at_default` | Exposición bruta efectiva en la fecha de default $T$ | **Resultado Realizado** |
| `realized_leq` | Porcentaje de disposición empírica sobre línea no utilizada | **Variable Objetivo (*Target*)** |

---

## Partición de Datos

La población de contratos en default (1.255 cuentas) se dividió mediante una partición estratificada por tipo de producto (80/20, estratificada por `product_type`, semilla fija 42):

| Partición | Cuentas | Tarjetas de Crédito | Sobregiros | Líneas Comerciales | LEQ Realizado Promedio |
|---|---:|---:|---:|---:|---:|
| **Entrenamiento (Train)** | 1.004 | 59,8% | 25,4% | 14,8% | 81,85% |
| **Validación (Test)** | 251 | 59,8% | 25,5% | 14,7% | 82,02% |

---

## Ingeniería de Características

Para capturar la aceleración del consumo de crédito antes del default sin incurrir en fuga de datos:
* `utilization_obs`: Nivel de utilización previa de la línea ($B_t / L_t$).
* `log_credit_limit`: Escala logarítmica del límite crediticio.
* `income_to_limit`: Razón de ingresos anuales sobre límite concedido.
* `util_sq`: Término cuadrático que captura el agotamiento de línea.
* `is_delinquent`: Indicador binario de morosidad previa.
* `util_delinq_inter`: Interacción de riesgo entre utilización y mora.
* **Tramos Regulatorios de Utilización**: Segmentos ($<20\%$, $20-50\%$, $50-80\%$, $>80\%$) que demuestran empíricamente la "paradoja de la utilización".

---

## Estrategia de Modelado

Se evaluaron cuatro enfoques bajo criterios de precisión estadística y error monetario de balance:

### 1. Fractional Logit GLM — Modelo Champion
El modelo Fraccional Logit es seleccionado como **Modelo Champion**:
* Garantiza estrictamente que las predicciones de LEQ se mantengan en el rango $[0, 1]$.
* Elimina el sesgo agregado de exposición de la cartera (+0,18%), previniendo distorsiones sistémicas de provisiones.
* Cumple plenamente con los requisitos de transparencia y auditoría bancaria.

### 2. XGBoost Regressor — Modelo Challenger
Modelo de árboles con aumento de gradiente que captura interacciones complejas de morosidad y saldo.

### 3. Factor Fijo Regulatorio de Basilea — Benchmark
Factores estándar regulatorios de Basilea (75% para tarjetas de crédito, 50% para sobregiros).

### 4. Media Histórica de LEQ — Benchmark Empírico
Promedio histórico global de disposición observado en el conjunto de entrenamiento (81,85%).

---

## Rendimiento en el Conjunto de Test

| Modelo | Rol | LEQ MAE | LEQ RMSE | LEQ $R^2$ | Sesgo Total EAD ($) | Sesgo % EAD | Error Monetario MAE ($) |
|---|---|---:|---:|---:|---:|---:|---:|
| **Factor Fijo Basilea (75%/50%)** | Benchmark | 0.158 | 0.194 | -0.682 | -$495.230 | **-9.84%** (Déficit) | $1.642,30 |
| **Media Histórica de Cartera** | Benchmark | 0.119 | 0.152 | -0.003 | -$21.140 | -0.42% | $1.238,10 |
| **Fractional Logit GLM** | **Champion** | **0.089** | **0.112** | **0.451** | **+$9.050** | **+0.18%** | **$894,20** |
| **XGBoost Regressor** | **Challenger** | **0.086** | **0.110** | **0.472** | **+$6.030** | **+0.12%** | **$868,50** |

> **Hallazgo Clave de Gobernanza**: El factor fijo de Basilea subestima la exposición en default en casi un **-10%**, generando un déficit estructural de cobertura. El modelo Champion **Fractional Logit** elimina prácticamente el sesgo agregado (+0,18%) y reduce el error monetario individual de exposición en un **45%**.

---

## Integración Integral de Provisiones IFRS 9 (ECL)

Integrando la EAD estimada con la PD de scorecards y la LGD de recuperación:

$$\text{ECL} = \text{PD} \times \text{LGD} \times \text{EAD}$$

| Métrica | Factor Fijo de Basilea (75%) | Modelo Champion CCF | Impacto / Ajuste de Provisión |
|---|---:|---:|---:|
| **Exposición Total Test (EAD)** | $4.538.200 | $5.042.480 | +$504.280 (+11,1%) |
| **Provisión Total IFRS 9 (ECL)** | $1.142.500 | $1.264.800 | +$122.300 (+9,67%) |

El modelo de CCF corrige la insuficiencia de reservas en facilidades donde los prestatarios en dificultades aceleran la disposición de fondos antes del impago definitivo.

---

## Monitoreo de Estabilidad (PSI) y Alertas Tempranas

| Variable Monitoreada | PSI | Interpretación |
|---|---:|---|
| **Utilización Pre-Default ($U_t$)** | 0.00015 | Altamente Estable ($\text{PSI} < 0.10$) |
| **Límite de Crédito Comprometido** | 0.00011 | Altamente Estable ($\text{PSI} < 0.10$) |

### Indicador Operacional de Alerta Temprana
Un algoritmo de semaforización clasifica las cuentas activas según la velocidad esperada de disposición:
* **Disposición Normal** ($<40\%$ disposición predicha): 25,1% de las cuentas.
* **Monitoreo Reforzado** ($40-70\%$ disposición predicha): 45,4% de las cuentas.
* **Acción Urgente Requerida** ($>70\%$ disposición predicha): 29,5% de las cuentas — señaladas para reducción preventiva de límite o reestructuración de deuda.

---

## Cuadernos del Módulo

| Cuaderno | Enfoque | Contenido Principal |
|---|---|---|
| [`01_data_requirements.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/CCF/notebooks/01_data_requirements.ipynb) | Requisitos de Datos | Auditoría de brecha de datasets públicos (UCI "NO-GO") y arquitectura temporal de cartera |
| [`02_target_construction.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/CCF/notebooks/02_target_construction.ipynb) | Construcción del Target | Derivación matemática de LEQ, manejo de divisiones por cero y dinámica de disposición |
| [`03_feature_engineering.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/CCF/notebooks/03_feature_engineering.ipynb) | Ingeniería de Features | Variables de comportamiento pre-default, tramos de uso y partición estratificada 80/20 |
| [`04_ccf_model.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/CCF/notebooks/04_ccf_model.ipynb) | Modelado | Factor Fijo Basilea, Media Histórica, Champion Fractional Logit y Challenger XGBoost |
| [`05_validation.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/CCF/notebooks/05_validation.ipynb) | Validación e Integración ECL | Calibración por tramos de uso y simulación integral de provisiones $\text{PD} \times \text{LGD} \times \text{EAD}$ |
| [`06_monitoring.ipynb`](file:///c:/Users/jhon_/Documents/GitHub/IFRS9-Credit-Risk/CCF/notebooks/06_monitoring.ipynb) | Monitoreo y Alertas | PSI de estabilidad y sistema de alertas operacionales de velocidad de disposición |

---

## Conclusiones Clave

1. Los factores fijos regulatorios ignoran el comportamiento de aceleración de deuda del deudor moroso, subestimando la exposición final en líneas revolventes activas.
2. El modelo Fractional Logit asegura predicciones acotadas en $[0, 1]$ y elimina el sesgo agregado de cartera.
3. El cálculo de provisiones IFRS 9 mediante un CCF modelado ajusta las reservas en un +9,7%, fortaleciendo la solvencia patrimonial del banco frente a crisis crediticias.
