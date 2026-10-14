# Marco de Modelado de Riesgo de Crédito IFRS 9: PD, LGD y CCF/EAD

Marco integral y profesional de modelado de riesgo de crédito inspirado en la normativa **IFRS 9** (constitución de provisiones por pérdida crediticia esperada para Fase 1, Fase 2 y Fase 3) y los estándares del Comité de **Basilea (IRB Avanzado)**.

El repositorio implementa la tríada completa del cálculo de la Pérdida Crediticia Esperada (*Expected Credit Loss*):

$$\text{ECL} = \text{PD} \times \text{LGD} \times \text{EAD}$$

donde:
* **PD (*Probability of Default*)**: Probabilidad de que el prestatario incurra en incumplimiento en el horizonte de previsión.
* **LGD (*Loss Given Default*)**: Severidad o porcentaje económico de pérdida sobre la exposición no recuperado tras el proceso de cobranza y liquidación de garantías ($LGD = 1 - \text{Tasa de Recuperación}$).
* **EAD (*Exposure at Default*)**: Exposición total adeudada al momento exacto del incumplimiento, modelada para líneas revolventes mediante el Factor de Conversión Crediticia (**CCF** / **LEQ**).

---

## Estructura del Repositorio

```text
IFRS9-Credit-Risk/
├── PD/                 # Módulo de Probabilidad de Incumplimiento
│   ├── data/raw/       # Dataset Give Me Some Credit (150.000 clientes)
│   ├── data/processed/ # Variables transformadas libres de fuga de datos
│   ├── notebooks/      # 01 al 07 notebooks reproducibles (EDA -> Champion Logit -> Challenger XGBoost -> PSI)
│   ├── src/            # Pipelines modulares de preprocesamiento y entrenamiento
│   └── README.md       # Documentación exhaustiva, calibración y matrices de métricas
├── LGD/                # Módulo de Severidad de la Pérdida
│   ├── data/raw/       # Cartera hipotecaria europea en recuperación (2.545 contratos)
│   ├── data/processed/ # Población en default (event == 1) y transformaciones no lineales
│   ├── notebooks/      # 01 al 06 notebooks ejecutados (EDA -> Fractional Logit -> Downturn Stress Testing)
│   ├── src/            # Fractional Logit GLM, Modelo Two-Stage Hurdle y métricas de riesgo
│   ├── models/         # Modelos entrenados Champion y Challenger serializados
│   └── README.md       # Documentación completa, calibración por decil y pruebas de estrés
├── CCF/                # Módulo de Factor de Conversión Crediticia y Exposición al Incumplimiento (EAD)
│   ├── data/raw/       # Cartera revolvente emparejada temporalmente t -> T (15.000 facilidades)
│   ├── data/processed/ # Predictores de comportamiento pre-default y particiones estratificadas
│   ├── notebooks/      # 01 al 06 notebooks ejecutados (Auditoría -> LEQ Acotado -> Integración ECL)
│   ├── src/            # Fórmulas de target (LEQ vs CCF), Fractional Logit GLM, generador de cartera
│   ├── models/         # Estimadores Champion y Challenger serializados
│   └── README.md       # Documentación completa, análisis de sesgo monetario ($) e impacto en capital
├── common/
│   └── metrics.py      # Métricas comunes de riesgo (AUC, Gini, KS, Brier, PSI)
├── tests/              # Pruebas unitarias automatizadas (unittest)
├── requirements.txt    # Dependencias del proyecto
└── README.md           # Resumen general del proyecto
```

---

## Filosofía de Modelado y Gobierno de Riesgos

| Módulo | Definición del Objetivo | Modelo Champion | Modelo Challenger | Criterios Clave de Evaluación |
|---|---|---|---|---|
| **PD** | Incumplimiento grave a 24 meses (`SeriousDlqin2yrs`) | **Regresión Logística** (Scorecard Interpretable) | **XGBoost** | ROC-AUC, Gini, estadístico KS, Brier Score, deciles de riesgo |
| **LGD** | Severidad económica de pérdida ($LGD \in [0, 1]$) | **Fractional Logit GLM** (Quasi-Binomial) | **XGBoost Regressor** | MAE, RMSE, garantía estricta de cotas $[0, 1]$, Downturn LGD |
| **CCF / EAD** | Disposición de línea realizada ($\text{LEQ} \in [0, 1]$) | **Fractional Logit GLM** (Acotado) | **XGBoost Regressor** | Error estadístico LEQ, sesgo monetario de EAD ($), impacto en provisiones ECL |

---

## Resumen de Módulos

### 1. Probabilidad de Incumplimiento (PD)
* **Dataset**: *Give Me Some Credit* (150.000 acreditados, tasa de default global del 6,68%).
* **Modelo Champion**: Regresión Logística (AUC: **0.8628**, Coeficiente Gini: **0.7257**, Kolmogorov-Smirnov KS: **0.5685**).
* **Modelo Challenger**: XGBoost (AUC: **0.8700**, Gini: **0.7401**, KS: **0.5835**).
* **Monitoreo**: Índice de Estabilidad Poblacional (PSI) en las 14 variables y en las probabilidades predichas $< 0.001$ (estabilidad absoluta entre muestras).

### 2. Severidad de la Pérdida (LGD)
* **Dataset**: Cartera Hipotecaria Europea de Recuperación (2.545 préstamos; 1.817 contratos en default).
* **Modelo Champion**: Fractional Logit GLM (MAE: **0.2651**, RMSE: **0.3266**, $R^2$: **0.1104**, 0% de predicciones fuera de límites económicos).
* **Calibración**: Alta correlación y ajuste por deciles de LTV (desde 21,4% de LGD en el decil de bajo riesgo hasta 53,4% en el tramo de hipotecas *underwater* con LTV > 100%).
* **Downturn LGD (Estrés Macroeconómico)**: Una caída simulada del 20% en las tasaciones inmobiliarias eleva la LGD promedio de la cartera de 31,6% a 38,4% (+680 pbs), sirviendo de base para provisiones conservadoras IFRS 9.

### 3. Factor de Conversión Crediticia y EAD (CCF)
* **Dataset**: Cartera de crédito revolvente (15.000 líneas activas, 1.255 defaults observados en ventana de 12 meses pre-default).
* **Modelo Champion**: Fractional Logit GLM (MAE de LEQ: **0.089**, sesgo total de EAD: **+0.18%**, MAE monetario: **$894**).
* **Hallazgo Regulatorio**: El factor fijo estándar de Basilea (75%/50%) subestima la exposición real en un **-9,84%**; el modelo Champion corrige el déficit de provisiones en +$122.300 (+9,67%).

---

## Ejecución Local

### 1. Activar Entorno Virtual e Instalar Dependencias
```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Activar en macOS/Linux:
source .venv/bin/activate

# Instalar dependencias requeridas
pip install -r requirements.txt
```

### 2. Ejecutar los Cuadernos
Todos los notebooks en `PD/notebooks/`, `LGD/notebooks/` y `CCF/notebooks/` son completamente reproducibles y se encuentran pre-ejecutados con salidas y gráficos incrustados. Para abrirlos de manera interactiva:
```bash
jupyter notebook
```

### 3. Ejecutar Pruebas Automatizadas
```bash
python -m unittest tests/test_metrics.py
```

---

## Descargo de Responsabilidad (Disclaimer)
Este repositorio es un proyecto de portafolio técnico y educativo inspirado en las mejores prácticas de la industria bancaria y la normativa IFRS 9 / Basilea. No constituye una certificación regulatoria para su uso en producción sin previa calibración con flujos de recuperación internos de la entidad, tasas de descuento efectivas y validación de gobernanza independiente.
