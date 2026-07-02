# Scheduled horario del 1065 + skill completion-report — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Envolver el flujo que ya funciona (armá el 1065 de X → mockup) en una Tarea Programada de Cowork cada 1h y agregar una skill `completion-report` que notifica por mail el cierre de cada entidad con los puntos a verificar.

**Architecture:** Los artefactos son archivos `SKILL.md` (markdown con frontmatter) + un `.yaml` de config, no código ejecutable. No hay test harness: cada tarea se verifica por estructura (frontmatter válido, secciones/claves presentes, referencias que existen) y la prueba de aceptación real es correr el flujo en Cowork con AGGUILU LLC. El flujo runtime es: `intake-trigger` (lee "CCH To do") → `return-orchestrator` (mockup) → `completion-report` (mail Gmail).

**Tech Stack:** Markdown (SKILL.md), YAML (source-resolver), conectores MCP (Airtable, Dropbox, Gmail) que viven en Cowork/Claude Desktop.

## Global Constraints

- **Idioma:** español, en el mismo tono que las skills existentes.
- **Solo lectura sobre Airtable:** nunca escribir `Primary Form Status` ni ningún otro estado.
- **Nunca escribir en CCH Axcess:** la subida real es costura futura (gated por credenciales sandbox).
- **No hardcodear** destinatarios ni IDs en las skills → todo dato de "dónde/quién" sale de `source-resolver`.
- **Sync manual:** las skills se editan en este repo pero corren en Cowork/Claude Desktop; no hay sync automático (se documenta el checklist de copia manual).
- **Frontmatter obligatorio** en cada SKILL.md: `name` (kebab-case, igual al folder) y `description`.
- **Fuente de verdad del diseño:** `docs/superpowers/specs/2026-07-01-scheduled-1065-completion-report-design.md`.

---

### Task 1: Config de destinatario del mail en source-resolver

**Files:**
- Modify: `.claude/skills/source-resolver/references/sources.yaml`

**Interfaces:**
- Produces: bloque `notifications.email.recipient` (string) que `completion-report` lee para saber a quién mandar el mail. Clave lógica: `notifications.email.recipient`.

- [ ] **Step 1: Agregar el bloque `notifications` al final de la sección `connectors` o como top-level nuevo**

En `sources.yaml`, después del bloque `connectors:` (antes de `# ---- sources ----`), agregar:

```yaml
# -----------------------------------------------------------------------------
# Notificaciones. A dónde/quién avisa completion-report al cerrar una entidad.
# -----------------------------------------------------------------------------
notifications:
  email:
    connector: gmail
    recipient: "josed@inforge.us"     # destinatario del mail de cierre (parametrizable)
    # send_mode: el conector Gmail vía MCP suele exponer solo create_draft.
    # "auto" = enviar si el conector lo permite; si no, dejar borrador. A confirmar en Cowork.
    send_mode: "auto"
```

- [ ] **Step 2: Verificar que el YAML sigue siendo válido y la clave existe**

Run:
```bash
python -c "import yaml,sys; d=yaml.safe_load(open('.claude/skills/source-resolver/references/sources.yaml',encoding='utf-8')); print(d['notifications']['email']['recipient'])"
```
Expected: imprime `josed@inforge.us` sin errores de parseo.

- [ ] **Step 3: Documentar la fuente nueva en el SKILL de source-resolver si lista sus claves**

Abrir `.claude/skills/source-resolver/SKILL.md`. Si enumera qué resuelve, agregar una línea:
`- notifications.email.recipient → destinatario del mail de cierre (lo consume completion-report).`
Si no enumera claves explícitamente, no tocar (el diccionario es `sources.yaml`).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/source-resolver/references/sources.yaml .claude/skills/source-resolver/SKILL.md
git commit -m "source-resolver: agrega config de destinatario del mail de cierre"
```

---

### Task 2: Contrato de salida de return-orchestrator hacia completion-report

**Files:**
- Modify: `.claude/skills/return-orchestrator/SKILL.md`

**Interfaces:**
- Produces: sección "Salida hacia completion-report" que declara el objeto que `completion-report` consume: `client`, `result` (success|failure), `reason`, `mockup` (ruta), `fields_by_status` (`auto`/`regla`/`check`/`manual`/`missing`), `qa` (`cross_checks`/`diagnostics`), `cch_upload` (done|pending).

- [ ] **Step 1: Agregar la sección de contrato tras "Resultado hacia intake-trigger"**

En `return-orchestrator/SKILL.md`, después de la sección "Resultado hacia intake-trigger", agregar:

```markdown
## Salida hacia completion-report

Además del mockup, cuando corre en flujo automático el orquestador expone un objeto que
`completion-report` consume para armar el mail (no re-calcula nada):

```yaml
client: AGGUILU LLC
result: success            # success | failure
reason: null               # motivo, solo si failure
mockup: "file:///C:/Users/PC/Downloads/1065_AGGUILU_mockup.html"
fields_by_status:          # derivado de los estados del mockup (AUTO/REGLA/CHECK/MANUAL)
  auto:   [ "<worksheet · línea>" ]   # cargados directo de la fuente
  regla:  [ "<worksheet · línea>" ]   # derivados por regla fiscal
  check:  [ "<worksheet · línea>" ]   # resueltos pero a verificar por una persona
  manual: [ "<worksheet · línea>" ]   # no están en las fuentes → carga humana
  missing:[ "<dato/fuente faltante>" ]
qa:
  cross_checks: "resumen de cross-check-engine"
  diagnostics:  "resumen de diagnostic-runner"
cch_upload: pending        # done | pending (pending mientras cch-axcess-client esté gated)
```

Los valores de `fields_by_status` salen del contador y las filas del mockup (columna Estado);
no es información nueva, es el mismo mockup en forma estructurada.
```

- [ ] **Step 2: Verificar que la sección quedó y nombra las 5 claves de estado**

Run:
```bash
grep -c -E "auto:|regla:|check:|manual:|missing:" .claude/skills/return-orchestrator/SKILL.md
```
Expected: `5` (o más).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/return-orchestrator/SKILL.md
git commit -m "return-orchestrator: declara la salida estructurada para completion-report"
```

---

### Task 3: Crear la skill completion-report

**Files:**
- Create: `.claude/skills/completion-report/SKILL.md`

**Interfaces:**
- Consumes: el objeto de salida de `return-orchestrator` (Task 2) y `notifications.email.recipient` de `source-resolver` (Task 1).
- Produces: un mail (enviado o borrador) vía conector Gmail + un `status` (`notified` | `draft_left` | `error`) para el resumen de `intake-trigger`.

- [ ] **Step 1: Crear el SKILL.md completo**

Crear `.claude/skills/completion-report/SKILL.md` con exactamente:

```markdown
---
name: completion-report
description: Use as the closing step for a 1065 once return-orchestrator produced the mockup — notifies by email (Gmail connector) that the 1065 of a client was completed, listing the points a person must verify (CHECK/MANUAL/missing), the QA summary and the mockup reference. Invoked by intake-trigger in the automated hourly flow. No escribe en Airtable ni en CCH.
---

# completion-report — el aviso de cierre (mail)

## Qué hace

Cierra el flujo de UNA entidad: toma el resultado de `return-orchestrator` y **arma + envía por
mail** (conector Gmail) el aviso de que el 1065 se completó, con los puntos que una persona debe
verificar. No toca Airtable ni CCH — solo notifica.

## Depende de
- **return-orchestrator** → el objeto de salida (`result`, `mockup`, `fields_by_status`, `qa`,
  `cch_upload`). Ver "Salida hacia completion-report" en ese SKILL.
- **source-resolver** → `notifications.email.recipient` y `send_mode` (no hardcodear el mail).
- **conector Gmail (MCP)** → enviar el mail o, si solo permite borradores, dejar el borrador.

## Quién la invoca
`intake-trigger`, al terminar cada entidad del flujo automático. En runs interactivos manuales
del orquestador NO se dispara (para no mandar mails de prueba).

## Procedimiento
1. **Resolver** el destinatario vía source-resolver (`notifications.email.recipient`) y el `send_mode`.
2. **Armar el mail** según `result` (ver "Contenido").
3. **Enviar** con el conector Gmail. Si el conector solo permite `create_draft`, dejar el borrador
   y devolver `status: draft_left`. Si envía, devolver `status: notified`.
4. **Devolver** el `status` para el resumen del trigger.

## Contenido del mail

**Éxito (`result: success`):**
- Asunto: `[1065] <cliente> — completado (<N> puntos a verificar)` (N = |check| + |manual| + |missing|).
- Cuerpo (español):
  1. "Se armó el borrador del Form 1065 de **<cliente>**."
  2. Qué quedó automático: conteo AUTO + REGLA (% de automatización del mockup).
  3. **Puntos a tener en cuenta** (a verificar por una persona): lista de `check` + `manual` +
     `missing`, cada uno con su worksheet/línea.
  4. QA: `qa.cross_checks` y `qa.diagnostics`.
  5. Estado subida a CCH: si `cch_upload: pending` → "Subida a CCH pendiente (credenciales sandbox)".
  6. Mockup: adjuntar el HTML si el conector lo permite; si no, incluir la ruta/enlace (`mockup`).

**Fallo (`result: failure`):**
- Asunto: `[1065] <cliente> — NO se pudo completar`.
- Cuerpo: el `reason` (fuente crítica faltante, carpeta no localizada, excepción).

## Salida
```yaml
client: AGGUILU LLC
status: notified        # notified | draft_left | error
recipient: josed@inforge.us
```

## Reglas
- **No escribe en Airtable** (ningún estado) **ni en CCH.** Solo manda el mail.
- **No re-calcula** el 1065: usa el `fields_by_status`/`qa` que ya trae el orquestador.
- Destinatario y modo de envío salen de source-resolver, nunca hardcodeados.
- Un fallo al mandar el mail no debe frenar el resto del batch del trigger: devolver `status: error`.
```

- [ ] **Step 2: Verificar frontmatter y secciones clave**

Run:
```bash
head -3 .claude/skills/completion-report/SKILL.md
grep -c -E "^## (Qué hace|Depende de|Procedimiento|Contenido del mail|Salida|Reglas)" .claude/skills/completion-report/SKILL.md
```
Expected: la línea 1 es `---`, la 2 `name: completion-report`; el grep imprime `6`.

- [ ] **Step 3: Verificar que no hay destinatario hardcodeado fuera de la referencia a source-resolver**

Run:
```bash
grep -n "josed@inforge.us" .claude/skills/completion-report/SKILL.md
```
Expected: solo aparece en el bloque de ejemplo "## Salida" (ilustrativo), no como valor operativo. Si aparece como valor a usar, reemplazar por "el que resuelve source-resolver".

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/completion-report/SKILL.md
git commit -m "Crea skill completion-report: mail de cierre del 1065 vía Gmail"
```

---

### Task 4: Cablear completion-report en intake-trigger

**Files:**
- Modify: `.claude/skills/intake-trigger/SKILL.md`

**Interfaces:**
- Consumes: `completion-report` (Task 3) y el objeto de salida de `return-orchestrator` (Task 2).

- [ ] **Step 1: Agregar el paso de notificación al Procedimiento**

En `intake-trigger/SKILL.md`, en la sección "Procedimiento", cambiar el paso 3 para que, tras el orquestador, invoque completion-report:

```markdown
3. **Por cada entidad, en serie (una a la vez):**
   a. invocar `return-orchestrator` con `client = <entidad>` → extrae fuentes (Airtable + Dropbox)
      y arma el borrador/mockup, devolviendo el objeto de salida (result, mockup, fields_by_status,
      qa, cch_upload).
   b. invocar `completion-report` con ese objeto → manda el mail de cierre (éxito o fallo).
```

- [ ] **Step 2: Actualizar la sección "Depende de" para incluir completion-report**

Agregar a la lista "Depende de":
```markdown
- **completion-report** → manda el mail de cierre por cada entidad (éxito o fallo).
```

- [ ] **Step 3: Actualizar el prompt de la Tarea Programada documentado en la skill**

Reemplazar el prompt de la sección "Cómo se ejecuta (Tareas Programadas de Cowork)" por:

```markdown
> **Ejecutá la skill `intake-trigger`.** Revisá Airtable por las entidades en
> `Primary Form Status = "CCH To do"`. Por cada una, en serie: armá su borrador 1065 con
> `return-orchestrator` (extracción + mockup) y luego ejecutá `completion-report` para notificar
> por mail que el 1065 se completó, con los puntos a verificar y la referencia al mockup.
> NO cambies ningún estado en Airtable. Devolveme el resumen de lo procesado.
```

Y ajustar la línea de cadencia para indicar **cada 1 hora** (tarea `intake-1065-cch`).

- [ ] **Step 4: Verificar que el trigger nombra completion-report**

Run:
```bash
grep -c "completion-report" .claude/skills/intake-trigger/SKILL.md
```
Expected: `>= 3` (Depende de, Procedimiento, prompt).

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/intake-trigger/SKILL.md
git commit -m "intake-trigger: encadena completion-report tras cada entidad + prompt horario"
```

---

### Task 5: Referencia de la Tarea Programada de Cowork (para pegar en Claude Desktop)

**Files:**
- Create: `.claude/skills/intake-trigger/references/scheduled-task.md`

**Interfaces:**
- Produces: documento con la config exacta del diálogo "Crear tarea programada" (Nombre, Descripción, Prompt, Frecuencia) que el usuario copia en Claude Desktop.

- [ ] **Step 1: Crear el archivo de referencia**

Crear `.claude/skills/intake-trigger/references/scheduled-task.md` con:

```markdown
# Tarea Programada de Cowork — intake-1065-cch

Se crea en **Claude Desktop** (diálogo "Crear tarea programada"). No se crea desde el repo.

| Campo | Valor |
|---|---|
| Nombre | `intake-1065-cch` |
| Descripción | `Revisa Airtable cada hora, arma los 1065 en 'CCH To do' y notifica por mail` |
| Trabajar en un proyecto | el proyecto del pipeline 1065 (donde viven las skills) |
| Modelo | predeterminado |
| Frecuencia | **Cada hora** |

**Prompt (pegar tal cual):**

> Ejecutá la skill `intake-trigger`. Revisá Airtable por las entidades en
> `Primary Form Status = "CCH To do"`. Por cada una, en serie: armá su borrador de 1065 con
> `return-orchestrator` (extracción de datos + mockup HTML). Al terminar cada entidad, ejecutá
> `completion-report` para notificar por mail (conector Gmail) que el 1065 se completó, con los
> puntos a verificar (CHECK/MANUAL/faltantes) y la referencia al mockup. No cambies ningún estado
> en Airtable. Devolveme el resumen de lo procesado.

**Requisitos en la PC dedicada:** Cowork abierto, "Mantener activo" encendido, conectores MCP
Airtable + Dropbox + Gmail autenticados en la sesión.
```

- [ ] **Step 2: Verificar contenido mínimo**

Run:
```bash
grep -c -E "intake-1065-cch|Cada hora|completion-report" .claude/skills/intake-trigger/references/scheduled-task.md
```
Expected: `>= 3`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/intake-trigger/references/scheduled-task.md
git commit -m "intake-trigger: referencia de la Tarea Programada horaria para Claude Desktop"
```

---

### Task 6: Prueba de aceptación (manual, en Cowork) y checklist de sync

**Files:** ninguno (verificación).

- [ ] **Step 1: Sincronizar a Claude Desktop (manual)**

Copiar a mano en Claude Desktop:
- Skill nueva `completion-report`.
- `intake-trigger`, `return-orchestrator`, `source-resolver` actualizadas.

- [ ] **Step 2: Prueba de humo en un chat de Cowork**

Con AGGUILU LLC en `Primary Form Status = "CCH To do"`, correr en un chat:
> Ejecutá `intake-trigger`.

Expected: se genera el mockup de AGGUILU (igual que `1065_AGGUILU_mockup.html`) y se crea/envía el
mail de cierre con los puntos a verificar. Si el conector solo dejó borrador, el mail queda en
Borradores de Gmail.

- [ ] **Step 3: Crear la Tarea Programada**

En Claude Desktop, crear `intake-1065-cch` con la config de `references/scheduled-task.md`
(Frecuencia: Cada hora).

- [ ] **Step 4: Verificar una corrida programada**

Tras la primera corrida horaria, confirmar: mockup generado + mail creado, y **ningún** estado de
Airtable modificado.
```
