# Perchik × Tenfold — Automatización Form 1065 → CCH Axcess

Suite de **skills** para que un agente arme el borrador de declaraciones **Form 1065** en
**CCH Axcess**, leyendo los datos de **2 fuentes: Airtable + Dropbox**. Modo lectura: deja el
return *listo para revisar* (escribir en CCH es la fase siguiente).

## Estructura del repo
- **`.claude/skills/`** — las 24 skills de la arquitectura + el tablero de estado
  (`.claude/skills/README.md`). Empezar por ahí.
  - `source-resolver/` — el diccionario de fuentes (`references/sources.yaml`): el único lugar
    que sabe de dónde sale cada dato.
- **`docs/`** — documentación y entregables:
  - `mockup-1065-salvin7.html` · `mockup-1065-agguilu.html` — simulaciones del 1065 relleno
    (Campo · Valor · Fuente · Estado) ⚠️ contienen datos reales de clientes.
  - `arquitectura-skills.html` — diagrama de la arquitectura.
  - `guia-claude-desktop.md` — cómo usar las skills + conectores en Claude Desktop.
  - `brief-slides-no-tecnico.md` — brief para slides de presentación.
  - `pendientes-mapping-v2.4-segun-videos.md` — brechas detectadas en los videos.
- **`trancript/`** — transcripciones de los videos de training (SALVIN7, AGGUILU, Form 8949).

## Diseño en 3 capas de responsabilidad
1. **Conectores** (Airtable / Dropbox) — tubo tonto: solo traen datos.
2. **`source-resolver`** — único lugar que sabe *dónde* vive cada dato.
3. **Skills** — *qué significa* cada dato y *a dónde va* en CCH.

## Estado
- ✅ Lectura + borrador + mockup: funciona (validado con SALVIN7, AGGUILU; CROOEL = caso 8949).
- ⛔ Escritura en CCH (`cch-axcess-client`): pendiente — vía Native API / automatización de UI.

> Gestión del proyecto en Jira: **PCO** (inforge.atlassian.net).
> Los videos de training (`video/`) y los zips (`dist/`) no se versionan — ver `.gitignore`.
