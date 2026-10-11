# CCF — Credit Conversion Factor / LEQ

## Estado del módulo

Se evaluó UCI **Default of Credit Card Clients** (Yeh, 2009; 30.000 filas; CC BY 4.0). [Ficha oficial](https://archive.ics.uci.edu/dataset/350/default%2Bof%2Bcredit%2Bcard%2Bclients). Incluye límite (`LIMIT_BAL`), facturas y pagos mensuales y un indicador de default el mes siguiente. No incluye EAD/saldo en default emparejado con saldo y límite en una fecha previa fija. Por ello es útil para ejercicios PD/utilización, pero **no permite observar CCF/LEQ** y no se reporta un modelo ni métricas de CCF.

## Definición escogida

Para líneas revolventes, el target principal del proyecto será Loan Equivalent Exposure (LEQ):

`LEQ = (EAD_T - Balance_t) / (Limit_t - Balance_t)`

con balance y límite medidos en una fecha previa fija y EAD al default. La literatura usa también CCF = EAD_T / Balance_t; la terminología varía. El código mantiene ambas convenciones separadas y no recorta automáticamente valores extremos. Denominadores cero/casi cero requieren tratamiento y reporte explícitos.

## Cuadernos

1. `01_data_requirements.ipynb`: consulta UCI, inspecciona metadatos y comprueba campos.
2. `02_target_construction.ipynb`: fórmulas, alineamiento temporal y ejemplo aritmético hipotético.
3. `03_ccf_model.ipynb`: omite el entrenamiento si faltan outcomes reales.
4. `04_validation.ipynb`: protocolo de validación y casos hipotéticos.

## Próximos datos necesarios

ID de facilidad/deudor, fecha de default, saldo y límite en observación pre-default fija, EAD/saldo al default, moneda, estado/cura y predictores medidos en esa fecha. Entonces se puede construir LEQ, separar temporalmente y por cliente, comparar baseline y regresión, y reportar métricas auténticas. Raw/processed/models están excluidos de Git.

**Conclusión:** el esqueleto CCF está completo como evaluación de factibilidad y metodología; el modelo empírico queda pendiente porque la fuente abierta seleccionada no identifica el target. No se sustituye por datos simulados ni proxy rotulado como CCF.


