# Skills 1065 → CCH Axcess — Tablero de construcción

Suite de skills para automatizar el data-entry del Form 1065 hacia CCH Axcess
(Tenfold × Perchik). Derivado del artifact *"Árbol de dependencias — Skills 1065 → CCH Axcess"*.

## Principio de diseño (decidido)

Tres trabajos separados, nunca mezclados:

1. **Traer/llevar datos** → los **conectores** (MCP Airtable / Dropbox). Tubo tonto: no
   saben qué es un SS-4 ni en qué carpeta vive nada.
2. **Saber dónde está cada cosa** → **`source-resolver`**. Único lugar con el mapa.
3. **Entender qué significa y a dónde va en CCH** → cada **skill** de núcleo/módulo.

> Si cambia la convención de carpetas, se toca **un solo archivo** (el diccionario del
> resolver), no las 15 skills ni los conectores.

## Orden de construcción (bottom-up) y estado

Una skill se codifica recién cuando sus dependencias ya existen y pasan.
`‖` = se pueden hacer en paralelo · `→` = dependencia dura (serial).

**Estados:** ✅ listo/existe · 🟡 esqueleto (SKILL.md con contrato y reglas, falta
implementación real contra MCP/CCH) · ⛔ brecha (regla/decisión pendiente).

| Nivel | Skill | Capa | Estado |
|------:|-------|------|--------|
| 0 | airtable-connector (MCP) | Conector | ✅ existe (MCP) |
| 0 | dropbox-connector (MCP)  | Conector | ✅ existe (MCP) |
| 1 | **source-resolver**      | Plataforma | ✅ diccionario poblado con IDs/estructura real + extracción probada |
| 1 | qb-report-reader         | Plataforma | 🟡 esqueleto |
| 1 | cch-axcess-client        | Plataforma | 🟡 mecanismo + **formato resuelto** (Tax Transfer XML, POST /ReturnsImportBatch, buffer→flush→poll, export read-back; ver `references/tax-transfer-format.md`). Falta: **field codes del 1065** (sacar exportando un return terminado), OAuth setup, licencia. |
| 2 | intake-trigger           | Entrada | ✅ lógica completa (alcance actual) — solo lectura: detecta `CCH To do` → dispara orquestador (extracción + borrador) → `completion-report` (mail). Writeback de estados diferido. Corre vía Tarea Programada de Cowork **cada 1h** (`intake-1065-cch`). |
| 2 | scenario-classifier      | Entrada | 🟡 esqueleto |
| 3 | basic-data               | Núcleo | 🟡 esqueleto |
| 3 | other-information        | Núcleo | 🟡 esqueleto |
| 3 | ownership-structure      | Núcleo | 🟡 esqueleto |
| 3 | efile-config             | Núcleo | 🟡 esqueleto |
| 3 | partners-k1              | Núcleo | 🟡 esqueleto |
| 3 | balance-sheet            | Núcleo | 🟡 esqueleto |
| 4 | income-router            | Núcleo | 🟡 esqueleto |
| 5 | income-real-estate       | Módulo income | 🟡 esqueleto |
| 5 | income-consulting-usa    | Módulo income | 🟡 esqueleto |
| 5 | income-consulting-foreign| Módulo income | 🟡 esqueleto |
| 5 | sale-of-property         | Módulo income | 🟡 esqueleto |
| 5 | change-in-ownership      | Módulo income | 🟡 esqueleto |
| 5 | income-passthrough-k1    | Módulo income | ⛔ esqueleto + BRECHA (holding recibe K-1) |
| 5 | sale-of-securities       | Módulo income | ⛔ esqueleto + BRECHA (8949 ∉ retención 1446) |
| 6 | foreign-forms            | Núcleo | 🟡 esqueleto |
| 7 | cross-check-engine       | QA | 🟡 esqueleto |
| 7 | diagnostic-runner        | QA | 🟡 esqueleto |
| 8 | print-efile              | Cierre | 🟡 esqueleto |
| 8 | **completion-report**    | Cierre / notificación | 🟡 diseñado (spec `docs/superpowers/specs/2026-07-01-…`) — al terminar cada entidad manda mail (Gmail) "1065 de X completado" + puntos a verificar + ref. al mockup. La invoca `intake-trigger`. |
| — | return-orchestrator      | Orquestación | ✅ funciona end-to-end en run interactivo (genera el mockup HTML, p.ej. `1065_AGGUILU_mockup.html`); pendiente cablear la subida a CCH cuando exista el cliente. |

## Cuello de botella — DESBLOQUEADO (jun-2026)

`cch-axcess-client` es el sumidero: **sin él no hay test end-to-end de nada.** La decisión dura
de *cómo* se escribe en CCH **ya se tomó**: API oficial **CCH Axcess Tax Services v2** (OIP,
"Import and export data to tax returns"), auth OAuth 2.0. Se descarta la automatización de UI.
Formato + OAuth ya documentados (ver `cch-axcess-client/references/`). **Bloqueo externo
(jun-2026):** el acceso (Developer Portal + sandbox) viene incluido con la cuenta Axcess de
Perchik (168142) — NO hace falta comprar licencia ni cuenta de sandbox aparte. Lo pendiente es
operativo: **firmar el DocuSign del quote + que WK active las APIs** (en abril aún no estaban
habilitadas). Por eso hoy no aparece "Developer Tools" ni "Subscribe". Acción: firmar el quote
(lo tiene Ian / hilo con Bridgit de WK) y confirmar activación de APIs. Mientras tanto se puede
construir el builder de XML contra el formato documentado. Ver `cch-axcess-client/SKILL.md`.

## Automatización horaria (scheduled) — en construcción (jul-2026)

Mientras esperamos las credenciales de sandbox, se **envuelve el flujo que ya funciona** (el run
manual "armá el 1065 de X" → mockup) en una **Tarea Programada de Cowork cada 1h** (`intake-1065-cch`)
y se le agrega una **notificación por mail** al cerrar cada entidad. Lo que corre HOY:

```
scheduled 1h → intake-trigger (lee "CCH To do") → return-orchestrator (mockup) → completion-report (mail Gmail)
```

- La **subida real a CCH** (`cch-axcess-client`) es una costura futura: se inserta entre el
  orquestador y el mail cuando haya credenciales. Hoy el mail informa "subida a CCH pendiente".
- **Solo se lee `CCH To do`** — no se escribe ningún estado en Airtable (decisión jul-2026). Sin
  writeback, cada hora reprocesa lo que siga en `CCH To do`; el equipo lo saca a mano al revisar.
- Diseño completo: `docs/superpowers/specs/2026-07-01-scheduled-1065-completion-report-design.md`.
- **Recordá:** las skills se editan en este repo pero corren en **Cowork/Claude Desktop** →
  hay que copiarlas a mano allá (no hay sync automático).

## Dónde retomamos (ago-2026)

Ya hay **acceso a la PC 24/7**. El próximo paso es implementar `cch-axcess-client` ahí: decidir su
forma (**MCP local por stdio vs CLI** — recomendación y trade-offs en el `README.md` de la raíz),
destrabar la activación de las APIs con WK, y **exportar un 1065 terminado para sacar los field
codes de Partnership**. Eso último es lo que convierte los 🟡 esqueletos en implementación real.
