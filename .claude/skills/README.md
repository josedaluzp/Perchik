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
| 1 | cch-axcess-client        | Plataforma | ⛔ contrato definido — falta decidir API/UI de CCH |
| 2 | intake-trigger           | Entrada | ✅ lógica completa (alcance actual) — solo lectura: detecta `CCH To do` → dispara orquestador (extracción + borrador). Writeback de estados diferido. Corre vía Tareas Programadas de Cowork. |
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
| — | return-orchestrator      | Orquestación | 🟡 esqueleto — se finaliza al último |

## Cuello de botella

`cch-axcess-client` es el sumidero: **sin él no hay test end-to-end de nada.** Antes de
codificarlo hay que decidir *cómo* se escribe en CCH Axcess (¿API oficial? ¿automatización
de UI?). Es la primera decisión dura pendiente.
