# Pendientes para el Mapping 1065 v2.4 — brechas detectadas en los videos

Lista accionable de lo que **falta o hay que modificar** en el documento
`Mapping 1065 CCH Axcess Tenfold Perchik v2.3 (rev jun-2026).pdf`, según el análisis de los videos
de training (SALVIN7, Form 8949, AGGUILU). Fecha: jun-2026.
Detalle completo del análisis: `whisper-salvin/analisis_3casos_video_vs_doc.md`.

## Prioridad ALTA (brechas de mapeo reales)

- [x] **Camino "Passthrough / Holding" (sociedad que recibe K-1 de otras).** Resuelto — regla
      formalizada en `.claude/skills/income-passthrough-k1/SKILL.md`. Ver
      `docs/superpowers/specs/2026-08-12-income-passthrough-securities-design.md`.
      *(Fuente: video SALVIN7 PI 12:00-15:00 · doc pg22-23, pg50 · transcript:
      `trancript/salvin7-llc-consulting-fuera-de-usa/`)*

- [x] **Form 8949 — securities NO gravados en la retención.** Resuelto — regla formalizada en
      `.claude/skills/sale-of-securities/SKILL.md` (la exclusión de 1446 no es automática en CCH,
      es una verificación manual post-carga). Ver
      `docs/superpowers/specs/2026-08-12-income-passthrough-securities-design.md`.
      *(Fuente: video Form 8949 · doc pg23 "Form 8949", sección 09 · transcript:
      `trancript/form-8949/part1.txt`)*

- [ ] **8804 — distinguir socio CORP vs INDIVIDUAL.** En venta de propiedades, **4M/4Q (9c y 10−9c)
      impactan sólo el % de los socios individuales**; la **corp va por la línea 4A** (resultado de
      actividad − resultado de venta). Hoy el doc mapea 4e/4m/4q sin distinguir tipo de socio.
      → Agregar la distinción. *(Fuente: video AGGUILU PIII-PIV · doc pg24, pg28-29)*

- [ ] **Schedule M-2 (Increases/Decreases) en el escenario estándar.** Hoy sólo está mapeado en
      Escenario C (cambio accionario, pg31). SALVIN7 lo carga en el estándar (FOREIGN SERVICE INCOME
      / expenses) para que impacte en el balance. → Agregar filas de M-2 al Escenario A (pg24).
      *(Fuente: video SALVIN7 PII 01:00)*

## Prioridad MEDIA (campos/notas que faltan)

- [ ] **"Type of entity filing this return" (Domestic LLC)** — no es una fila en la tabla Other
      Information (pg17). Aparece en los tres videos. → Agregar fila.

- [ ] **Método contable (Cash / Accrual)** — sólo está como dato fuente (OA cl. 6.1 / pie del P&L);
      no es una fila de mapping en Basic Data – General (pg16). → Agregar fila.

- [ ] **Balance suprimido pero el diagnostic igual exige completar parte.** Aun suprimiendo el
      balance (<1M / <250k), el diagnostic obliga a completar **buildings/land activos + amortización
      acumulada** (sin las propiedades vendidas). → Agregar nota en la sección de Balance (pg24).
      *(Fuente: video AGGUILU PIII)*

- [ ] **K-2 a mayor granularidad (US source vs Foreign source).** Detallar las columnas y qué línea
      usa cada concepto: income real estate en fila 2 ESI/US Source, expenses punto 3 US Source,
      consulting foreign en columna Foreign, intereses línea 6 (US vs Non-US). Hoy el K-2 está mapeado
      grueso (pg21: "Section 10", ejemplo 50/50). → Enriquecer. *(Fuente: SALVIN7 PII · AGGUILU PIV)*

## Prioridad BAJA (tips operativos no documentados)

- [ ] **ERO – Electronic Return Originator (overrides):** marcar el primer punto. No figura. *(los 3 videos)*
- [ ] **Partners › General Options › K-1/K-3 Print** en el escenario estándar (produce for all
      partners · suppress state · also in client copy). Hoy sólo aparece en Escenario C (pg32).
- [ ] **Punto 12 / FBAR = "No de entrada"** porque el diagnostic lo tira como error si queda vacío.
- [ ] **Regla de redondeo del balance** (≥ 0.50 hacia arriba). *(SALVIN7 PII 03:00)*

## A VERIFICAR (posibles correcciones, requieren criterio de Perchik)

- [ ] **Regla de SSN/EIN del socio sin número.** El doc (pg20) la redacta por *tipo de actividad*
      (consulting-foreign/loss → `888-00-8888`; real estate con ganancia → `APPLIED FOR`). Pero en
      **SALVIN7 (consulting foreign)** y **AGGUILU (real estate con ganancia)** el socio **corp
      foreign se cargó como "Applied for"** en ambos. → ¿La regla en realidad la maneja el **tipo de
      entidad** (corp → Applied for)? Revisar y reescribir.

- [ ] **Business code de Consulting** — video SALVIN7 muestra ~`541600`; doc dice `541990`. Verificar
      (puede ser lectura parcial del frame).

- [ ] **Numeración "Exempt from filing"** — narrador dice "punto 4", doc lo mapea como "punto 8".
      Sólo nomenclatura; confirmar el número correcto.

---

### Lo que los videos CONFIRMARON (no tocar)
- Escenario B (venta de propiedades) validado **campo por campo** por AGGUILU: 100% disposed, Fair
  Rental Days, Building+Land en Sch D/4797, Sales price Building = P&L − Land, Unrecaptured gain
  O/R = Total depreciation → 9c, Form 4797 1A, cadena 9c/10/4m/4q/K-2/K-3.
- Form 8949 data-entry validado (description, fechas, costo, precio, 1099-B code A, short/long).
- Umbral de balance 1M/250k, Schedule B-1, Partner Information, 8805 por socio, verificación K-2/K-3.
