# Companion "1065 estándar — walkthrough verificado en CCH Axcess (SALVIN7)"

**Fecha:** 2026-06-17
**Decisión base:** Opción B (extender el funcional de Mapping v2.3) materializada como
**documento companion nuevo** en estilo Tenfold, con **capturas embebidas**. No se toca el v2.3.

## Objetivo

Producir el efecto de que Claude "mira" los 3 videos del caso SALVIN7 (screencast de armado
del 1065 estándar en CCH Axcess): combinar lo que se **dice** (transcript con timestamps) con lo
que se **muestra** en pantalla (frames), y volcarlo en un walkthrough paso a paso que llene el
hueco del v2.3 (que cubre el 1065 estándar solo en abstracto: 8 etapas + mapping campo a campo,
sin "Flujo paso a paso en CCH Axcess" para el caso estándar).

## Insumos ya producidos

- Transcripts: `whisper-salvin/out/part{1,2,3}.txt` y `.srt` (whisper large-v3-turbo-q5_0, ES,
  glosario técnico, timestamps). Build CPU plano (el BLAS crashea en Ryzen 7 5700 / sin AVX-512).
- Videos: `Perchik/video/PART {I,II,III} SALVIN7 LLC.mp4` (16.9 / 9.6 / 10.4 min).

## Pipeline

1. **Extracción de frames por cambio de escena** — ffmpeg `select='gt(scene,T)'` + `metadata=print`.
   Calibrar umbral sobre PART I (objetivo ~30-80 frames crudos/video). Respaldo: frame mínimo cada ~90 s.
2. **Alineación** — cada frame `MM:SS` ↔ segmento(s) del `.srt`. Salida `alignment.json`.
3. **Visión** — Claude describe cada frame: pantalla/form de CCH, campos/valores, acción.
4. **Síntesis sobre taxonomía v2.3** — orden de los videos:
   - PART I → Basic Data · Estructura societaria + filing · Partners→K-1
   - PART II → Income/Deductions · Schedule M-1 / M-2
   - PART III → Foreign: 8804/8805, K-2/K-3
5. **Render Tenfold** — skill `tenfold-perchik-doc-style` (style.css/template.html → build.py/WeasyPrint).

## Estructura del documento

1. Portada + intro (qué es, cómo leerlo, leyenda de badges, nota "complementa v2.3").
2. Mapa rápido: 3 videos ↔ 8 etapas.
3. Walkthrough paso a paso: por paso → captura embebida + "qué se hace" + ref de minuto + badge
   (`AUTO`/`REGLA`/`MANUAL`/`CHECK`) + puntero a fila de mapping del v2.3 cuando aplica.
4. Hallazgos: confirma/contradice v2.3 (insumo para v2.4).

## Curaduría

Reviso todos los frames; curo ~6-12 por video (≈20-35 total) a ancho de columna, frame completo.

## Entregables

- `whisper-salvin/out/frames/` — frames crudos + `alignment.json`.
- `whisper-salvin/walkthrough.md` — línea de tiempo anotada (revisable antes del PDF).
- `docs/1065 estándar - Walkthrough CCH Axcess (SALVIN7).pdf` — entregable final.

## Datos sensibles

Capturas de declaración real (EIN, socios, montos). Default: **sin redactar** (artefacto interno,
el v2.3 ya usa datos reales). Redacción de EIN/SSN/montos disponible si se pide.
