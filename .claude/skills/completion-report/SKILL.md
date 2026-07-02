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
