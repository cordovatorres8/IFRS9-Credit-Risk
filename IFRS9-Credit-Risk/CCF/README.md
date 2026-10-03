# CCF — Credit Conversion Factor

CCF requires sufficient information about undrawn/available exposure and drawn exposure around default.

A typical conceptual definition is:

`CCF = (EAD_at_default - drawn_exposure_at_observation) / available_undrawn_limit`

The exact definition must follow the chosen dataset and documented modelling convention.

**Do not create a CCF model from a dataset that lacks the required exposure/limit fields.**

This module is intentionally structured as an experimental portfolio component so that assumptions are visible and auditable.
