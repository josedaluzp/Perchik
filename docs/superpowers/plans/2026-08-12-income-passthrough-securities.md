# Cerrar brechas income-passthrough-k1 / sale-of-securities — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Formalizar en las skills `income-passthrough-k1` y `sale-of-securities` la regla de
mapeo que hoy falta (marcada BRECHA en v2.3), usando los transcripts reales de los videos de
training como única fuente de verdad, y dejar los archivos de referencia relacionados sin
menciones de BRECHA.

**Architecture:** Es un cambio de documentación (4 archivos Markdown/YAML), no de código. Cada
tarea reescribe o edita un archivo siguiendo exactamente la regla ya aprobada en
`docs/superpowers/specs/2026-08-12-income-passthrough-securities-design.md`. La "verificación"
de cada tarea es un `grep` que confirma que el archivo no contiene más "BRECHA" y que contiene
las cifras/reglas exactas del spec (no hay tests automatizados porque no hay código).

**Tech Stack:** N/A — edición de Markdown/YAML en el repo `perchik-architecture-skills`.

## Global Constraints

- Fuente de verdad única: `trancript/salvin7-llc-consulting-fuera-de-usa/part1-3.txt` y
  `trancript/form-8949/part1.txt`. No inventar regla tributaria fuera de lo que dice el
  transcript.
- No tocar `cch-axcess-mcp/` (código) — este plan es independiente del bloqueo OAuth.
- Commits locales permitidos en este repo (política ya vigente para esta rama
  `feature/cch-axcess-mcp`), nunca push a ningún remoto.
- Ningún archivo debe quedar mencionando "BRECHA" al finalizar el plan.

---

### Task 1: Reescribir `income-passthrough-k1/SKILL.md`

**Files:**
- Modify: `.claude/skills/income-passthrough-k1/SKILL.md` (reescritura completa)

**Interfaces:**
- Consumes: ninguno (contenido ya validado en el spec 2026-08-12).
- Produces: el `SKILL.md` que lee `income-router` (solo por `description` del frontmatter,
  sin cambio de contrato) y que referencia `source-resolver` (Task 3).

- [ ] **Step 1: Reemplazar el contenido completo del archivo**

Reemplazar `.claude/skills/income-passthrough-k1/SKILL.md` por:

```markdown
---
name: income-passthrough-k1
description: Use when a 1065 entity is a holding that RECEIVES K-1s from other partnerships — loads each received K-1 line by line into Income › Partnership Passthrough (K-1 1065), aggregates real estate and interest into K-2 Section 10 (US Source), and excludes non-deductible expenses from K-2/K-3. An income module dispatched by income-router. REGLA + CHECK.
---

# income-passthrough-k1 — holding que recibe K-1

## Qué hace
Carga el income de una **holding** que recibe K-1 de otras sociedades, **línea por línea**,
en `Income › Partnership Passthrough (K-1 1065)`, y agrega el resultado al K-2/8804 de la
sociedad. No cubre la actividad propia de la holding (eso lo maneja el módulo de income que
corresponda, ej. income-consulting-foreign) — income-router enciende ambos en paralelo cuando
aplica.

## Depende de
- **source-resolver** → `income.k1_received`.
- **cch-axcess-client**.
- Coordina con **income-consulting-foreign** (o el módulo de actividad propia que dispare
  income-router) y con **balance-sheet**.

## 1. Carga por K-1, campo por campo
Por cada K-1 recibido: abrir `Income › Partnership Passthrough (K-1 1065)`, completar:
- Nombre de la sociedad emisora, tipo (domestic/limited), % de participación.
- Partner Capital Account Analysis.
- Cada casilla del K-1 real (net rental real estate income/loss, interest, deductions,
  non-deductible expenses, business interest expense, current year gross receipts, etc.) se
  tipea **1 a 1** en el campo del mismo nombre del worksheet — sin cálculo, transcripción
  directa.

*(Caso SALVIN7: 3 K-1 recibidos — Airport Crossing Investors, Cherokee Investors, Rose
Investors.)*

## 2. Agregación al K-2, Section 10 (US Source)
Asume que las sociedades emisoras de los K-1 recibidos son domésticas:

- **Línea 6 (Interest):** sumar el interest (box 5) de todos los K-1 recibidos → columna
  US Source. *(SALVIN7: 72 + 122 + 257 = 451.)*
- **Real estate (income o deductions según signo):** sumar el "net rental real estate
  income/loss" (box 2) de todos los K-1.
  - Si el neto es **positivo** → línea de INCOME correspondiente, columna US Source.
  - Si el neto es **negativo** → línea de DEDUCTIONS, columna US Source, sumándole el total
    de "Deductions" (box 13) de esos mismos K-1.
  *(SALVIN7: neto = −6.138 − 6.285 + 0 = −12.423; + (47+32+49) = **12.551**.)*

## 3. Excluir del K-2/K-3 los "non-deductible expenses"
Los non-deductible expenses de los K-1 recibidos bajan el capital account del socio en **su
propio** K-1, pero **no** deben cargarse en el K-2/K-3 de los socios de la sociedad que los
recibe.

## 4. Balance sheet
El ending capital account de cada K-1 recibido (Partner Capital Account Analysis, línea
final) se carga como inversión/"Other Asset" en el balance — una línea por cada sociedad de
la que se recibe K-1.

## 5. 8804
Solo entra la porción US-source (el resultado agregado de los K-1 recibidos, si es positivo)
prorrateada al socio corp según su %. La actividad foreign propia de la holding **nunca**
toca el 8804. *(SALVIN7: resultado negativo → 8804 en cero.)*

## Verificaciones (CHECK)
- **K-2 total == P&L net income**, con diferencia tolerada únicamente por los non-deductible
  expenses excluidos (regla 3). Diferencia mayor → no forzar el cierre, flaggear para revisión
  manual (`cross-check-engine`).
- **Σ ending capital account de todos los socios (K-1) == balance sheet "Partners' capital
  accounts"** al cierre. Si no cierra → revisión manual antes de imprimir.
- Si algún K-1 da ganancia real estate positiva y hay socio corp con % > 0 → confirmar
  explícitamente que impacta el 8804 línea 4a (no asumir 0).

*(Fuente: `trancript/salvin7-llc-consulting-fuera-de-usa/part1.txt`, `part2.txt`, `part3.txt`.)*
```

- [ ] **Step 2: Verificar que no queda BRECHA y que las cifras clave están**

Run:
```bash
grep -c "BRECHA" .claude/skills/income-passthrough-k1/SKILL.md
grep -c "12.551\|12,551" .claude/skills/income-passthrough-k1/SKILL.md
grep -c "REGLA + CHECK" .claude/skills/income-passthrough-k1/SKILL.md
```
Expected: primer comando → `0`; segundo y tercero → `1` o más (no `0`).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/income-passthrough-k1/SKILL.md
git commit -m "docs(income-passthrough-k1): formalizar regla de mapeo K-1 recibido (caso SALVIN7)"
```

---

### Task 2: Reescribir `sale-of-securities/SKILL.md`

**Files:**
- Modify: `.claude/skills/sale-of-securities/SKILL.md` (reescritura completa)

**Interfaces:**
- Consumes: ninguno.
- Produces: el `SKILL.md` que lee `income-router` (solo `description`) y que referencia
  `source-resolver` (Task 3).

- [ ] **Step 1: Reemplazar el contenido completo del archivo**

Reemplazar `.claude/skills/sale-of-securities/SKILL.md` por:

```markdown
---
name: sale-of-securities
description: Use to enter a sale of securities (stocks) for a 1065 in CCH Axcess via Form 8949 — short/long-term gains must be verified to stay excluded from Section 1446 withholding (CCH does not exclude them automatically). An insertable income module (Case C2). REGLA + CHECK.
---

# sale-of-securities — Form 8949 (∉ retención 1446)

## Qué hace
Carga venta de acciones en **Form 8949** y verifica que las ganancias **no** queden gravadas
por la retención de Section 1446. Es un **módulo insertable** (Caso C2), no un return
completo; se compone dentro de C1/C3 cuando hay venta de securities.

## Depende de
- **source-resolver** → `sale.securities_1099b`.
- **cch-axcess-client**.

## 1. Carga por venta, una fila por vez
`Income › Schedule D, 4797, Gain and Loss › Detail` — una fila por cada venta. Por cada
venta, copiar del 1099-B:
- Descripción (idéntica al 1099-B).
- Fecha de adquisición y fecha de venta.
- Precio de venta y costo.
- `1099-B Code = A`.
- Short/long term (> 1 año en la posición = long term).

## 2. Cross-check contra la fuente
El total cargado en Schedule D/8949 debe coincidir exacto (o con diferencia de redondeo ≤ $1)
con el total del 1099-B de origen.

## 3. La exclusión de Section 1446 NO es automática — es una verificación manual
Error a evitar: pensar que hay algo que "configurar" para excluir la ganancia. **CCH carga la
ganancia short/long-term en el 8804 línea 4e y en la retención por default**, igual que si
fuera income gravado. La regla operativa:
- Sumar el punto 9 de **todos** los 8805 de socios foreign → debe dar igual a la línea **4e**
  del 8804 (tolerancia ~$1 por redondeo).
- Sumar el punto 10 (retención) de todos los 8805 → debe dar igual a la retención total.
- **Si no cierra:** no ajustar montos a mano en el 8949 ni forzar el 8804/8805 — es señal de
  que hay otro income mezclado en el 4e (o falta un socio en el 8805). Flaggear para revisión
  manual.

## Verificaciones (CHECK)
- securities ∉ 1446 (regla 3, la verificación central de C2).
- Total 8949 == total 1099-B (regla 2).

*(Fuente: `trancript/form-8949/part1.txt`.)*
```

- [ ] **Step 2: Verificar que no queda BRECHA y que la regla 3 está**

Run:
```bash
grep -c "BRECHA" .claude/skills/sale-of-securities/SKILL.md
grep -c "NO es automática" .claude/skills/sale-of-securities/SKILL.md
grep -c "REGLA + CHECK" .claude/skills/sale-of-securities/SKILL.md
```
Expected: primer comando → `0`; segundo y tercero → `1` o más.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/sale-of-securities/SKILL.md
git commit -m "docs(sale-of-securities): formalizar verificacion manual de exclusion 1446 (Form 8949)"
```

---

### Task 3: Limpiar notas BRECHA en `sources.yaml`

**Files:**
- Modify: `.claude/skills/source-resolver/references/sources.yaml:122-132`

**Interfaces:**
- Consumes: nombres de las skills `income-passthrough-k1` / `sale-of-securities` (Task 1, 2 —
  ya existen, no cambian de nombre).
- Produces: ninguno (hoja del árbol de dependencias).

- [ ] **Step 1: Editar la entrada `income.k1_received`**

En `.claude/skills/source-resolver/references/sources.yaml`, reemplazar:

```yaml
  - key: income.k1_received
    needed_by: [income-passthrough-k1]
    connector: dropbox
    locator: { search_scope: clients_scope, name_contains: "{entity}", match: "K1*|K-1*", prefer: latest_year }
    notes: "Holding que RECIBE K-1. Puede estar en subcarpeta Investments. (BRECHA: regla propia)"
```

por:

```yaml
  - key: income.k1_received
    needed_by: [income-passthrough-k1]
    connector: dropbox
    locator: { search_scope: clients_scope, name_contains: "{entity}", match: "K1*|K-1*", prefer: latest_year }
    notes: "Holding que RECIBE K-1. Puede estar en subcarpeta Investments. Regla de mapeo: income-passthrough-k1/SKILL.md."
```

- [ ] **Step 2: Editar la entrada `sale.securities_1099b`**

En el mismo archivo, reemplazar:

```yaml
  - key: sale.securities_1099b
    needed_by: [sale-of-securities]
    connector: dropbox
    locator: { search_scope: clients_scope, name_contains: "{entity}", match: "*1099-B*|*Investment*", prefer: latest_year }
    notes: "Form 8949. Ganancias NO entran a retención 1446. (BRECHA)"
```

por:

```yaml
  - key: sale.securities_1099b
    needed_by: [sale-of-securities]
    connector: dropbox
    locator: { search_scope: clients_scope, name_contains: "{entity}", match: "*1099-B*|*Investment*", prefer: latest_year }
    notes: "Form 8949. Ganancias NO entran a retención 1446 (verificación manual, ver sale-of-securities/SKILL.md)."
```

- [ ] **Step 3: Verificar que no quedan menciones de BRECHA en el archivo**

Run:
```bash
grep -c "BRECHA" .claude/skills/source-resolver/references/sources.yaml
```
Expected: `0`.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/source-resolver/references/sources.yaml
git commit -m "docs(source-resolver): quitar notas BRECHA ya resueltas de sources.yaml"
```

---

### Task 4: Marcar como resueltos los 2 bullets en el doc de pendientes v2.4

**Files:**
- Modify: `docs/pendientes-mapping-v2.4-segun-videos.md:10-20`

**Interfaces:**
- Consumes: ninguno.
- Produces: ninguno (documento de seguimiento, no lo lee ninguna skill).

- [ ] **Step 1: Marcar el bullet de "Passthrough / Holding" como resuelto**

En `docs/pendientes-mapping-v2.4-segun-videos.md`, reemplazar:

```markdown
- [ ] **Camino "Passthrough / Holding" (sociedad que recibe K-1 de otras).** Caso SALVIN7: su income
      entra por 3 K-1 recibidos, cargados línea por línea en `Income › Partnership Passthrough
      (K-1 1065)`. Hoy el doc lo deja como 1 línea MANUAL fuera de R1 y admite que "Holding necesita
      regla propia". → Agregar una rama/sección en el árbol de Income (pg22) con el detalle de carga.
      *(Fuente: video SALVIN7 PI 12:00-15:00 · doc pg22-23, pg50)*
```

por:

```markdown
- [x] **Camino "Passthrough / Holding" (sociedad que recibe K-1 de otras).** Resuelto — regla
      formalizada en `.claude/skills/income-passthrough-k1/SKILL.md`. Ver
      `docs/superpowers/specs/2026-08-12-income-passthrough-securities-design.md`.
      *(Fuente: video SALVIN7 PI 12:00-15:00 · doc pg22-23, pg50 · transcript:
      `trancript/salvin7-llc-consulting-fuera-de-usa/`)*
```

- [ ] **Step 2: Marcar el bullet de "Form 8949" como resuelto**

En el mismo archivo, reemplazar:

```markdown
- [ ] **Form 8949 — securities NO gravados en la retención.** Las ganancias short/long term de
      acciones no entran a Section 1446, pero CCH las mete solo en el **8804 punto 4e**. Regla a
      documentar: excluirlas y verificar que **Σ punto 9 del 8805 (socios foreign) = 4e del 8804** y
      **punto 10 = retención**. → Agregar al mapeo/verificación del 8804/8805.
      *(Fuente: video Form 8949 · doc pg23 "Form 8949", sección 09)*
```

por:

```markdown
- [x] **Form 8949 — securities NO gravados en la retención.** Resuelto — regla formalizada en
      `.claude/skills/sale-of-securities/SKILL.md` (la exclusión de 1446 no es automática en CCH,
      es una verificación manual post-carga). Ver
      `docs/superpowers/specs/2026-08-12-income-passthrough-securities-design.md`.
      *(Fuente: video Form 8949 · doc pg23 "Form 8949", sección 09 · transcript:
      `trancript/form-8949/part1.txt`)*
```

- [ ] **Step 3: Verificar que ambos bullets quedaron marcados `[x]`**

Run:
```bash
grep -n "Passthrough / Holding\|Form 8949 — securities" docs/pendientes-mapping-v2.4-segun-videos.md
```
Expected: ambas líneas empiezan con `- [x]`.

- [ ] **Step 4: Commit**

```bash
git add docs/pendientes-mapping-v2.4-segun-videos.md
git commit -m "docs: marcar como resueltas las brechas de income-passthrough-k1 y sale-of-securities"
```
