# IFRS9-Credit-Risk

Proyecto de portafolio sobre modelado de riesgo de crédito inspirado en IFRS 9. Incluye:

- **PD (probabilidad de incumplimiento)**: regresión logística como modelo base y campeón interpretable, y XGBoost como modelo retador.
- **LGD (pérdida dado el incumplimiento)**: flujo de trabajo de regresión —incluida la regresión beta, según corresponda— condicionado a la variable objetivo disponible.
- **CCF (factor de conversión de crédito)**: flujo de trabajo experimental de cartera. El conjunto de datos debe contener información suficiente sobre exposiciones y límites para calcular un CCF observado.
- Validación, calibración, bandas de riesgo y monitoreo.

> **Importante:** Esta es una implementación educativa y de portafolio. No constituye una implementación regulatoria completa de IFRS 9 ni afirma cumplir con sus requisitos regulatorios.

## Estructura del repositorio

```text
IFRS9-Credit-Risk/
├── PD/
│   ├── data/raw/
│   ├── data/processed/
│   ├── notebooks/
│   ├── src/
│   ├── models/
│   └── README.md
├── LGD/
│   ├── data/raw/
│   ├── data/processed/
│   ├── notebooks/
│   ├── src/
│   ├── models/
│   └── README.md
├── CCF/
│   ├── data/raw/
│   ├── data/processed/
│   ├── notebooks/
│   ├── src/
│   ├── models/
│   └── README.md
├── common/
│   └── metrics.py
├── tests/
├── requirements.txt
└── .gitignore
```

Flujo de trabajo
1. Descarga manualmente los conjuntos de datos públicos y colócalos en la carpeta data/raw/ correspondiente.
2. Nunca subas credenciales, tokens de API ni datos bancarios sensibles al repositorio.
3. Ejecuta los notebooks en orden numérico.
4. Guarda los modelos entrenados en models/.
5. Documenta las hipótesis, limitaciones y resultados de validación.
Enfoque de modelado recomendado
PD
- Objetivo: incumplimiento dentro del horizonte de observación definido.
- Modelo campeón: regresión logística.
- Modelo retador: XGBoost.
- Métricas: ROC-AUC, Gini, KS, matriz de confusión y calibración.
- Monitoreo: PSI y estabilidad de la población y de las bandas de riesgo.
LGD
- Define cuidadosamente el objetivo de pérdida o recuperación.
- Cuando corresponda, separa las observaciones con incumplimiento de las que no lo presentan.
- Evalúa MAE, RMSE y el comportamiento de la distribución.
- Si utilizas un modelo acotado, documenta el tratamiento de los valores límite cero y uno.
CCF
No se debe fabricar un CCF a partir de un conjunto de datos que carezca de los campos de exposición y límite necesarios. Por eso, el proyecto incluye un flujo de trabajo que verifica la presencia de las columnas requeridas antes de modelar.
Ejecución local

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Then open Jupyter:

```bash
jupyter notebook
```
