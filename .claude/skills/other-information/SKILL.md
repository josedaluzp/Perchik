---
name: other-information
description: Use to fill Schedule B / Other Information of a 1065 in CCH Axcess — FBAR, foreign partners, 1099 questions, exempt-from-filing. Stage 2. REGLA + MANUAL.
---

# other-information — Schedule B / Other Information (etapa 2)

## Qué hace
Responde las preguntas de Schedule B y la sección Other Information.

## Depende de
- **source-resolver** → `entity.record`, `partners.list`, `misc.form_1099`.
- **cch-axcess-client** → escribe.

## Mapeo / reglas
| Pregunta | Regla |
|----------|-------|
| Foreign partners? | `true` si partners.list tiene algún foreign |
| 1099 emitidos / requeridos | según `misc.form_1099` |
| **FBAR (punto 12)** | **"No de entrada"** — el diagnostic lo tira como error si queda vacío |
| Exempt from filing | confirmar numeración (¿punto 4 u 8? — a verificar) |

## Verificaciones
- Ningún campo de Schedule B vacío que el diagnostic exija.

## Brechas / a verificar (de pendientes v2.4)
- FBAR = "No de entrada" para no romper el diagnostic.
- Numeración "Exempt from filing": narrador dice punto 4, doc v2.3 dice punto 8. Confirmar.
