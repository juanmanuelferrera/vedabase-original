# Pendientes

Cuaderno de trabajo. Queda **fuera de los dos manifiestos** a propósito: cambia
cada vez que se cierra o se abre algo, y si entrara, cada nota movería la raíz
del corpus y con ella la del paquete. Las cifras que describen lo publicado no
están aquí, están en [ANCHORS.md](ANCHORS.md).

Última revisión: **20 de octubre de 2026**, tras decidir que no se republica. Lo que quedó abierto está marcado como tal.

---

## Antes de tocar nada: el mini es la única máquina

**Desde el 19 de octubre, todo se hace en el Mac mini.** Al MacBook se entra por
Tailscale y Parsec, es decir, se entra al mini desde él: ya no es una segunda
máquina con trabajo propio. Allí `git_projects` está renombrado a
`git_projects_OLD`, que es donde seguían los escaneos.

Lo que faltaba aquí se trajo ese día por `rsync` sobre Tailscale, contado en los
dos extremos:

| | ficheros | tamaño |
|---|---:|---:|
| `scan_vedabase/originals` (los PDF) | 102 (71 `.pdf`) | 2 124 580 394 B |
| `scan_vedabase/surya_ocr` | 35 529 | 139 MB |

Con eso el mini ya reúne **todo** lo que `build_archive.py` necesita —corpus,
escaneos, OCR y el registro de auditoría—, que era lo único que le impedía
calcular la raíz del paquete. Dos avisos que siguen valiendo:

- **El disco va justo**: quedan unos 7 GiB libres de 228.
- **El `MANIFEST.sha256` que hay en `~/vedabase-archive` del mini es el del 17
  de septiembre** —103 481 ficheros, `_index` en 124, la firma exacta del error
  de aquel día—. No vale para nada: al reconstruir hay que contar de cero y
  comparar por secciones. El `UPLOAD-STATE.json` de aquí sí es el bueno
  (107 763 subidos).

El monedero de Turbo es `~/.arweave/wallet.json`, enlazado a Dropbox. Al cerrar
quedó en 0,003 créditos, prácticamente cero.

**No ejecutes `upload_archive.py` en el MacBook**, aunque ya no haya motivo para
ejecutar nada allí. Su fichero de estado ve como pendientes miles de ficheros
que ya están publicados, y volvería a pagarlos. Hay un guardián que lo impide
(`scripts/UPLOAD-STATE.suelo`), pero no conviene probarlo.

### Recalcular la raíz del paquete

En el mini, siempre en este orden:

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

Todo esto se deja escrito por si algún día hay que republicar. **No es el plan**:
ver la decisión del 20 de octubre, abajo.

---

## Lo que queda por hacer

Nada de esto corre prisa. Lo que sigue abierto, en una línea cada cosa:

1. ~~Republicar.~~ **Decidido el 20 de octubre: no se republica.** Ver abajo.
2. ~~Aplicar `arreglo_d1_2026-10-18.sql`.~~ **Hecho el 18 de octubre**: los
   cuatro bloques entraron, 11 enunciados, y el canary pasó de 17/25 a 25/25.
   Las 4 filas del día están en `applied_d1: true`; la única que sigue en
   `false` es `krp/2`, descartada desde agosto, y ahí debe quedarse.

   **Aviso para la próxima vez que haya que tocar D1.** `wrangler d1 execute
   --file=…` **no sirve con el token OAuth**: sube el fichero al endpoint
   `/import` y ese responde `Authentication error [code: 10000]` aunque el
   token tenga `d1 (write)` y rol de Super Administrador. La vía que funciona
   es `--command`, que va por `/query`:

   ```
   npx wrangler d1 execute vedabase-search-db --remote \
       --command "$(grep -v '^--' scripts/arreglo_d1_2026-10-18.sql | tr '\n' ' ')"
   ```

   El `grep` quita los comentarios y el `tr` deja los enunciados en una línea.
   La otra salida sería exportar un API Token con `D1:Edit` en
   `CLOUDFLARE_API_TOKEN`, que sí desbloquea el `--file`.
3. **«river Kāverī» en minúscula** en `cc/madhya/9/80`, `cc/madhya/9/87` y
   `cc/madhya/1/107`, donde el impreso escribe «River Kāverī». Salió al
   adjudicar el 9.74 (ver abajo); los escaneos están aquí, así que es barato.
   Y el topónimo moderno sigue en español y portugués, una aparición en cada
   uno de `9/74` y `9/79`: el 18 de octubre se revirtió solo el inglés.
4. **Los 19 libros pequeños** (2g) y **las traducciones de varios párrafos**
   (2h). Es lo único grande que queda, y ahora está diagnosticado.

Lo demás de esta sección está cerrado y se deja escrito para que no se reabra.

### 1. La fila de `PROVENANCE.md` que llevaba un número: quitada el 18 de octubre

Decía que el corpus son 107 114 ficheros; eran 107 181. En vez de actualizar la
cifra se ha quitado, que es lo que mandaba el propio `PROVENANCE.md` al decir de
sí mismo que «no lleva ninguna cifra que cambie». Ahora la fila remite a
`ANCHORS.md`, que está fuera de todo manifiesto y existe justamente para eso.

**Sigue sin republicarse.** El cambio está en el repo y nada más: tocar
`PROVENANCE.md` obliga a recalcular las dos raíces y republicar los dos
manifiestos, unos **0,37 créditos (2,69 $)**, y el monedero quedó en 0,003. Se
hace el día que haya que republicar por un motivo propio, junto con todo lo
demás que se ha movido hoy.

### 2. Los versos duplicados del Gītā: quitados el 18 de octubre

Las seis filas de diferencia con D1 nunca fueron texto que faltara: `sb` y `cc`
traían en D1 las portadas de canto y de līlā, que no son versos, y el `bg`
español traía siete versos de más.

Eran el verso agrupado **y además cada verso suelto con el mismo contenido**:

    bg-17.8-10.md  +  bg-17.8.md  bg-17.9.md  bg-17.10.md
    bg-18.13-14.md +  bg-18.13.md bg-18.14.md
    bg-18.36-37.md +  bg-18.36.md bg-18.37.md

**Quitados los 7 del español y los 3 del ruso** (`bg-17.8`, `bg-18.13`,
`bg-18.36`), con sus líneas de `bg_es.jsonl` y `bg_ru.jsonl`. Los tres juegos de
refs coinciden ahora exactamente con el inglés: 658 entradas.

Queda una cosa, y no es de este punto: el portugués y el ruso **no tienen
`bg/0e`**, que el inglés, el español y el hindi sí tienen. No se ha mirado.

**En D1 falta borrar las 3 filas rusas.** El español nunca las tuvo
(`/es/bg/17/8` responde 301), pero `/ru/bg/17/8` responde 200 y sirve una copia
degradada del agrupado: sin devanāgarī y con el verso en una sola línea. Está en
`astro_vedabase/scripts/arreglo_d1_2026-10-18.sql`.

### 2b. El árabe: es deliberado, y hay una puerta cerrada por dentro

No era un olvido. `astro_vedabase/src/lib/i18n.ts:56` tiene el árabe como
`available: false` con una **lista blanca de 9 rutas**. Lo que pasa la lista
responde 200; lo que no, redirige a `/ar/`. Comprobado en vivo el 14 de octubre:

| ruta | |
|---|---|
| `/ar/`, `/ar/library/`, `/ar/library/bg/`, `/ar/library/sb/` | **200** |
| `/ar/library/al-aziz/`, `/ar/ravanari/` | **200** |
| `/ar/library/bg/1/` (capítulo) | **302 → /ar/** |
| `/ar/library/bg/1/1/` (verso) | **302 → /ar/** |

En D1 hay **10.477 filas**: `bg` 627 (el inglés tiene 657) y `sb` **9.850**,
que son **1.585 más que las 8.265 del inglés**. Esa diferencia habría que
mirarla: o el árabe trocea los versos de otra manera, o sobra algo.

**El `sb` árabe no es la primera edición.** Las 1.585 filas de más no eran un
troceado distinto:

| lang | cantos 11-12 | canto 10 | total |
|---|---:|---:|---:|
| **ar** | **1.570** | **1.080** | 9.850 |
| en | 0 | 555 | 8.265 |
| es | 0 | 554 | 8.287 |
| hi | 0 | 554 | 8.258 |
| pt | 0 | 555 | 8.254 |
| ru | 0 | 555 | 8.265 |

El árabe es **la única lengua con cantos 11 y 12**, que Prabhupāda no escribió:
los remataron discípulos después de 1977. Y su canto 10 tiene 1.080 entradas
donde todas las demás tienen 554-555, es decir, el canto **completo**, no la
parte que él dejó hecha. Eso es una traducción de la edición moderna de la BBT,
no de la primera edición, y choca de frente con lo que este archivo dice ser.

Hoy no se ve: los versos están tras la lista blanca y `/ar/library/sb/` no
enlaza ningún canto (comprobado). Pero las filas están en D1, y si alguien abre
la lista blanca salen a la luz 1.570 versos que no son de Prabhupāda.

**Lo que chirría:** `[...path].astro:1366` sirve audio árabe de los capítulos del
Gītā desde `/media/audio/ar/bg/chapter-NN.mp3`, y **el audio está subido y
responde** (comprobados los capítulos 1, 2 y 18: 200 `audio/mpeg`, 8-13 MB cada
uno). Pero las páginas de capítulo son justamente las que la lista blanca no
deja pasar, así que ese audio **hoy no es alcanzable por nadie**.

Abrirlo sería añadir los patrones de capítulo y verso a `landingWhitelist` (o
poner `available: true`). **Decidido el 18 de octubre: se queda cerrada.** No se
ha tocado nada: ni la lista blanca, ni las filas de D1, ni el audio. Los 1.570
versos de los cantos 11-12 y el canto 10 completo siguen sin ser alcanzables, y
el audio árabe del Gītā sigue subido y respondiendo 200 sin que nadie pueda
llegar a él.

### 2d. `cc/madhya/9/79`: adjudicado, y aparecieron tres cosas más

Visto el impreso a 400 dpi (`mad3.pdf`, página 368 del PDF = **p. 335 impresa**),
la frase es:

> According to some, the place known as Pāpanāśana was located eight miles
> southwest of Kumbhakoṇam**.** Others say that in the district of Tinebheli
> there is a city known as Pālamakoṭā**.** Twenty miles west of there is a holy
> place known as Pāpanāśana near the river named Tāmraparṇī.

Los dos puntos estaban perdidos. La «T» mayúscula de «Twenty» a mitad de frase
delataba que un punto se había sustituido por «and that». Corregido en el
markdown y en `cc_en.jsonl`, y dado de alta en `corrections.jsonl`. El `UPDATE`
de D1 quedó aplicado el 14 de octubre y comprobado en vivo con la caché
desactivada; aquí no queda nada pendiente.

**`cc_en.jsonl` estaba dañado solo él** en esa entrada: «Kumbhako**n**ṇam» con
una ene de más (dos veces), «Tanjoreāñ» por «Tāñjor» y «is **the** holy place»
por «is **a** holy place». Ni el markdown ni D1 lo tienen. Pinta de pasada de
diacríticos mal aplicada sobre ese fichero: **merecía un barrido del `.jsonl`
entero**, porque si pasó aquí pasó en más sitios.

**Barrido hecho el 18 de octubre, y sí había más.** Dos caminos:

1. `cotejar_jsonl_md.py` sobre el inglés: `cc` 11.360 iguales y 0 que difieran,
   `bg` 653, `sb` 8.261 y las 2 diferencias conocidas, que son falsos positivos
   del cotejo. El daño de este punto ya lo había barrido la pasada de 2f.
2. Buscando la *clase* de daño —consonante doblada alrededor de un diacrítico
   (`ṇn`, `nṇ`, `ṁm`, `ṅn`, `rṛ`…)— en los 16 `.jsonl` de las cinco lenguas.
   Casi todo lo que sale es legítimo (`Nirṛti`, `khāṅna`, 263 apariciones).

Lo único real: **`Kumbhakonṇam`, 12 apariciones, en español y portugués**, y no
solo en el `.jsonl` sino también en el Markdown. Exactamente el mismo defecto
que se adjudicó en el inglés el 9 de agosto sobre la imagen de la p. 335
impresa. Corregido en `cc_es.jsonl`, `cc_pt.jsonl`, `cc-madhya-9.78.md` y
`cc-madhya-9.79.md` de las dos lenguas, y dado de alta en `corrections.jsonl`
con `applied_d1: false`. **En D1 queda por aplicar**
(`astro_vedabase/scripts/arreglo_d1_2026-10-18.sql`, bloque 1).

De paso: tres filas de `corrections.jsonl` llevaban la clave de idioma `po` en
vez de `pt`, las tres con un fichero de `translations/portugues/`. Corregidas.

### 2e. El impreso y lo que servíamos: revertido el 18 de octubre

En ese mismo purport, con la imagen delante, había tres divergencias:

| impreso (1975, p. 335-336) | lo que servían el repo y D1 |
|---|---|
| Near **Tricinapallī** is a river named Kāverī | Near **Tiruchchirāpalli** is a river |
| Pāpanāśana **near the river named** Tāmraparṇī | Pāpanāśana**,** near the river Tāmraparṇī |
| in the district of Tāñjor **about** ten miles | de Tāñjor**,** about ten miles |

«Tiruchchirāpalli» por «Tricinapallī» no era una errata: era una modernización
del topónimo, justo lo que este proyecto existe para deshacer. **Revertidas las
tres al impreso**, en el Markdown y en `cc_en.jsonl`, y dadas de alta en
`corrections.jsonl`. **En D1 queda por aplicar** (bloque 2 del
`arreglo_d1_2026-10-18.sql`).

#### Y el barrido de topónimos que había que hacer antes de decidir

Buscados 24 nombres modernos de ciudades indias en todo el corpus inglés. Casi
todo lo que sale está en **conferencias y conversaciones** —Ahmedabad 189,
Varanasi 37, Pondicherry 25, Cochin 21—, que son transcripciones de lo que se
dijo en voz alta y no se tocan.

En los libros queda **un solo caso vivo**:

> `cc/madhya/9/74`: «went to the bank of the river Kāverī via the district of
> **Tiruchchirāpalli**». Mismo topónimo, mismo capítulo, mismo río que el 9.79.

**Adjudicado el 19 de octubre**, con los escaneos ya en el mini. Visto el
impreso a 400 dpi (`mad3.pdf`, páginas 365-366 del PDF = **pp. 332-333
impresas**), no era una divergencia sino **cinco**:

| impreso (1975, pp. 332-333) | lo que servíamos |
|---|---|
| via the district of **Tricinapallī** | via the district of **Tiruchchirāpalli** |
| a devotee of Lord Śiva**,** came to that temple**,** and | sin ninguna de las dos comas |
| the **River** Kāverī (sinónimos, traducción y purport) | the **r**iver Kāverī, las tres |

Las dos comas son el mismo defecto que se adjudicó en el 9.79: puntuación
perdida en una pasada de correcciones, y no se habría visto sin la imagen.

Aplicado al Markdown y a `cc_en.jsonl` por un mismo guion que aborta si los
recuentos no cuadran —5 sustituciones en cada uno, y después 0 restos de las
lecturas viejas—, dado de alta en `corrections.jsonl` y **aplicado en D1**
(`scripts/arreglo_d1_2026-10-19.sql`, 4 enunciados) y comprobado en vivo con la
caché desactivada. La página del escaneo que se calculó, `mad3#p0366`, coincide
con la que ya traía la corrección de agosto sobre ese mismo verso: dos caminos
independientes al mismo sitio.

(`Trivandrum` en `cc/madhya/1/115` se miró y se deja: es el nombre antiguo, no
el moderno.)

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

**Diagnosticado el 18 de octubre, libro por libro. No son 16 problemas, son
cuatro formas, y una de ellas es peligrosa.** Esto es lo que hay que arreglar:

- **El título del capítulo** (`rv`, `tqk`, y por la pinta casi todos). El `.md`
  abre con `1. Rāja-Vidyā: The King of Knowledge`; el `.jsonl` lo guarda en
  `translation` y el parser se lo deja pegado a la cabeza del `purport`. Es el
  arreglo más barato y el que desbloquea más libros.
- **Los sinónimos** (`rv`, `tqk`). El parser toma por sinónimos el primer
  párrafo de prosa. En `tqk` el `.md` sí trae sinónimos de verdad
  (`*kuntī uvāca*—Śrīmatī Kuntī said; …`) y el `.jsonl` los tiene vacíos.
- **Diferencias de texto de verdad** (`ej` «Antimaterial» contra
  «Anti-material», `ekc` 2 caracteres, `tlc` 14). Estas son las que el volcado
  tiene que arreglar, y las que justifican todo el trabajo.
- **`ssr`: el emparejamiento de refs está mal, y escribir ahí destruiría.**
  `ssr/1` en el `.jsonl` es «Discovering the Self» y `chapter-1.md` es «Learning
  the Science of the Soul»: no son el mismo texto. `ruta_md()` deriva la ruta de
  la ref y en `ssr` esa derivación no vale. **Antes de tocar `ssr` hay que
  emparejar por contenido**, como las 77 portadas.

El veto del 95 % es justamente lo que ha impedido que esto pasara. No bajarlo.

Y quedan **77 entradas de portada** (`kb/0a`, `tlc/0b`, `ssr/0a`…) cuyo `.md`
tiene nombre propio (`preface.md`, `prologue.md`) y no se deduce de la ref: hay
que emparejarlas por contenido.

### 2h. Las cuatro lenguas: medidas las cuatro, y no es la misma historia

Enseñado al parser que las traducciones guardan en `verse_text` solo la
transliteración, y que el portugués separa cada línea del verso con una línea en
blanco:

| lengua | reproduce | difieren | de esas, con corrección registrada |
|---|---:|---:|---:|
| `ru` | 99,9 % | 27 | 8 |
| `es` | 98,5 % | 289 | 68 |
| `hi` | 95,0 % | 101 | 18 |
| `pt` | 94,9 % | 65 | 27 |
| | | **482** | **121** |

**Y aquí está la diferencia con el inglés.** Allí el 83,5 % de las divergencias
se explicaban por el libro de correcciones, y por eso volcar el Markdown era lo
correcto. Aquí solo **121 de 482**. Mirando el resto, son tres cosas:

- **El mismo desfase**, p. ej. `bg/6/8` en español y en ruso, donde el Markdown
  trae `समलोष्ट्राश्मकाञ्चनः` y el `.jsonl` la lectura vieja.
- **El Markdown roto**, no el `.jsonl`: ver 2i.
- **Traducciones de varios párrafos** (diálogos de `cc/adi/4/125`,
  `cc/adi/17/152`) que el parser no sabe recoger todavía.

**No se ha escrito nada en ninguna de las cuatro**, y el escritor solo recorre
`translations/english`, así que no hay forma de tocarlas por accidente.

### 2i. Los ficheros del español con el verso repetido: quitado el 18 de octubre

Eran **156**, no 155. El recuento de septiembre se hizo con una sola pasada; este
se ha hecho con dos caminos distintos y se han mirado a mano los que no
coincidían:

| lengua | ficheros |
|---|---:|
| **español** | **156** |
| portugués, hindi, ruso | 0 |
| inglés (libros) | 0 |

De los 156, **147 son dos copias idénticas** y **9 difieren solo en el signo**:
siete en la raya (`bale,—hāse` contra `bale,--hāse`), uno en un guion suelto
(`saba,-sabe` contra `saba,—sabe`) y uno en unas comillas
(`'kṛṣṇa-rāsa-pañcādhyāya'`). Es la huella de una doble ingesta donde una pasada
normalizó el signo y la otra no.

El inglés que la nota de septiembre daba por 1 no estaba en los libros: son
kīrtanas de las conferencias, donde el mantra se repite de verdad.

**Qué copia se ha quitado, y por qué la segunda.** El `.jsonl` español respalda
la **segunda**, pero el `.jsonl` es el testigo atrasado (ver 2f y 2h): las
correcciones se aplicaron al Markdown y a D1. Así que se preguntó a producción,
con la caché desactivada, por las nueve que no son idénticas: **D1 sirve la
primera en las nueve**. Regla única, entonces: fuera la segunda. Comprobado
después: 0 repetidos en las cuatro lenguas.

El guion de `cc/madhya/10/40` sigue siendo `,-` donde el resto del corpus pone
`,—`. Eso ya no es una copia repetida, es un signo mal puesto, y está también en
D1. No se ha tocado.

### 3. `life-comes-from-life` en español, en un solo bloque

Tiene **1 entrada** donde el inglés tiene 18: el libro entero en un comentario de
179 227 caracteres. **No falta texto**, es otro troceado.

**Decidido el 18 de octubre: se queda en un bloque.** Partirlo obligaba a
reescribir las referencias en el Markdown, en el `.jsonl` y en D1, y no se gana
texto, solo alineación.

### 4. Las etiquetas de hablante del hindi: uniformadas el 18 de octubre

`lcfl` mezclaba etiquetas latinas (`Dr. Singh.`) y en devanagari (`डॉ. सिंह:`).
La convención del corpus es la latina —`pqpa` va 694 a 9— y la caminata 5, que
sí estaba traducida, ya escribía `Śrīla Prabhupāda के साथ Dr. Singh`.

Contadas de verdad, las etiquetas en devanagari eran **65**, no 127: las demás
que acaban en dos puntos son títulos (`प्रथम प्रातःकालीन भ्रमण:`, «primera
caminata matutina») y líneas de presentación, que no son turnos de palabra y no
se han tocado. Las 65 estaban todas en `chapter-1` (31) y `chapter-2` (34).

| devanagari | latina | nº |
|---|---|---:|
| `श्रील प्रभुपाद:` | `Śrīla Prabhupāda.` | 33 |
| `करन्धर:` | `Karandhara.` | 15 |
| `डॉ. सिंह:` | `Dr. Singh.` | 14 |
| `ब्रह्मानन्द स्वामी:` | `Brahmānanda Swami.` | 2 |
| `छात्र:` | `Student.` | 1 |

Hechas en el Markdown y en `lcfl_hi.jsonl`, 65 en cada uno —que los dos den 65
por separado es la comprobación—. Después: 0 en devanagari, 445 latinas.

**En D1 queda por aplicar** (bloque 4 del `arreglo_d1_2026-10-18.sql`);
`/hi/lcfl/1.md` todavía sirve las de devanagari.

Lo que **no** se ha tocado, porque no son etiquetas de hablante: la línea de
presentación de cada caminata (`श्रील प्रभुपाद के साथ डॉ. थौडम दामोदर सिंह…`) va en
devanagari en 13 capítulos y en latina en 3. Ahí la mayoría es la contraria, y
es otra decisión.

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
- **18 de octubre.** Quitada la cifra de `PROVENANCE.md`; quitados los 7 versos
  duplicados del Gītā español y los 3 del ruso; quitada la copia repetida del
  verso en 156 ficheros del español; corregido `Kumbhakonṇam` en español y
  portugués; revertidas al impreso las tres lecturas de `cc/madhya/9/79`;
  uniformadas a la latina las 65 etiquetas de hablante del hindi en `lcfl`.
  Decidido y cerrado: la lista blanca del árabe **se queda cerrada**, y
  `life-comes-from-life` en español **se queda en un bloque**.
- El barrido de topónimos modernizados está hecho sobre todo el corpus inglés:
  lo que sale en conferencias y conversaciones no se toca, y en los libros el
  único que quedaba, `cc/madhya/9/74`, se adjudicó el 19 de octubre (2e). No hay
  que volver a barrer.
- **20 de octubre: no se republica en Arweave.** Lo anclado es la raíz del 20
  de septiembre, y **describe el corpus de ese día, no el de hoy**. Desde
  entonces el repo se ha movido dos veces: el 18 de octubre (10 ficheros menos,
  162 con el texto cambiado, 7 `.jsonl` y `PROVENANCE.md`) y el 19 (el verso
  `cc/madhya/9/74` y `cc_en.jsonl`). Nada de eso está publicado ni va a estarlo.

  El porqué: republicar cuesta unos 0,37 créditos (2,69 $) solo por los dos
  manifiestos, el monedero está en 0,003, y lo que se ganaría es que la copia
  permanente incluyera un puñado de comas y dos topónimos. El texto publicado no
  está mal: está en el estado del 20 de septiembre, que es una lectura honrada
  del impreso. Lo que vive y se corrige es el repo y D1 —que es lo que la gente
  lee en vedabase.cc—, y ahí sí está todo al día.

  **La consecuencia hay que tenerla presente, no esconderla:** quien compare el
  repo con la raíz anclada encontrará diferencias, y a partir de hoy **esa
  diferencia es la esperada**. No es una raíz sin explicar —que es lo que
  `ANCHORS.md` existe para evitar—, es una decisión escrita aquí. Si algún día
  se republica, se republica todo junto y se anota allí la raíz nueva.

- **19 de octubre.** El mini pasa a ser la única máquina: traídos por Tailscale
  los 102 ficheros de escaneos (2 124 580 394 B) y los 35 529 del OCR de Surya.
  Cerrado `cc/madhya/9/74`, en el repo y en D1. `corrections.jsonl` vuelve a
  tener una sola fila en `false`: `krp/2`, la descartada de agosto.

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
