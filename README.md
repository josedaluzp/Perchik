# Perchik × Tenfold — Automatización Form 1065 → CCH Axcess

Suite de **skills** para que un agente arme el borrador de declaraciones **Form 1065** en
**CCH Axcess**, leyendo los datos de **2 fuentes: Airtable + Dropbox**. Modo lectura: deja el
return *listo para revisar* (escribir en CCH es la fase siguiente).

## Estructura del repo
- **`.claude/skills/`** — las 24 skills de la arquitectura + el tablero de estado
  (`.claude/skills/README.md`). Empezar por ahí.
  - `source-resolver/` — el diccionario de fuentes (`references/sources.yaml`): el único lugar
    que sabe de dónde sale cada dato.
  - `cch-axcess-client/references/` — `oauth-auth.md` (OAuth 2.0 completo) y
    `tax-transfer-format.md` (el XML de import). Lo que hay que implementar en la PC dedicada.
- **`docs/`** — documentación y entregables:
  - `mockup-1065-salvin7.html` · `mockup-1065-agguilu.html` — simulaciones del 1065 relleno
    (Campo · Valor · Fuente · Estado) ⚠️ contienen datos reales de clientes.
  - `arquitectura-skills.html` — diagrama de la arquitectura.
  - `guia-claude-desktop.md` — cómo usar las skills + conectores en Claude Desktop.
  - `tarea-programada-intake-1065-cch.md` — config exacta de la tarea horaria (prompt incluido).
  - `pc-24-7/` — el documento de selección de la PC dedicada 24/7 (candidatos y requisitos).
  - `brief-slides-no-tecnico.md` — brief para slides de presentación.
  - `pendientes-mapping-v2.4-segun-videos.md` — brechas detectadas en los videos.
  - `superpowers/specs/` · `superpowers/plans/` — diseños e implementaciones por etapa.
- **`trancript/`** — transcripciones de los videos de training (SALVIN7, AGGUILU, Form 8949).

## Diseño en 3 capas de responsabilidad
1. **Conectores** (Airtable / Dropbox / Gmail) — tubo tonto: solo traen y llevan datos.
2. **`source-resolver`** — único lugar que sabe *dónde* vive cada dato.
3. **Skills** — *qué significa* cada dato y *a dónde va* en CCH.

## Estado (ago-2026)

**✅ Lo que corre hoy, sin intervención:**

```
Tarea Programada de Cowork (cada 1h)
  → intake-trigger        lee Airtable: entidades en "CCH To do" (máx. 5 por corrida)
  → return-orchestrator   Airtable + Dropbox → mockup HTML del 1065
  → completion-report     mail por Gmail: qué se completó y qué hay que verificar
```

Validado con SALVIN7 (consulting fuera de USA), AGGUILU (real estate con socio corp) y CROOEL
(caso 8949). Sin writeback: no se escribe ningún estado en Airtable, el equipo saca la entidad de
`CCH To do` a mano al revisar el mail.

**⛔ Lo que falta — el sumidero `cch-axcess-client` (escribir en CCH):**
La decisión de *cómo* ya está tomada: **API oficial CCH Axcess Tax Services v2** (OIP), OAuth 2.0,
import/export de XML por lotes. Se descartó la automatización de UI. Falta ejecutarla.

## Retomamos acá — la PC dedicada

Ya tenemos **acceso a la PC 24/7** donde va instalada toda esta arquitectura. Ese es el hito que
desbloquea la fase de escritura. Tres frentes, en este orden:

### 1. Decidir la forma del cliente CCH: MCP vs CLI ⬅️ decisión abierta

El código que habla con la API de CCH (OAuth + armar el XML + POST + poll) tiene que vivir **en la
PC**, no en la conversación. La pregunta es con qué superficie lo consumen las skills:

| Opción | Cómo lo invoca la skill | A favor | En contra |
|---|---|---|---|
| **A · MCP local (stdio)** | como una tool más, igual que Airtable/Dropbox/Gmail | mismo patrón que el resto de la suite; Claude Desktop lo arranca y lo mata solo; sin puerto, sin servicio, sin TLS; los secretos viven en el env del proceso y **nunca pasan por el modelo** | vive solo mientras Desktop está abierto; hay que escribir el server MCP |
| **B · CLI** | ejecutando un comando en la PC | trivial de probar y depurar desde la terminal; imprescindible igual para el consentimiento OAuth inicial y para exportar el 1065 y sacar los field codes | requiere que el entorno donde corren las skills pueda ejecutar comandos **en esa PC** — si corre en el contenedor de Cowork, no la alcanza |
| **C · Server HTTP en segundo plano** | vía conector MCP remoto | sobrevive a que se cierre Desktop; compartible | puerto, servicio de Windows, certificado, firewall: la mayor superficie operativa en una máquina desatendida |

**Recomendación (a confirmar):** **A + B sobre el mismo código.** Un módulo Python único con dos
entradas — un **server MCP por stdio** que es lo que consumen las skills, y un **CLI** sobre las
mismas funciones para el setup y el debug. No es trabajo doble: es el mismo paquete con dos
puntos de entrada, y el CLI hace falta sí o sí para dos cosas que un MCP no puede hacer solo.

Puntos que la decisión tiene que resolver:
- **Dónde corre realmente la skill** respecto de la PC. Es lo que decide si B es viable por sí solo.
- **Vigencia del refresh token.** Cada refresh resetea la expiración del access *y* del refresh
  (ver `oauth-auth.md`): si se refresca seguido, no vuelve a hacer falta un humano. Como una
  corrida sin entidades podría no tocar CCH, conviene que `intake-trigger` llame un
  `cch_auth_status` barato en **cada** corrida para mantener el token vivo.
- **Redirect URI del consentimiento inicial:** CCH **bloquea `localhost`**, hay que registrar una
  `https://` propia y leer el `code` de la barra de direcciones.

### 2. Destrabar el acceso a la API (bloqueo externo, no técnico)
El acceso al Developer Portal viene incluido con la cuenta Axcess de Perchik (**168142**) — no hay
que comprar licencia ni sandbox aparte. Falta **firmar el DocuSign del quote y que WK active las
APIs**; hasta entonces no aparece "Developer Tools" en el Dashboard. Lo tiene Ian (hilo con Bridgit
de WK).

### 3. Sacar los field codes del 1065 ⬅️ lo único crítico del lado técnico
El ejemplo de la API es Individual (`ReturnType="I"`, codes `IFDSGEN.*`); el 1065 es
**Partnership (`ReturnType="P"`)**, con otros codes. La vía directa: **exportar un 1065 ya
terminado** (AGGUILU / SALVIN7) y leer los `Location` reales de cada campo del XML. Se puede hacer
apenas haya credenciales, y es lo que convierte las 20 skills de esqueleto en implementación real.

Mientras 2 y 3 estén pendientes, se puede construir el builder de XML contra el formato ya
documentado en `tax-transfer-format.md`.

## Operación
- Las skills se editan **en este repo** pero corren en **Cowork / Claude Desktop** → hay que
  copiarlas a mano allá. **No hay sync automático.**
- Requisitos en la PC dedicada: Cowork abierto, "Mantener activo" encendido, y los conectores
  **Airtable + Dropbox + Gmail** autenticados en la sesión.
- Secretos (`client_id`, `client_secret`, `refresh_token`, account number) → solo en `.env` local,
  nunca en el repo. Ver `.env.example`.

> Gestión del proyecto en Jira: **PCO** (inforge.atlassian.net).
> Los videos de training (`video/`) y los zips (`dist/`) no se versionan — ver `.gitignore`.
