---
name: print-efile
description: Use as the final step of a 1065 once QA is green — produce the Account/Client Copy and create the e-file (Form 8879-PE). Closing stage. CHECK.
---

# print-efile — cierre (Copy + e-file)

## Qué hace
Cierra el return: genera copias y crea el e-file.

## Depende de
- **cross-check-engine** y **diagnostic-runner** en verde.
- **cch-axcess-client**.

## Procedimiento
1. Generar **Account Copy / Client Copy**.
2. Crear el **e-file 8879-PE**.
3. (Opcional) guardar la Client Copy en Dropbox y marcar el estado en Airtable.

## Reglas
- No ejecutar si QA no pasó (`all_pass`/`clean` deben ser true).
- Confirmar antes de transmitir (acción de salida).
