# LGD — Loss Given Default

This module is structured for a public loan/default dataset containing recovery or loss information.

Before modelling, explicitly define:

- default population;
- exposure basis;
- recoveries;
- costs, if available;
- observation/recovery window;
- LGD target and its bounds.

Do not manufacture an LGD target if the dataset does not provide enough information.

Recommended outputs:
- distribution of LGD;
- mean/median LGD;
- MAE/RMSE;
- segmentation by risk/product characteristics;
- sensitivity to zero/one boundary values.
