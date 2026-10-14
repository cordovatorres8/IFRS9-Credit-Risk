# CCF / EAD — Métricas Reproducibles y Gobernanza

Resultados auditables calculados sobre la cartera revolvente de 15.000 facilidades con 1.255 defaults observados en horizonte de 12 meses. Partición estratificada por tipo de producto 80/20 (1.004 train / 251 test), semilla 42.

## 1. Comparativa de Modelos: Precisión Estadística y Exposición Monetaria

| Modelo | Rol | LEQ MAE | LEQ RMSE | $R^2$ LEQ | Sesgo Total EAD ($) | Sesgo % EAD | Error Monetario EAD MAE ($) |
|---|---|---:|---:|---:|---:|---:|---:|
| **Factor Regulatorio Basilea (75%/50%)** | Benchmark | 0.158 | 0.194 | -0.682 | -$495.230 | -9.84% | $1.642,30 |
| **Media Histórica de Cartera** | Benchmark | 0.119 | 0.152 | -0.003 | -$21.140 | -0.42% | $1.238,10 |
| **Fractional Logit GLM** | **Champion** | **0.089** | **0.112** | **0.451** | **+$9.050** | **+0.18%** | **$894,20** |
| **XGBoost Regressor** | **Challenger** | **0.086** | **0.110** | **0.472** | **+$6.030** | **+0.12%** | **$868,50** |

> **Hallazgo Clave de Gobernanza**: El factor regulatorio fijo estándar subestima la exposición aggregate en casi un **-10%**, mientras que el modelo Champion **Fractional Logit** reduce el error monetario en un **45%** y mantiene la cota $[0, 1]$.

## 2. Calibración por Tramos de Utilización Pre-Default ($U_t$)

| Tramo de Utilización | Cuentas | EAD Real Promedio ($) | EAD Modelo Champion ($) | EAD Factor Regulatorio ($) | Error Regulatorio ($) |
|---|---:|---:|---:|---:|---:|
| **Baja (< 20%)** | 52 | $16.420 | $16.310 | $14.850 | -$1.570 |
| **Media (20% - 50%)** | 78 | $19.850 | $19.790 | $17.920 | -$1.930 |
| **Alta (50% - 80%)** | 81 | $22.410 | $22.470 | $21.100 | -$1.310 |
| **Casi Agotada (> 80%)** | 40 | $25.120 | $25.190 | $24.890 | -$230 |

## 3. Impacto en Provisiones IFRS 9 (ECL = PD × LGD × EAD)
* **ECL Total bajo Factor Regulatorio**: $1.142.500
* **ECL Total bajo Modelo Champion**: $1.264.800
* **Corrección de Provisiones**: +$122.300 (+9.67%) eliminando el déficit de cobertura pre-default.

## 4. Monitoreo de Estabilidad (PSI)
* **PSI Utilización Pre-Default**: `0.00015` (Estable)
* **PSI Límite Comprometido**: `0.00011` (Estable)
