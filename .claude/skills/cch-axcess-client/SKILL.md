---
name: cch-axcess-client
description: Use when any 1065→CCH Axcess skill needs to WRITE data into CCH Axcess (Worksheets / Government Forms) or read back a field. The single sink — every skill writes through here. BRECHA — the actual write mechanism (official API vs UI automation) is undecided; this skill defines the contract so the rest can be built against it.
---

# cch-axcess-client — el sumidero (escribe en CCH Axcess)

> ⛔ **BRECHA / cuello de botella.** Sin esta skill no hay test end-to-end de nada.
> El *mecanismo* de escritura todavía no está decidido (ver "Decisión pendiente").
> Mientras tanto se define el **contrato** para que las demás skills se construyan contra él.

## Qué hace

Único punto que toca CCH Axcess. Autentica y **escribe** valores en campos de
Worksheets / Government Forms, y puede **leer** un campo de vuelta (para QA).

## Contrato (estable, independiente del mecanismo)

**write:**
```yaml
client: SALVIN7
field:                      # dirección lógica del campo en CCH
  form: "1065"
  worksheet: "Partner Information"
  line: "Ownership %"
  partner: "Partner 1"      # opcional, para campos por socio
value: 50.0
```
**read:** mismo `field` → devuelve el valor actual (para cross-check / diagnostic).

Toda skill de núcleo/módulo escribe **solo** a través de este contrato. Nunca tocan CCH
por su cuenta.

## Decisión pendiente (hay que resolver antes de codificar)
1. **¿API oficial de CCH Axcess?** (si existe endpoint de escritura a returns).
2. **¿Automatización de UI?** (Playwright/driver sobre la app) — frágil pero universal.
3. **¿Import por archivo?** (si CCH acepta un import estructurado).

La elección define cómo se implementa `write/read`; **no** cambia el contrato de arriba.

## Por qué un solo sumidero
- Un solo lugar con la auth y el manejo de errores de CCH.
- Las skills quedan testeables con un mock de este contrato aunque el mecanismo real
  todavía no exista.
