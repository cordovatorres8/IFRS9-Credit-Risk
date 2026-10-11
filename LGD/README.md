# LGD — Loss Given Default

## Fuente y objetivo

Módulo educativo basado en el `lgd.csv` proporcionado (2.545 observaciones). El [diccionario fuente](https://github.com/JLZml/Credit-Scoring-Data-Sets/blob/master/6.%20Credit%20risk%20analysis/LGD/data%20description) define `lgd_time` como LGD; `Recovery_rate` como recuperación; `purpose1` como indicador de alquiler; y `event=1` como evento de default/cura, `event=0` como no evento. En el CSV las tasas están codificadas como proporciones. Se verificó que `lgd_time = 1 - Recovery_rate` con error máximo 1.11e-16.

El modelado se limita a `event=1` (1.817 filas); `event` solo filtra la población y no es predictor. El único predictor principal es `LTV`; `purpose1` queda como candidato si se confirma disponibilidad previa.

## Control de fuga

Excluir de X: `Recovery_rate`, `lgd_time`, `y_logistic`, `lnrr`, `Y_probit` y `event`. Recovery_rate es el complemento exacto del objetivo; las transformaciones derivan del target; la disponibilidad de event no está confirmada.

## Resultados ejecutados sobre el archivo adjunto

Split aleatorio estratificado por `purpose1`, 80/20, semilla 42 (1453 train / 364 test). Baseline de media: MAE **0.3005**, RMSE **0.3464**. Regresión lineal con LTV: MAE **0.2645**, RMSE **0.3261**, R² **0.1129**. No hubo predicciones fuera de [0,1] en este test. Resultados calculados directamente; CSV y filas individuales no se suben.

Se encontraron 120 filas repetidas (17 en event=1), sin ID para determinar su naturaleza. En `event=1`, LGD media=0.3195, mediana=0.1452; LTV máximo=1.984.

## Ejecución local

Guarde el CSV localmente como `LGD/data/raw/lgd.csv` y ejecute notebooks 01–06 en orden. Raw, processed y modelos están excluidos de Git. Instale `requirements.txt`.

## Límites

Sin fechas ni identificadores, no hay evaluación temporal ni agrupación por préstamo. La muestra es pequeña, modificada y anonimizada; no garantiza representatividad. Antes de uso real hacen falta cash flows/costos, descuento, madurez y censura del workout, datos temporales y validación independiente. Proyecto educativo, no implementación completa ni declaración de cumplimiento IFRS 9.
