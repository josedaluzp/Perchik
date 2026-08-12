# Diseño: cerrar las 2 brechas de income (income-passthrough-k1, sale-of-securities)

Fecha: 2026-08-12
Estado: aprobado por el usuario, pendiente de escribir en las skills.

## Objetivo

Dos módulos de income quedaron marcados **BRECHA** en v2.3 del mapping
(`docs/pendientes-mapping-v2.4-segun-videos.md`, prioridad ALTA): `income-passthrough-k1`
(holding que recibe K-1, caso SALVIN7) y `sale-of-securities` (venta de acciones, Form 8949).
Ambos tenían la regla de mapeo sin formalizar en el `SKILL.md`.

**Fuente de verdad:** los transcripts reales de los videos de training, ya en el repo:
- `trancript/salvin7-llc-consulting-fuera-de-usa/part1.txt`, `part2.txt`, `part3.txt`
- `trancript/form-8949/part1.txt`

No se infiere ni se inventa regla tributaria: se transcribe la regla exacta que el video
ejecuta, con las cifras reales como caso de prueba. Este mismo criterio aplica a futuro para
cualquier otro caso de uso de este proyecto: **el transcript de su video es la fuente de
verdad**, y el objetivo final es que la automatización reproduzca ese caso — paso a paso y
cifra a cifra — antes de generalizar la regla a otros clientes.

## Alcance

Esto es documentación de reglas (edición de `SKILL.md` + limpieza de referencias), no código.
No toca `cch-axcess-mcp/`. No requiere las credenciales de CCH bloqueadas — es trabajo 100%
independiente del bloqueo OAuth actual.

## Regla — income-passthrough-k1 (caso SALVIN7)

SALVIN7 **no** es un agregador puro de K-1: además de los 3 K-1 recibidos, tiene actividad
propia (consulting fuera de USA), que ya cubre `income-consulting-foreign`. La regla de este
módulo cubre solo la porción de los K-1 recibidos.

1. **Carga por K-1, campo por campo.** Cada K-1 recibido se abre en `Income › Partnership
   Passthrough (K-1 1065)`: nombre de la sociedad emisora, tipo (domestic/limited), % de
   participación, capital account analysis. Cada casilla del K-1 real (net rental real
   estate, interest, deductions, non-deductible expenses, business interest expense, current
   year gross receipts, etc.) se tipea 1 a 1 en el campo del mismo nombre del worksheet — sin
   cálculo, transcripción directa. (Caso SALVIN7: 3 K-1 — Airport Crossing Investors, Cherokee
   Investors, Rose Investors.)

2. **Agregación al K-2, Section 10 (US Source)** — asume que las sociedades emisoras de los
   K-1 recibidos son domésticas:
   - **Línea 6 (Interest):** sumar el interest (box 5) de todos los K-1 recibidos → columna
     US Source. (SALVIN7: 72 + 122 + 257 = 451.)
   - **Real estate (línea de income o de deductions según signo):** sumar el "net rental real
     estate income/loss" (box 2) de todos los K-1.
     - Si el neto es **positivo** → va a la línea de INCOME correspondiente, columna US Source.
     - Si el neto es **negativo** → va a DEDUCTIONS, columna US Source, y al monto se le suma
       el total de "Deductions" (box 13) de esos mismos K-1.
       (SALVIN7: neto = −6.138 −6.285 + 0 = −12.423; + (47+32+49) = **12.551**.)

3. **Excluir del K-2/K-3 los "non-deductible expenses"** de los K-1 recibidos. Esos bajan el
   capital account del socio en su propio K-1, pero no deben tocar el K-2/K-3 de los socios
   de la sociedad que los recibe. (Por esto el video acepta una diferencia de ~$8 al chequear
   K-2 == P&L — ver Verificaciones.)

4. **Balance sheet.** El ending capital account de cada K-1 recibido (letra L / capital
   account analysis) se carga como inversión/"Other Asset" en el balance de la sociedad —
   una línea por cada sociedad de la que se recibe K-1.

5. **8804.** Solo entra la porción US-source (el resultado de los K-1 recibidos, si es
   positivo) prorrateada al socio corp según su %. La actividad foreign propia de la holding
   (consulting fuera de USA) nunca toca el 8804. (Caso SALVIN7: al ser el resultado negativo,
   el 8804 queda en cero.)

### Verificaciones (CHECK)

- **K-2 total == P&L net income**, con una diferencia tolerada **únicamente** por el monto de
  los "non-deductible expenses" excluidos (regla 3). Si la diferencia es mayor a esos gastos
  no deducibles conocidos → **no forzar el cierre**, flaggear para revisión manual
  (`cross-check-engine`).
- **Σ ending capital account de todos los socios (K-1) == balance sheet "Partners' capital
  accounts"** al cierre del año. Si no cierra → revisión manual antes de imprimir.
- Si algún K-1 recibido da ganancia real estate positiva y hay socio corp con % > 0 →
  confirmar que impacta el 8804 línea 4a explícitamente (no asumir 0 — eso fue particular del
  caso SALVIN7, que dio pérdida).

## Regla — sale-of-securities (Form 8949)

Ya estaba mayormente documentada en v2.3; el transcript la confirma con un caso real y agrega
el punto 3 (crítico, no estaba explícito).

1. **Carga por venta, una fila por vez** en `Income › Schedule D, 4797, Gain and Loss ›
   Detail`. Por cada venta, copiar del 1099-B: descripción (idéntica al 1099-B), fecha de
   adquisición, fecha de venta, precio de venta, costo, `1099-B Code = A`, y short/long term
   (> 1 año = long term).
2. **Cross-check contra la fuente.** El total cargado en Schedule D/8949 debe coincidir
   exacto (o con diferencia de redondeo ≤ $1) con el total del 1099-B de origen.
3. **La exclusión de Section 1446 NO es automática en CCH — es una verificación manual
   posterior, no una configuración.** CCH carga la ganancia short/long-term en el 8804 línea
   4e y en la retención por default, igual que si fuera income gravado. La regla operativa:
   - Sumar el punto 9 de **todos** los 8805 de socios foreign → debe dar igual a la línea 4e
     del 8804 (tolerancia ~$1 por redondeo).
   - Sumar el punto 10 (retención) de todos los 8805 → debe dar igual a la retención total.
   - **Si no cierra:** no ajustar montos a mano en el 8949 ni forzar el 8804/8805 — es señal
     de que hay otro income mezclado en el 4e (o falta un socio en el 8805). Flaggear para
     revisión manual (mismo criterio que `cross-check-engine` / cadena "securities ∉ 1446"
     ya listada en `foreign-forms`).

## Archivos a cambiar

- `.claude/skills/income-passthrough-k1/SKILL.md` — reescribir con la regla de arriba.
  Quitar el banner "⛔ BRECHA" y el título "(BRECHA)". Cambiar el tag de status en la
  frontmatter (`description`) de `MANUAL. BRECHA — needs its own rule defined.` a
  `REGLA + CHECK.` (mismo formato que `sale-of-property`).
- `.claude/skills/sale-of-securities/SKILL.md` — agregar el punto 3 (verificación manual, no
  automática) y el detalle de carga fila-por-fila. Quitar "(BRECHA)" del título y el banner.
  Cambiar el tag de `MANUAL + CHECK. BRECHA.` a `REGLA + CHECK.`
- `.claude/skills/source-resolver/references/sources.yaml` — quitar las notas
  `(BRECHA: regla propia)` y `(BRECHA)` de las entradas `income.k1_received` y
  `sale.securities_1099b` (ya no aplica).
- `docs/pendientes-mapping-v2.4-segun-videos.md` — marcar como resueltos (`[x]`) los dos
  bullets de Prioridad ALTA correspondientes a estos dos casos, con una línea apuntando a
  este spec.

## Criterio de aceptación

- Las dos `SKILL.md` quedan sin ninguna mención de "BRECHA" ni "pendiente de definir".
- La regla de cada módulo, aplicada a mano sobre las cifras del transcript (SALVIN7 / Form
  8949), reproduce los mismos números que el video: K-2 real estate deductions = 12.551,
  K-2 interest US Source = 451, 8804 = 0 (SALVIN7); y la cadena Σ8805 pt.9 = 8804 4e /
  Σ8805 pt.10 = retención (Form 8949).
- Próximo paso (fuera de este spec): validar contra los forms reales de CCH — cuando el
  bloqueo OAuth se resuelva y se pueda automatizar la carga, confirmar que produce esos mismos
  3 casos de uso (SALVIN7, AGGUILU, Form 8949) tal cual describen sus transcripts, antes de
  generalizar a otros clientes.
