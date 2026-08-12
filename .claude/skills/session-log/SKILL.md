---
name: session-log
description: Use when the user asks to save, log, or record what was worked on in the current Claude Code session (e.g. "guardá lo que trabajamos hasta ahora en esta sesión", "guardá el log de hoy", "guardá la sesión"). Writes/updates a dated plain-text (.txt) file in logs/ at the repo root summarizing the session — decisiones, archivos tocados, pendientes, próximos pasos. Solo local, no toca git.
---

# session-log — registro diario de sesión (local, sin git)

Este repo se trabaja localmente — no se commitea cada sesión por default.
Este skill es la forma de dejar un registro legible de qué se hizo, para
poder retomar otro día sin perder contexto, sin depender del historial de
git.

## Cuándo se activa

El usuario pide guardar/registrar lo trabajado en la sesión actual, en
cualquier variante ("guardá lo que hicimos", "guardá el log de hoy", "dejá
registro de esta sesión", etc.). No hace falta que lo pida con esas palabras
exactas.

## Qué hacer

1. **Fecha de hoy** en formato `YYYY-MM-DD` (usar la fecha real del entorno,
   no inventarla).
2. **Archivo destino:** `logs/<YYYY-MM-DD>.txt` en la raíz del repo — **texto
   plano, no markdown** (sin `#`, sin `**negrita**`, sin backticks de
   markdown — usar mayúsculas y guiones para separar secciones, como en el
   ejemplo abajo). Crear la carpeta `logs/` si no existe.
3. **Si el archivo de hoy ya existe** (segunda sesión el mismo día): NO
   sobrescribir — agregar al final un separador de línea y un encabezado de
   hora (ej. `SESION 14:30`), y continuar el resumen ahí.
4. **Resumir la conversación actual** (desde el arranque de la sesión, o
   desde el último punto ya registrado si se llama dos veces en la misma
   sesión) en estas secciones:
   - **QUE SE HIZO** — en orden, con rutas de archivo concretas (creados,
     editados, borrados).
   - **DECISIONES TOMADAS** — la decisión + el por qué (una línea alcanza si
     ya está claro en la conversación).
   - **PENDIENTE / BLOQUEADO** — qué falta y por qué está bloqueado (ej.
     "falta confirmar X en el portal", "falta que el usuario cargue Y").
   - **PROXIMOS PASOS** — lo concreto que sigue la próxima sesión.
5. **Nada de relleno.** Es un registro de trabajo para retomar contexto, no
   un reporte para un tercero — directo, en viñetas (`- `), sin repetir
   explicación de cosas ya obvias por el nombre del archivo/decisión.
6. **No commitear.** Este skill nunca corre `git add`/`git commit` — el
   registro queda como archivo local nomás, sin importar si el proyecto
   está permitiendo commits para otra tarea puntual (ej. un plan de
   subagent-driven-development). `logs/` no está gitignored por default; si
   el usuario prefiere que sí lo esté, agregarlo a `.gitignore` cuando lo
   pida, no por iniciativa propia.
7. Al terminar, confirmar al usuario la ruta del archivo escrito (una línea).

## Estructura del archivo

```
2026-08-10

QUE SE HIZO
-----------
- ...

DECISIONES TOMADAS
-------------------
- ...

PENDIENTE / BLOQUEADO
----------------------
- ...

PROXIMOS PASOS
----------------
- ...

SESION 16:45
-------------
(si hay una segunda sesión el mismo día, mismo formato acá abajo)
```
