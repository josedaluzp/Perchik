---
name: diagnostic-runner
description: Use after cross-check-engine to run the CCH Axcess Diagnostic on a populated 1065 and interpret the errors/warnings it returns, mapping each to the skill that must fix it. QA stage. CHECK.
---

# diagnostic-runner — corre el Diagnostic de CCH

## Qué hace
Ejecuta el Diagnostic nativo de CCH Axcess e **interpreta** los errores, asignando cada
uno a la skill que lo debe resolver.

## Depende de
- **cch-axcess-client** → dispara el diagnostic y lee resultados.
- corre después de **cross-check-engine**.

## Salida
```yaml
diagnostics:
  - code: "FBAR"
    severity: error
    owner: other-information
    detail: "Punto 12 vacío → cargar 'No de entrada'"
  - code: "Balance"
    severity: error
    owner: balance-sheet
    detail: "Faltan buildings/land + amortización (aun con balance suprimido)"
clean: false
```

## Errores conocidos (de los videos)
- **FBAR (punto 12) vacío** → other-information lo pone en "No de entrada".
- **Balance suprimido** igual exige buildings/land + amortización → balance-sheet.

## Reglas
- No cerrar hasta `clean: true`.
