# Procedencia y archivo permanente

Este repositorio contiene el **texto**. El trabajo que lo respalda —los escaneos
del papel, las dos lecturas de OCR, el registro de cada discrepancia y las
herramientas que hicieron el cotejo— vive fuera, porque son binarios y ficheros
de trabajo que no tienen sitio en git.

Este fichero dice dónde está cada pieza y cómo comprobarla. La copia permanente
de todo junto se sube a Arweave, donde no se puede modificar ni retirar; los
identificadores van en la tabla de abajo conforme se publican.

## Las piezas

| Pieza | Qué es | Dónde está hoy | Tamaño | Arweave |
|---|---|---|---|---|
| **corpus** | El texto de las primeras ediciones, 102.835 ficheros | este repositorio | 767 MB | `ar://<pendiente>` |
| **escaneos** | 70 PDF de los libros impresos, incluido el Śrīmad-Bhāgavatam completo | `scan_vedabase/originals/` | 2.078 MB | `ar://<pendiente>` |
| **ocr-surya** | Lectura de cada página por el motor Surya | `scan_vedabase/surya_ocr/` | 72 MB | `ar://<pendiente>` |
| **auditoría** | Registro de las discrepancias: abiertas, arbitradas, aplicadas | `astro_vedabase/scripts/scan_audit/*.json` | 68 MB | `ar://<pendiente>` |
| **informes** | Cada diferencia junto a la imagen de la página escaneada | `.../scan_audit/*.html` | 126 MB | `ar://<pendiente>` |
| **herramientas** | El código que hizo la comparación y la aplicación | ambos repos, `*.py` | 1,1 MB | `ar://<pendiente>` |
| **manifiesto** | SHA-256 de cada fichero + hash raíz del conjunto | `MANIFEST.sha256` | 15 MB | `ar://<pendiente>` |

Para montar el paquete completo:

```
python3 scripts/build_archive.py --dry-run   # ver qué entra
python3 scripts/build_archive.py             # montarlo
```

## Cómo comprobar que el texto no ha cambiado

```
python3 scripts/hash_manifest.py --check
```

Recalcula el hash de cada fichero y lo compara con `MANIFEST.sha256`. Si el
`root` coincide con el anclado en Arweave en la fecha correspondiente, el texto
es el mismo que se publicó entonces. Si no coincide, algo cambió — y eso es
justamente lo que se quiere poder detectar.

El manifiesto prueba que **el texto no se ha alterado**. Lo que prueba que
**coincide con el papel** es el cotejo, y su registro está en `auditoría/` e
`informes/`: cada discrepancia, contra qué página se resolvió y qué se decidió.

## Anclas publicadas

Un ancla en una sola fecha no demuestra nada sobre lo que venga después. Lo que
sirve es la sucesión. Cada vez que cambia el corpus se regenera el manifiesto y
se ancla el `root` nuevo.

| Fecha | root del corpus | Transacción |
|---|---|---|
| *(pendiente)* | `1d26996b1d851271290c6640496d1ea7547b4172450093f7d69635c2b4816f29` | `ar://<pendiente>` |

## Procedencia de los escaneos

*(Por completar. Un PDF de un libro de 1972 no acredita por sí solo de dónde
salió; esto es lo que convierte un fichero en una prueba.)*

Por cada escaneo hace falta dejar constancia de:

- edición y **tirada** — no basta el año de copyright: dos volúmenes del
  Caitanya-caritāmṛta que parecían primeras ediciones resultaron ser la
  reimpresión de 1983, y solo se vio en la página de créditos
- de qué ejemplar físico procede y de quién era
- cuándo y cómo se escaneó, y a qué resolución
- si procede de una copia pública, cuál y con qué fecha

Lo ya sabido:

- **Caitanya-caritāmṛta, 17 volúmenes** — coinciden byte a byte con el item de
  archive.org subido el 24-10-2021. Los volúmenes 1 y 2 de Ādi-līlā son la
  **segunda impresión de 1983**, no la primera tirada (1974 y 1973
  respectivamente); el volumen 3 sí es de 1974. Documentado en el README.
