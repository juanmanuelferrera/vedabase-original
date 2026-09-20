# Pendientes

Cuaderno de trabajo. Queda **fuera de los dos manifiestos** a propósito: cambia
cada vez que se cierra o se abre algo, y si entrara, cada nota movería la raíz
del corpus y con ella la del paquete. Las cifras que describen lo publicado no
están aquí, están en [ANCHORS.md](ANCHORS.md).

Última revisión: **20 de septiembre de 2026**, al cerrar el archivo.

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

### 2. El español no cuadra con la base de datos

Seis filas de diferencia, y son anteriores a septiembre de 2026:

| libro | D1 | repo |
|---|---:|---:|
| `bg` | 658 | **665** |
| `cc` | **11 364** | 11 361 |
| `sb` | **8 287** | 8 277 |

No se sabe qué lado tiene razón. Ruso, hindi y portugués cuadran exactamente en
los 22 libros de cada uno, así que esto es solo del español.

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

### 5. `astro_vedabase` tiene 33 ficheros sin comitear

Cabeceras, pies y traducciones de interfaz. Son trabajo del usuario, no de este
proyecto. No tocar sin preguntar.

---

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
