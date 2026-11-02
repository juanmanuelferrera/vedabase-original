# vedabase-original — PROGRESS

Estado: Bhagavad-gītā en español: texto y devanagari del libro de Perú (PDF 2026-11-02b) aplicados en el repo (jsonl + .md), subido a GitHub y llevado a D1 el 2-nov (1.205 campos, verificado campo a campo; purga ×2, canary 234/0 y 11 comprobaciones en vivo OK). Ebooks, packs y ancla de Arweave sin hacer.
Siguiente: (1) revisar `~/Desktop/gita_peru_no_aplicados.tsv` (5 campos y 21 omitidos); (2) decidir si el devanagari de Perú se lleva también al inglés (pt, ru y hi ya lo llevan y están subidos); (3) ebooks es/pt/ru/hi de la Gītā y packs sin regenerar; (4) decidir si se añaden Guía del Alfabeto y Glosario de 2022 como páginas nuevas; (5) anclar la raíz del manifiesto en Arweave (`ANCHORS.md`).

## Regla de este bloque (2-nov)

- Perú manda en el español de la Gītā; el repo (`bg_es.jsonl`, canónico) es donde se escribe; D1 y ebooks salen de ahí. No se ejecuta `build_translations.py` (reconstruiría el jsonl desde otras fuentes): los `.md` se regeneran con `render_row` desde el jsonl.
- Alcance: lo que ya existía en la edición de 2022. Lo añadido para Perú (Nota del editor, Ilustraciones, Referencias, Versos e Índice General) no entra.
- Devanagari: 41 cambios en 38 versos en español, y los mismos en portugués y ruso (hindi ya traía 40 de los 41; se cambió 1). El inglés no se toca sin decisión: su `.md` es el espejo de 1972 («el papel manda»).

## Hecho (con evidencia)

- 653 bloques de verso del PDF = los 653 de `bg_es.jsonl`; 610 versos/bloques con cambios (preliminares incluidos): 3.625 ediciones (`corrections.jsonl`, 2026-11-02, `applied_d1: false`).
- Comprobado tras aplicar: mismos refs, `verse_text`/`url` intactos, nº de `*` igual en todos los campos, 21 uniones de palabras cortadas por salto de párrafo, los 20 campos que aún difieren de Perú son los omitidos listados; `check_translations_drift.py` sin deriva nueva (261, la de antes).
- Palabras pegadas (2-nov, tarde): la capa de texto del PDF omite espacios (sánscrito en cursiva, y huecos de 1,5 a 2 pt). La 1.ª pasada dejó ~40 frases pegadas y la 2.ª aún «yatantaḥca» y «saberacerca». Causa: umbral de hueco entre glifos demasiado alto; los datos separan limpio (entre letras ≤0,5 pt, entre palabras ≥1,5 pt) y el umbral ya es 1 pt. Texto rehecho desde el commit del devanagari; copia de las pasadas malas en la rama local `backup-texto-peru-pegado`.
- Comprobación independiente: de las 3.254 correcciones de `gita_peru/datos/correcciones_cuerpo.tsv` (pp. 43–744), 3.191 aparecen exactas, con espacios, en el texto extraído y ninguna solo sin espacios; las 63 restantes son filas de rondas anteriores sobrescritas o con marcas de formato. Además ninguna palabra nueva queda fuera del vocabulario del repo salvo las 47 revisadas una a una (español válido o tal como está impreso, p. ej. `ye'nupaśyanti` sin espacio).
- Tercera pasada (2-nov, noche): la 2.ª aún mezclaba el orden de fragmentos de una misma línea (8.7, 11.39: «a consiguiente; Mí;»). Causa: agrupar por borde superior en vez de por línea base. Corregido y rehecho; los espacios junto a «–» se ignoran al comparar (el PDF los estira al justificar).
- OCR independiente (tesseract, 702 págs. a 250 ppp) contra el texto extraído: 641 págs. comparables, ratio medio 0,966, 0 palabras mías que sean 2 del OCR (sin pegados) y sin desórdenes (lo que baja la ratio son líneas de sánscrito y cabeceras).
- Guiones de final de línea: se decide por el vocabulario del repo (gana la forma más frecuente; si ninguna, se conserva el guion en palabras sánscritas).

## No comprobado

- El devanagari se aplicó desde el cotejo del 2-nov (lecturas sobre imagen), no descifrando la fuente `Indevr20`. 6.8, 18.44 y 18.66 (español distinto del inglés) no se tocaron.
- Ningún verso visto renderizado en la web; D1 sigue con el texto anterior.
- Algunas frases sánscritas con avagraha quedan sin espacio antes del apóstrofo (`yathā'rudro'bdhijaṁ`), como en el PDF.

## D1 (2-nov, noche)

- Plan y SQL en `~/Desktop/d1_plan_bg_peru/` (16 ficheros, 1.226 sentencias; `rollback/` con las inversas; `verificar_d1.py`). Cada UPDATE con precondición exacta (el campo vale hoy lo que se leyó). Simulado antes en Python sobre el D1 descargado: 0 problemas.
- Ejecutado fichero a fichero con comprobación tras cada uno: devanagari es 38, pt 38, ru 38, hi 1; texto es: 554 significados, 230 traducciones, 306 sinónimos. `verificar_d1.py`: 1.205 campos previstos, 0 distintos.
- Purga completa ×2, `smoke-canary` 234 pass / 0 fail. En vivo (curl sin caché): 4.11, 9.14, 1.26, 13.1, 5.29, 2.9, 18.72 (es, pt, ru), 18.28 y 2.66 con el texto nuevo y sin el viejo.
- Rutas reales de la web: `/es/bg/<cap>/<verso>/` (la de `/library/` redirige).
- Sin hacer: ebooks (`scripts/regen_books`, desde el repo), packs, ancla de Arweave, Guía del Alfabeto/Glosario como páginas nuevas, y las 5 filas / 21 omitidos de `~/Desktop/gita_peru_no_aplicados.tsv`.
