# Pendientes

Cuaderno de trabajo. Queda **fuera de los dos manifiestos** a propósito: cambia
cada vez que se cierra o se abre algo, y si entrara, cada nota movería la raíz
del corpus y con ella la del paquete. Las cifras que describen lo publicado no
están aquí, están en [ANCHORS.md](ANCHORS.md).

Última revisión: **13 de octubre de 2026**, tras el barrido de `applied_d1`.

---

## Antes de tocar nada: cómo se reparte el trabajo

**Ninguna de las dos máquinas tiene el archivo completo**, y eso ha causado tres
errores en un solo día. Conviene tenerlo presente:

| | Mac mini | MacBook (`jagannatha`) |
|---|---|---|
| `UPLOAD-STATE.json` | **el bueno** | el de septiembre, atrasado |
| Corpus, `corrections`, `_index` | sí | sí |
| Escaneos (2 GB), OCR, informes | **no** | **sí** |
| Sube a Arweave | **sí** | no |
| Calcula la raíz del paquete | no puede | **sí** |

El monedero de Turbo es `~/.arweave/wallet.json`, enlazado a Dropbox: el saldo es
el mismo desde las dos. Al cerrar quedó en 0,003 créditos, prácticamente cero.

**No ejecutes `upload_archive.py` en el MacBook.** Su fichero de estado ve como
pendientes miles de ficheros que ya están publicados, y volvería a pagarlos. Hay
un guardián que lo impide (`scripts/UPLOAD-STATE.suelo`), pero no conviene
probarlo.

### Recalcular la raíz del paquete

En el MacBook, siempre en este orden:

```
cd ~/git_projects/vedabase-original && git pull
curl -sL https://arweave.net/raw/MQPpISw9sPH2UUWgTbe18QWLMu58LVmVbirN9R91zMM -o /tmp/rutas.json
python3 scripts/build_index.py --desde-manifiesto /tmp/rutas.json
python3 scripts/build_archive.py            # ensambla y calcula
head -2 ~/vedabase-archive/MANIFEST.sha256  # comprobar el RECUENTO
```

Ese identificador es el del 20 de septiembre; si se ha republicado desde
entonces, el vigente está en `ANCHORS.md`, en *The way in*. El `/raw/` es lo que
devuelve el JSON en bruto: sin él, la pasarela resuelve el manifiesto y sirve la
portada.

El recuento tiene que coincidir con el número de rutas del manifiesto. Si no
coincide, **para y busca la diferencia por secciones** antes de subir nada:

```
awk '{print $2}' ~/vedabase-archive/MANIFEST.sha256 | grep -v '^$' | cut -d/ -f1 | sort | uniq -c
```

Así se encontró el último error del día: `_index` en 124 donde el archivo tenía
126.

---

## Lo que queda por hacer

Nada de esto corre prisa y nada afecta a lo publicado.

### 1. La fila de `PROVENANCE.md` que lleva un número

Dice que el corpus son 107 114 ficheros; son 107 181. Se quedó vieja al añadir
los 67 ficheros del hindi.

**No actualizar el número: quitarlo.** `PROVENANCE.md` está dentro del manifiesto
y dice de sí mismo que «no lleva ninguna cifra que cambie». Esa fila es la
excepción, y por eso se queda vieja cada vez. Que remita a `ANCHORS.md`, que está
fuera de todo manifiesto y existe justamente para eso.

Cuesta unos **0,37 créditos (2,69 $)**, porque tocar ese fichero obliga a
recalcular las dos raíces y republicar los dos manifiestos. Hacerlo el día que
haya que republicar `PROVENANCE.md` por un motivo propio, no antes.

### 2. El español sí cuadra: resuelto el 13 de octubre

Las seis filas de diferencia no eran texto que faltara. Comparando ref por ref
el `.jsonl` del repo contra D1:

| libro | diferencia | qué es |
|---|---|---|
| `sb` | D1 tiene 10 refs más | las portadas de canto (`sb/1` … `sb/10`), no son versos |
| `cc` | D1 tiene 3 refs más | las portadas de lila (`cc/adi`, `cc/madhya`, `cc/antya`) |
| `bg` | el repo tiene 7 refs más | **versos duplicados en el repo** |

Los 7 del Gītā son un defecto del repo, no de D1. El español trae el verso
agrupado **y además cada verso suelto, con el mismo contenido byte a byte**:

    bg-17.8-10.md  +  bg-17.8.md  bg-17.9.md  bg-17.10.md
    bg-18.13-14.md +  bg-18.13.md bg-18.14.md
    bg-18.36-37.md +  bg-18.36.md bg-18.37.md

D1 sirve solo el agrupado, igual que el inglés, el portugués y el hindi. Quitar
los 7 sueltos (y sus 7 líneas de `bg_es.jsonl`) es lo que cuadra las cifras,
pero **mueve la raíz del corpus**: hacerlo el día que haya que republicar.

**El ruso arrastra el mismo defecto, en menor medida: 3 duplicados** (`bg-17.8.md`,
`bg-18.13.md`, `bg-18.36.md` junto a sus agrupados), y esos sí están en D1 por
duplicado. La nota de septiembre decía que el ruso cuadraba exactamente; no es
cierto.

### 2b. El árabe está en D1 y no se sirve

`lang='ar'` tiene **10 477 filas** en D1 — `bg` 627 y `sb` 9 850 — con su `url`
puesta (`/ar/library/bg/1/1/`). La portada `https://vedabase.cc/ar/` responde
200 en árabe, pero cualquier verso **redirige a la portada**:

    curl -sL -o /dev/null -w '%{http_code} %{url_effective}' https://vedabase.cc/ar/library/bg/1/1/
    → 200 https://vedabase.cc/ar/

No hay `translations/arabe/` en el repo ni una sola mención del árabe en
`ANCHORS.md`, `PENDIENTES.md`, `PROVENANCE.md` ni `README.md`. Hace falta saber
si es trabajo a medias que se dejó aparcado o algo que no debe servirse.

### 2d. `cc/madhya/9/79`: adjudicado, y aparecieron tres cosas más

Visto el impreso a 400 dpi (`mad3.pdf`, página 368 del PDF = **p. 335 impresa**),
la frase es:

> According to some, the place known as Pāpanāśana was located eight miles
> southwest of Kumbhakoṇam**.** Others say that in the district of Tinebheli
> there is a city known as Pālamakoṭā**.** Twenty miles west of there is a holy
> place known as Pāpanāśana near the river named Tāmraparṇī.

Los dos puntos estaban perdidos. La «T» mayúscula de «Twenty» a mitad de frase
delataba que un punto se había sustituido por «and that». Corregido en el
markdown y en `cc_en.jsonl`, y dado de alta en `corrections.jsonl`.

**Queda un `UPDATE` en D1**, que el clasificador del modo automático denegó dos
veces: `astro_vedabase/scripts/arreglo_cc_madhya_9_79_d1.sql`.

**`cc_en.jsonl` estaba dañado solo él** en esa entrada: «Kumbhako**n**ṇam» con
una ene de más (dos veces), «Tanjoreāñ» por «Tāñjor» y «is **the** holy place»
por «is **a** holy place». Ni el markdown ni D1 lo tienen. Pinta de pasada de
diacríticos mal aplicada sobre ese fichero: **merece un barrido del `.jsonl`
entero**, porque si pasó aquí pasó en más sitios.

### 2e. El impreso y lo que servimos no dicen lo mismo, y no es puntuación

En ese mismo purport, con la imagen delante:

| impreso (1975, p. 335-336) | lo que sirven el repo y D1 |
|---|---|
| Near **Tricinapallī** is a river named Kāverī | Near **Tiruchchirāpalli** is a river |
| Pāpanāśana **near the river named** Tāmraparṇī | Pāpanāśana**,** near the river Tāmraparṇī |
| in the district of Tāñjor **about** ten miles | de Tāñjor**,** about ten miles |

«Tiruchchirāpalli» por «Tricinapallī» no es una errata: es una modernización del
topónimo, justo lo que este proyecto existe para deshacer. **No lo he tocado**:
cambiarlo es decisión tuya, y si el criterio es revertirlo, lo primero es saber
cuántos purports más lo llevan.

### 2f. Los `.jsonl` de `bg`, `cc` y `sb`: arreglado el 14 de octubre

`PROVENANCE.md` llama canónico al `.jsonl` y dice que el Markdown por verso es
una exportación suya. Era al revés: las correcciones se aplicaron al Markdown y
a D1, y el `.jsonl` se quedó con la lectura revisada.

**Corregido en los tres libros grandes: 3.310 entradas** (`sb` 1.666, `cc` 1.581,
`bg` 63). Ahora llevan el mismo texto que el Markdown.

Lo que da garantía no es el cambio, es el método. `astro_vedabase/scripts/md_a_jsonl.py`
reconstruye los cinco campos desde el Markdown y **antes de escribir se valida
contra las entradas que ya coincidían**: reproduce **20.200 byte a byte**. Solo
entonces escribe las que difieren. Comprobado después por el camino
independiente (`cotejar_jsonl_md.py`): de 3.301 diferencias a 2, y las dos son
falsos positivos del cotejo, que compara una concatenación de campos contra un
documento lineal (en `sb/10/1/notes` los dos lados miden 33.891 caracteres).

114 entradas se dejaron como estaban: difieren solo en el marcado, y 108 son
versos citados dentro del purport, en cursiva en el `.jsonl` y en cita en el
`.md`. Reformatearlas no arregla nada.

### 2g. Los 19 libros pequeños: medidos, no tocados, y no son un solo problema

El mismo cotejo da **248 entradas** que difieren en los pequeños, pero **no se
ha escrito ni una**, porque al mirarlas de cerca son dos cosas distintas:

- **`kb/16` es el mismo problema**: el Markdown trae «falling down on the
  **hank** of the Yamunā» y «to **he** understood», que son erratas del impreso
  de 1970 adjudicadas en agosto sobre la imagen, y el `.jsonl` trae la lectura
  moderna. Aquí el Markdown manda.
- **`tqk/5` no**: ahí el `.jsonl` tiene enlaces `[[bg/7/8|…]]` y abreviaturas
  («Bs. 5.35» por «Brahma-saṁhitā 5.35») que el Markdown no tiene, y su
  estructura es otra. Volcarle el Markdown encima lo destrozaría.

Por eso la herramienta lleva un **veto por libro**: si no reproduce al menos el
95 % de las entradas que ya coinciden, no escribe en ese libro. Hoy veta 16:
`bbd`, `ej`, `ekc`, `kb`, `krp`, `lcfl`, `nod`, `owk`, `pop`, `poy`, `pqpa`,
`rv`, `ssr`, `tlc`, `tqk`, `ttp`.

Para desbloquearlos hay que enseñarle la forma del Markdown de cada uno, libro
por libro. **No vale una pasada general.**

Y quedan **77 entradas de portada** (`kb/0a`, `tlc/0b`, `ssr/0a`…) cuyo `.md`
tiene nombre propio (`preface.md`, `prologue.md`) y no se deduce de la ref: hay
que emparejarlas por contenido.

**Las otras cuatro lenguas no están cotejadas.**

### 3. `life-comes-from-life` en español, en un solo bloque

Tiene **1 entrada** donde el inglés tiene 18: el libro entero en un comentario de
179 227 caracteres. **No falta texto**, es otro troceado. Partirlo es una
decisión, no un arreglo: habría que decidir si se quiere alineación 1:1 con el
inglés a costa de reescribir las referencias.

### 4. Las etiquetas de hablante del hindi

`lcfl` mezcla 369 etiquetas latinas (`Dr. Singh.`) y 127 en devanagari
(`डॉ. सिंह:`). La convención del corpus es la latina — `pqpa` va 694 a 9 — y la
caminata 5, que sí estaba traducida, escribe `Śrīla Prabhupāda के साथ Dr. Singh`.
Uniformarlas son 496 líneas y **una decisión del usuario**, no un arreglo obvio.

### 5. Los escaneos de las cartas: en la web desde el 14 de octubre

Cada carta de `/en/library/letters/<slug>/` que tenga original escaneado lo
muestra. **4.963 de las 6.582 cartas (75,4 %)**; las otras 1.619 no lo tienen en
Vanisource.

- 5.783 imágenes descargadas y auditadas contra el índice: 0 que falten, 0 que
  sobren, 0 con tamaño distinto al de la API.
- Convertidas a WebP: **0,98 GB**, 179 KB de media, un 39 % menos que el origen.
- Subidas a `r2://vedabase-site-content/media/letters/`, comprobadas una a una
  por HTTP: **5.783 de 5.783, todas 200**.
- Columna `scan_files` en D1: 4.963 filas.
- La plantilla las sirve enteras, con carga diferida, después de la
  transcripción. El 82,7 % de las cartas es una sola página.

El detalle y las dos trampas del camino están en
`astro_vedabase/scripts/letter_scans/PROGRESS.md`. Resumen de las trampas: la
API de R2 admite unas 4 peticiones/s y por encima devuelve 429 y luego 403 del
WAF; y **R2 responde 403 a una clave que acaba en punto**.

Lo único que queda: 6 cartas emparejadas se quedan sin original porque Vanimedia
lista la ficha del fichero y no sirve el fichero.

## Lo que ya no hay que hacer

Escrito para que nadie lo reabra por error. El detalle y el porqué están en
`ANCHORS.md`.

- El ruso está completo: 22 libros, los diez cantos del Bhāgavatam, publicados y
  alcanzables por ruta.
- El hindi también: 22 libros, con `lob` y `lcfl` rematados el 20 de septiembre.
- Los `.jsonl` rusos están reparados — sección, tipo de contenido y texto.
- `build_archive.py` ya no cuenta `ocr-surya` en el manifiesto, y se niega si lo
  encuentra sin `ocr-packed`.
- `upload_archive.py` se niega a arrancar con un fichero de estado atrasado.
- `build_index.py` puede tomar su lista del manifiesto publicado
  (`--desde-manifiesto`) en vez del disco de la máquina de turno.
- El flag `applied_d1` de `corrections.jsonl` está al día (13-oct). Decía que
  1 554 correcciones seguían sin aplicar; 1 547 ya lo estaban. Quedan 8 en
  `false`: las 7 de arriba y `krp/2`, descartada en agosto. El método: contar la
  cadena vieja y la nueva en el markdown del repo y en la fila de D1, y comparar
  los dos recuentos. No volver a fiarse del flag sin ese recuento.
- Octubre: la nota editorial de `770528mevrn` (la lectura dudosa «He is/His
  granddisciple») y los purports del apéndice que SB 4.29.1 y 4.29.2 llevaban
  pegados por duplicado. Las dos erratas del impreso del Gītā («ultilize» en
  2.7, «concommitant» en 13.8-12) están en D1 y en `PRINT_ERRATA.md`.
- Los 7 arreglos de D1 del 14 de octubre están aplicados y comprobados en vivo
  con la caché desactivada: los 5 purports a los que al aplicar una corrección
  de agosto se les movió o se les perdió el punto final (`cc/madhya/9/79`,
  `cc/madhya/8/168`, `sb/3/9/2`, `cc/madhya/8/288`, `cc/adi/7/133`) y las 2
  correcciones que nunca habían llegado a D1 (`ej/1`, `transcripts/740212bgvrn`).
  `corrections.jsonl` queda con una sola fila en `false`: `krp/2`, descartada.
- Los cuatro `chapter_title` de SB que el flag daba por pendientes no viven en
  `verses`: están en `astro_vedabase/content/en/sb/{1,3,6,9}.md` y en
  `src/lib/chapter-names.json`, y los cuatro están bien.

---

## La lección que más sirvió

**El recuento es la comprobación.** Los tres errores graves del 20 de septiembre
se encontraron comparando un número de ficheros con otro, nunca leyendo el código
ni mirando una suma de verificación:

- 131 704 contra 107 868 — el OCR suelto colándose en el paquete
- 21 235 contra 107 868 — una raíz calculada en la máquina incompleta
- 124 contra 126 — el índice dos páginas por detrás

Antes de anclar cualquier cosa, contar. Y antes de creerse un recuento,
compararlo con otro obtenido por un camino distinto.
