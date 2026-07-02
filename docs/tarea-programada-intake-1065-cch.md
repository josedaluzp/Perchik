# Tarea Programada de Cowork — `intake-1065-cch`

Encapsula todo el flujo del 1065 en una tarea que corre **cada 1 hora** en Claude Desktop.
Se crea en el diálogo **"Crear tarea programada"** (Ajustes → Tareas programadas).

| Campo | Valor |
|---|---|
| **Nombre** | `intake-1065-cch` |
| **Descripción** | `Revisa Airtable cada hora, arma los 1065 en 'CCH To do' y notifica por mail` |
| **Trabajar en un proyecto** | el proyecto donde están cargadas las skills |
| **Modelo** | predeterminado |
| **Frecuencia** | **Cada hora** |

**Prompt (pegar tal cual en el cuadro de texto):**

> Revisá en Airtable (Entity Tracker) las entidades con `Primary Form Status = "CCH To do"`.
> Por cada una, en serie (una a la vez):
> 1. Armá el borrador del Form 1065 con `return-orchestrator` (extrae datos de Airtable + Dropbox
>    y genera el mockup HTML).
> 2. Ejecutá `completion-report` para notificar por mail (conector Gmail) que el 1065 se completó,
>    con los puntos a verificar (CHECK/MANUAL/faltantes) y la referencia al mockup.
>
> NO cambies ningún estado en Airtable. Devolveme el resumen de lo procesado.

**Requisitos en la PC dedicada:** Cowork abierto, "Mantener activo" encendido, y los conectores
**Airtable + Dropbox + Gmail** autenticados en la sesión.

**Nota (idempotencia):** como no se escribe ningún estado, cada corrida reprocesa lo que siga en
`CCH To do`. El equipo saca la entidad de ese estado a mano cuando revisa el mail.
