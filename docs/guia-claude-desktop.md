# Guía — Usar las skills 1065 → CCH Axcess en Claude Desktop

Objetivo: que el equipo de Perchik pueda, desde **Claude Desktop**, pedir el borrador de un
Form 1065 y que Claude **extraiga todos los datos** de Airtable + Dropbox y los muestre listos
para cargar en CCH. Alcance hoy: **leer + armar borrador + mockup**. (Escribir en CCH todavía
es manual — ver "Límites".)

## 1. Conectar los conectores (una sola vez)

En Claude Desktop → **Ajustes → Conectores** (Settings → Connectors):

1. **Airtable** → conectar y autorizar la base **"Tax Year 2025 - Usar Esta"**.
2. **Dropbox** → conectar con la cuenta del team **PERCHIK, CPA** (acceso a `/Estudio PERCHIK CPA/Clients`).

> Son los mismos conectores que ya usamos. Sin estos dos, las skills no tienen de dónde leer.

## 2. Cargar las skills (una sola vez)

Las skills viven en `.claude/skills/`. Cada una es una carpeta con `SKILL.md` (y a veces
`references/`). El formato es el de **Agent Skills** de Anthropic, así que se suben tal cual.

> **Ya están empaquetadas** en `dist/skills-claude-desktop/` — un `.zip` por skill, con el
> `SKILL.md` en la raíz (el formato que pide Claude Desktop). No hace falta comprimir nada.

En Claude Desktop → **Ajustes → Capacidades → Skills** (Settings → Capabilities → Skills):

1. Arrastrar/subir los `.zip` desde `dist/skills-claude-desktop/`.
2. Subir. Empezar por las base, en este orden:
   - `source-resolver` (incluye `references/sources.yaml` — **imprescindible**, es el mapa de dónde sale cada dato)
   - `scenario-classifier`, `intake-trigger`
   - las de núcleo: `basic-data`, `partners-k1`, `balance-sheet`, `other-information`, `ownership-structure`, `efile-config`
   - income: `income-router` + los módulos que apliquen
   - `foreign-forms`, `cross-check-engine`, `print-efile`, `return-orchestrator`

> Mínimo viable para probar un cliente: **source-resolver + basic-data + partners-k1 +
> balance-sheet + el módulo de income que corresponda**.

## 3. Cómo usarlo (día a día)

Prompt tipo, en un chat de Claude Desktop con los conectores activos:

> **"Armá el borrador del Form 1065 2025 para SALVIN7 LLC: traé todos los datos de Airtable y
> Dropbox y mostrame cada valor en el campo de CCH donde va, marcando lo que necesita revisión."**

Claude va a:
1. Buscar la entidad en Airtable (Entity Tracker) + sus socios (Individual Tracker).
2. Localizar la carpeta del cliente en Dropbox y leer P&L, Balance, Capital Account, K-1, etc.
3. Mapear cada dato a su campo de CCH y devolver la tabla (como el mockup), separando lo
   **AUTO** de lo que requiere **CHECK/MANUAL**.

Variantes útiles:
- *"Solo la parte de socios y el 8804/8805 de AGGUILU."*
- *"Compará lo que extrajiste contra el 1065 ya armado del año pasado."*
- *"Listame qué documentos fuente falta que el cliente entregue."*

## 4. Flujo recomendado de trabajo

1. Claude arma el borrador (lectura automática).
2. El preparador **revisa los CHECK** (ej. EIN de socio corp foreign, discrepancias de dirección).
3. El preparador **carga en CCH Axcess** los valores AUTO (copiar/pegar guiado por la tabla).
4. Correr el Diagnostic de CCH y cerrar como siempre.

## 5. Límites (importante)

- **No escribe en CCH todavía.** Falta definir `cch-axcess-client` (API oficial vs automatización
  de UI). Hasta entonces la carga final es manual.
- **Siempre revisar los CHECK.** La automatización no decide reglas de criterio (clasificación de
  un préstamo, EIN pendiente, etc.).
- **Scripts locales** (parsear un PDF gigante, build de PDFs) corren mejor en **Claude Code** que
  en Desktop. Para el uso del equipo, Desktop alcanza; para desarrollo, Claude Code.

## 6. Resumen

| Necesidad | Dónde |
|-----------|-------|
| Que el equipo pida borradores de 1065 | **Claude Desktop** + conectores + skills |
| Desarrollar / orquestar / scripts | **Claude Code** (este repo) |
| Escribir directo en CCH | pendiente (`cch-axcess-client`) |
