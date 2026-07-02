# Diseño — Scheduled horario del 1065 + skill `completion-report`

- **Fecha:** 2026-07-01
- **Autor:** José (Perchik / Tenfold) + Claude
- **Estado:** aprobado para plan de implementación
- **Contexto:** trabajo construible **ahora**, mientras esperamos las credenciales de
  sandbox de CCH Axcess (OIP). No requiere que `cch-axcess-client` esté vivo.

---

## 1. Objetivo

Automatizar, **cada 1 hora**, el flujo que hoy corremos a mano en un chat
("armá el 1065 de AGGUILU LLC" → mockup HTML) y agregarle una **notificación por mail**
que avise que el 1065 de un cliente se completó, con los puntos que una persona debe verificar.

Dos entregables:

1. **Una Tarea Programada de Cowork** (Claude Desktop) que *contiene* toda la arquitectura de
   skills existente y la dispara sola contra las entidades listas.
2. **Una skill nueva `completion-report`** que arma y envía el mail de cierre vía el conector Gmail.

## 2. Alcance

**Dentro (se construye ahora):**
- La Tarea Programada horaria (config + prompt listo para pegar en Claude Desktop).
- La skill `completion-report` (SKILL.md + contrato lógico).
- Ajuste de `intake-trigger` para invocar `completion-report` tras cada entidad.
- Config del destinatario del mail en `source-resolver`.

**Fuera (documentado como costura futura, NO se construye ahora):**
- La subida real de datos a CCH Axcess (`cch-axcess-client`) — gated por credenciales sandbox.
- El writeback de estados en Airtable (`CCH In progress` / `Ready to Check` / `Corregir`) —
  decisión del usuario: **por ahora solo se lee `CCH To do`, no se toca ningún otro estado.**

## 3. Flujo end-to-end (lo que corre hoy dentro del scheduled)

```
Tarea Programada Cowork (Frecuencia: Cada hora)
        │
        ▼
  intake-trigger ─────── lee Airtable → entidades con Primary Form Status = "CCH To do"
        │
        ▼  (por cada entidad, EN SERIE)
  return-orchestrator ── arquitectura completa de skills (ya funciona)
        │                 → genera el mockup HTML (resultado final)
        │                 → devuelve result: success | failure + detalle de campos por estado
        ▼
  completion-report ──── (SKILL NUEVA) arma y envía el mail vía Gmail:
                          "1065 de <cliente> completado" + puntos a verificar + ref. al mockup
        │
        ▼
  (FUTURO, cuando cch-axcess-client tenga credenciales:
   entre orchestrator y completion-report se inserta la subida AUTO/REGLA a CCH.)
```

Regla de serie (heredada de `intake-trigger`): una entidad a la vez, para no pisar conexiones
MCP ni dejar borradores a medias.

## 4. Pieza 1 — Tarea Programada de Cowork

Se crea **en Claude Desktop** (diálogo "Crear tarea programada"). No se puede crear desde el repo.

| Campo | Valor |
|---|---|
| **Nombre** | `intake-1065-cch` |
| **Descripción** | `Revisa Airtable cada hora, arma los 1065 en 'CCH To do' y notifica por mail` |
| **Prompt** | ver abajo |
| **Trabajar en un proyecto** | el proyecto del pipeline 1065 (donde viven las skills) |
| **Modelo** | predeterminado |
| **Frecuencia** | **Cada hora** |

**Prompt (listo para pegar):**

> Ejecutá la skill `intake-trigger`. Revisá Airtable por las entidades en
> `Primary Form Status = "CCH To do"`. Por cada una, en serie: armá su borrador de 1065 con
> `return-orchestrator` (extracción de datos + mockup HTML). Al terminar cada entidad, ejecutá
> `completion-report` para notificar por mail (conector Gmail) que el 1065 se completó, con los
> puntos a verificar (CHECK/MANUAL/faltantes) y la referencia al mockup. **No cambies ningún
> estado en Airtable.** Devolveme el resumen de lo procesado.

> **Por qué Cowork y no una routine cloud:** las tareas programadas de Cowork corren en la sesión
> local autenticada → los conectores MCP (Airtable, Dropbox, Gmail) están vivos. Un headless
> podría despertar sin esos conectores.

## 5. Pieza 2 — Skill nueva `completion-report`

- **Capa:** Cierre / notificación. Corre al final del flujo de cada entidad.
- **Qué hace:** toma el resultado de `return-orchestrator` para una entidad y **arma + envía por
  Gmail** un mail de notificación. No toca CCH ni Airtable.
- **Quién la invoca:** `intake-trigger` (flujo automático). En runs interactivos manuales del
  orquestador NO se dispara (para no mandar mails de prueba).

**Contrato lógico de entrada:**
```yaml
client: AGGUILU LLC
result: success            # success | failure
mockup: file:///C:/Users/PC/Downloads/1065_AGGUILU_mockup.html   # ruta del artifact
reason: null               # motivo, sólo si failure
fields_by_status:          # del mockup del orchestrator
  auto:   [ ... ]          # cargados directo de la fuente
  regla:  [ ... ]          # derivados por regla fiscal
  check:  [ ... ]          # resueltos pero a verificar por una persona
  manual: [ ... ]          # no están en las fuentes → carga humana
  missing:[ ... ]          # fuentes/datos faltantes
qa:                        # de cross-check-engine + diagnostic-runner
  cross_checks: "ΣK-1=100%, M-1 OK, ..."
  diagnostics: "0 errores, 2 warnings"
cch_upload: pending        # done | pending  (pending mientras cch-axcess-client esté gated)
recipient: josed@inforge.us
```

**Salida:** el mail enviado (o borrador creado) + un `status` para el resumen del trigger.

**Depende de:**
- `source-resolver` → el destinatario del mail (config, no hardcodeado).
- conector Gmail (MCP) → enviar / crear borrador.
- resultado de `return-orchestrator` (mockup + estados) y de la QA.

## 6. Contenido del mail

- **Asunto (success):** `[1065] AGGUILU LLC — completado (N puntos a verificar)`
- **Asunto (failure):** `[1065] AGGUILU LLC — NO se pudo completar`
- **Cuerpo (success):**
  1. Mensaje de éxito: "Se armó el borrador del Form 1065 de **AGGUILU LLC**."
  2. **Qué quedó automático:** conteo AUTO + REGLA (el % de automatización del mockup).
  3. **Puntos a tener en cuenta** (lo que una persona debe verificar): lista de CHECK + MANUAL +
     datos faltantes, cada uno con worksheet/línea.
  4. **QA:** resumen de cross-checks y diagnostics.
  5. **Estado subida a CCH:** `pendiente (credenciales sandbox)` hasta que `cch-axcess-client` viva.
  6. **Mockup:** adjunto si el conector lo permite; si no, la ruta/enlace del HTML.
- **Cuerpo (failure):** motivo del fallo (fuente crítica faltante, carpeta no localizada, excepción).
- **Idioma:** español.

## 7. Cambios a skills existentes

| Skill | Cambio |
|---|---|
| 🆕 `completion-report` | SKILL.md nueva con el contrato de arriba. |
| ✏️ `intake-trigger` | Agregar el paso: por cada entidad, tras `return-orchestrator`, invocar `completion-report`. Actualizar el prompt de la Tarea Programada documentado en la skill. |
| ✏️ `source-resolver` (`sources.yaml`) | Agregar `notifications.email.recipient` (default `josed@inforge.us`) como config. |
| ✏️ `return-orchestrator` | Confirmar que su salida expone `fields_by_status` + `qa` + `mockup` para que `completion-report` los consuma. Ajustar si falta. |

## 8. Limitaciones conocidas y decisiones

- **Reproceso (idempotencia):** sin writeback, cada corrida horaria re-arma toda entidad que siga
  en `CCH To do`, y **re-manda el mail**. Mitigación por ahora: el equipo saca la entidad de
  `CCH To do` a mano al revisar. Decisión explícita del usuario: no tocar otros estados todavía.
- **Subida a CCH:** cableada como costura pero **inactiva** hasta las credenciales sandbox; el mail
  informa "pendiente".
- **Gmail enviar vs borrador:** el conector Gmail vía MCP suele exponer sólo `create_draft`. En
  Cowork/Claude Desktop puede diferir. Si no puede enviar, `completion-report` deja el **borrador**
  y el mail se manda a mano. A confirmar al implementar.
- **Sync manual a Claude Desktop:** las skills se editan acá pero corren en Cowork; hay que
  copiarlas a mano en Claude Desktop (ver §10).

## 9. Criterios de éxito

- Correr la Tarea Programada (o su prompt a demanda) detecta las entidades en `CCH To do` y, por
  cada una, produce el mockup HTML **igual** que el run manual actual.
- Por cada entidad exitosa se genera el mail con: mensaje de éxito, conteo AUTO/REGLA, lista de
  CHECK/MANUAL/faltantes, resumen QA, estado de subida CCH y referencia al mockup.
- Un `failure` produce un mail de "no se pudo completar" con el motivo, sin frenar el resto.
- No se escribe ningún estado en Airtable ni nada en CCH.
- **Prueba de aceptación:** con AGGUILU LLC en `CCH To do`, el flujo reproduce
  `1065_AGGUILU_mockup.html` y genera su mail de cierre.

## 10. Checklist de sincronización a Claude Desktop (manual)

Tras implementar en el repo, copiar a mano en Claude Desktop:
- [ ] Nueva skill `completion-report` (SKILL.md).
- [ ] `intake-trigger` actualizada.
- [ ] `source-resolver` (`sources.yaml`) con el destinatario.
- [ ] `return-orchestrator` si se ajustó su salida.
- [ ] Crear la Tarea Programada `intake-1065-cch` (Frecuencia: Cada hora) con el prompt de §4.
