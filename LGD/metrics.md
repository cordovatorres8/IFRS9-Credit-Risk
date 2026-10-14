# LGD — Métricas Reproducibles y Gobernanza de Modelos

Resultados auditables calculados sobre la población en default (`event == 1`, 1.817 observaciones). Partición estratificada por `purpose1` 80/20 (1.453 train / 364 test), semilla fija 42.

## 1. Comparativa de Modelos en Test Set

| Modelo | Tipo | MAE | RMSE | $R^2$ | Predicciones Fuera de [0, 1] | Racional de Selección |
|---|---|---:|---:|---:|---:|---|
| **Baseline** | Dummy Mean | 0.3005 | 0.3464 | -0.0003 | 0.0% | Benchmark no informativo |
| **Linear Regression** | Benchmark OLS | 0.2645 | 0.3261 | 0.1129 | 0.0%* | Modelo lineal estándar; sin garantía de cota |
| **Fractional Logit** | **Champion** | **0.2651** | **0.3266** | **0.1104** | **0.0% (Garantizado)** | **Cota matemática estricta $[0, 1]$, interpretable** |
| **Two-Stage Hurdle** | Alternativo | 0.2628 | 0.3261 | 0.1133 | 0.0% | Modela masa en cero + severidad |
| **XGBoost Regressor** | **Challenger** | **0.2612** | **0.3284** | **0.1009** | 0.0% | Captura no linealidades complejas |

*\*En esta muestra de prueba no hubo predicciones fuera de rango, pero OLS no garantiza dicha cota bajo extrapolación o estrés macroeconómico.*

## 2. Calibración por Deciles de LTV (Champion)

| Decil LTV | Rango LTV | Observaciones | LGD Real Promedio | LGD Predicha Promedio | Diferencia Absoluta |
|---|---|---:|---:|---:|---:|
| 1 | [0.00 - 0.40] | 46 | 21.4% | 22.1% | 0.7% |
| 2 | [0.40 - 0.55] | 45 | 24.8% | 25.3% | 0.5% |
| 3 | [0.55 - 0.68] | 46 | 28.1% | 28.4% | 0.3% |
| 4 | [0.68 - 0.80] | 45 | 31.9% | 31.5% | 0.4% |
| 5 | [0.80 - 0.92] | 46 | 34.2% | 33.9% | 0.3% |
| 6 | [0.92 - 1.05] | 45 | 37.6% | 36.8% | 0.8% |
| 7 | [1.05 - 1.25] | 46 | 42.1% | 40.5% | 1.6% |
| 8 | [1.25 - 1.98] | 45 | 53.4% | 51.8% | 1.6% |

## 3. Monitoreo de Estabilidad (PSI)
* **PSI de LTV**: `0.00012` (< 0.10, Altamente estable)
* **PSI de LGD Predicha**: `0.00018` (< 0.10, Altamente estable)

## 4. Pruebas de Estrés y Downturn LGD
* **LGD Baseline**: 31.61%
* **Escenario Downturn Leve (-10% valor colateral)**: 34.82% (+321 bps)
* **Escenario Downturn Severo (-20% valor colateral)**: 38.41% (+680 bps)
* **Escenario Crisis Extrema (-30% valor colateral)**: 42.65% (+1.104 bps)
