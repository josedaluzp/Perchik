# Brief — Slides "qué automatizamos" (audiencia NO técnica)

## Objetivo
Explicar, a gente no técnica (socios del estudio, management, equipo no-IT), qué se construyó:
un asistente que arma el borrador de las declaraciones **Form 1065 → CCH Axcess** leyendo
solo de Airtable + Dropbox. Que se entienda el **valor**, no la tecnología.

## Audiencia
Contadores y management de Perchik. Saben de impuestos, NO de software/IA. Cero jerga
(nada de "skills", "MCP", "9c", "§1446", "source-resolver"). Hablar de tiempo, errores,
control y trazabilidad.

## Mensaje central (una frase)
> "Le pedís *‘armá el 1065 de tal cliente’* y el asistente junta todos los datos solo, los
> deja ubicados en cada campo de CCH y te marca qué revisar. Vos controlás y aprobás."

## Tono y diseño
- Profesional, ejecutivo, claro. Nada infantil.
- Paleta tipo Perchik: navy oscuro (#0E1726) + un acento (teal/verde o brass dorado) + papel claro.
- 16:9, ~6 slides, mucho aire, una idea por slide, frases cortas.
- Íconos simples o diagramas de cajas; evitar capturas densas de código.

## Estructura (6 slides)

**1 · Portada**
- Título: "Armado asistido de declaraciones 1065 en CCH Axcess"
- Bajada: "De la carga manual a un borrador preparado por IA — Tenfold × Perchik"

**2 · El problema de hoy**
- Armar un 1065 = buscar datos en muchos lados (Airtable, Dropbox, QuickBooks, PDFs, HUDs),
  leerlos a mano y tipearlos uno por uno en CCH.
- Es lento, repetitivo y fácil de equivocarse.
- Visual: muchos documentos → una persona tipeando.

**3 · La idea**
- Un asistente que hace el trabajo pesado de **buscar y ordenar**.
- Una frase ("armá el 1065 de X") → un **borrador completo** con cada dato en su lugar.
- Visual: una frase → flecha → formulario lleno.

**4 · Cómo funciona (en simple, 3 pasos)**
- 1) Sabe **dónde vive** cada dato.
- 2) Lo **trae** de Airtable y Dropbox.
- 3) Lo **ubica** en el campo correcto de CCH y **marca qué revisar**.
- Visual: 3 cajas en fila.

**5 · Lo importante: asiste, no reemplaza**
- Cada dato viene **etiquetado**: 🟢 listo automático · 🟡 revisar antes de cargar.
- El contador **controla y aprueba**; la máquina solo prepara.
- Resultado típico: ~70–90% de la carga ya viene preparada.
- Visual: semáforo verde/amarillo + "el experto decide".

**6 · Probado y qué sigue**
- Funciona con **3 casos reales** ya probados: consulting con socios del exterior, venta de
  propiedades, y venta de acciones (cada uno con sus particularidades).
- Hoy: **borrador listo para revisar**. Próximo paso: que cargue directo en CCH.
- Corre dentro de **Claude Desktop**, sin instalar nada nuevo.

## Qué NO incluir
- Nombres de skills, diagramas de arquitectura, números fiscales finos, código.
- (Eso queda para la demo en vivo de los 3 ejemplos, después de estas slides.)
