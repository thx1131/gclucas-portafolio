# CLAUDE.md — gclucas-portafolio

Contexto para Claude Code. Leer completo antes de tocar código. Última actualización: 2026-09-05 (auditoría de bugs/inconsistencias del sitio: contacto falso, /text/ placeholder indexable, og:image genérico, statements vacíos, título duplicado).

## Qué es esto

Portafolio estático multipágina del artista visual GC Lucas (Lucas de la Garza), en producción en **https://gclucas.art** con contenido real: **~143 obras en 24 series**. Motor propio de generación: **Atelier v2.0** (Python).

- Repo: `https://thx1131@github.com/thx1131/gclucas-portafolio.git` (rama `main` = producción)
- Codebase local: `~/Documentos/gclucas-portafolio/`
- Pipeline de imágenes (scripts + venv): `~/Documentos/obras-extraccion/`
- Hosting: Cloudflare Pages (deploy automático en push a main)
- Imágenes: Cloudinary, cloud name `dt2w4nxz6`, public_id `obras/{ID}`
- Luis = implementador técnico y gatekeeper editorial. Lucas = contenido y dirección creativa.

## Arquitectura (NO revertir sin discutirlo)

```
data/series.json + data/works.json (FUENTE CANÓNICA — se edita directo)
  → build/build_site_v2.py
  → HTML estático pre-generado (SEO: meta/OG únicos por página)
  → git push → Cloudflare Pages
```

⚠️ **Cambio 2026-09-04**: el Google Sheet + Excel + `excel_to_json.py` quedaron **retirados del flujo activo**. El Sheet es ahora un archivo histórico de referencia, ya no se sincroniza ni se re-exporta. Ver "Pipeline de imágenes" abajo.

**Aprobado 2026-09-04, en implementación**: mover la ejecución de `build/build_site_v2.py` del laptop de Luis al build de Cloudflare Pages, para que cada push a `main` genere el HTML en CI en vez de depender de que Luis lo regenere y commitee local. Hecho de este lado (Claude): `.python-version` (fija Python 3.13) y `_load_json`/`_load_template` ahora abortan el build (exit ≠ 0) si falta un archivo requerido o el JSON es inválido — antes fallaban en silencio (exit 0) e igual publicaban una página rota. Pendiente del lado de Luis: configurar en el dashboard de Pages el build command y build output directory (ver sección de abajo con los valores exactos).

⚠️ **Riesgo de deriva del HTML versionado, mientras se siga commiteando como fallback**: una vez que el build corre en CI, el HTML del repo puede quedar desincronizado de lo realmente publicado si Luis hace push a `data/` o `templates/` sin regenerar local antes de commitear. gclucas.art reflejará el build de CI (que sí regenera en cada push), pero el HTML que queda versionado en git dejará de ser un espejo fiel de lo publicado — deja de servir como "lo que ves en git es lo que hay en producción". Decisión pendiente: dejar de versionar el HTML generado una vez confirmado que el build en CI es confiable (varios deploys exitosos seguidos).

Principios fijos:
1. **HTML pre-generado**, nunca renderizado client-side. Vanilla HTML/CSS/JS, cero frameworks.
2. **URLs limpias**: `/work/pixelogue/` (carpeta + index.html), nunca `.html` visible.
3. **IDs inmutables**: formato 3 letras + 3 dígitos (`PEL001`). Jamás cambian, aunque la serie se renombre.
4. **Los JSON en `data/` son la fuente canónica** — se editan directo, a mano o con scripts. Ya no hay una fuente editorial externa que "gane": lo que está en `data/series.json` y `data/works.json` es la verdad. (Hasta 2026-09-04 la regla era la inversa: todo cambio entraba por Google Sheets → JSON, nunca al revés — ver arriba.)
5. Sitio **solo en inglés** (sin toggle bilingüe).
6. Colores en CSS custom properties, no en JSON. Fuente: Carlito (Google Fonts). ⚠️ Nota 2026-09-04: `data/site.json` tiene un bloque `colors` que **no lee `build_site_v2.py`** — es un duplicado muerto de lo que ya vive en `css/main.css :root`. Se actualizó por consistencia al cambiar `--text-light`, pero técnicamente no hace nada; evaluar borrarlo del JSON para no mantener dos fuentes de la misma info.

## Comandos frecuentes

```bash
# Regenerar sitio (tras cualquier cambio en data/ o templates/)
cd ~/Documentos/gclucas-portafolio && python3 build/build_site_v2.py

# Probar local
python3 -m http.server 8000

# Publicar
git add . && git commit -m "feat|fix|docs: ..." && git push
```

Pipeline de imágenes (en `~/Documentos/obras-extraccion/`, activar venv primero):
- `extract_pptx_v2.py` — extrae imagen principal por slide, matchea IDs vía Excel (maneja fills, duplicados apilados, nombres multilingües/seriados)
- `verificar.py` — cruza IDs del Excel vs carpeta local de imágenes
- `cloudinary_sync.py` — upload idempotente a `obras/{ID}` con tags de serie → `cloudinary_urls.json`
- `excel_to_json.py` — **retirado del flujo activo (2026-09-04)**. Ya no se ejecuta como parte del proceso normal: `data/series.json` y `data/works.json` son la fuente canónica y se editan directo. El script se conserva en el repo sin borrar, por si hace falta para una migración masiva futura.

Regla: editaste `data/` o `templates/` → regenera antes de push. Solo `css/` o `js/` → push directo.

## Migración del build a Cloudflare Pages CI (2026-09-04)

Configuración a poner en el dashboard de Pages (Build & deployments):
- **Build command**: `python3 build/build_site_v2.py`
- **Build output directory**: `/` (raíz — el script escribe ahí mismo, no genera `dist/`)
- **Root directory**: sin cambios, `/`
- Python queda fijado por `.python-version` (3.13) en la raíz del repo; no hace falta setear `PYTHON_VERSION` a mano.
- No hace falta `requirements.txt` — `build_site_v2.py` es 100% stdlib, sin dependencias.

Qué revisar en el log del primer deploy para confirmar que funcionó:
- Debe aparecer el bloque `🎨 ATELIER v2.0 - Multipágina SEO-Optimizado` seguido de los `✅ Created: ...` por cada página (home, statement, work index, cada serie, texts, bio, contact, sitemap).
- Build debe terminar en **success**, no solo "sin errores visibles" — si falta un archivo requerido (cualquier JSON de `data/` o cualquier template salvo `text-detail.html`), el build ahora aborta con `❌ Error fatal: ...` y exit code ≠ 0, y Cloudflare debe marcar el deploy como fallido y mantener el último deploy bueno.
- Comparar una página al azar (ej. `/work/ficciones/`) entre el HTML servido en gclucas.art y el HTML commiteado en git — deberían ser idénticos mientras no haya deriva (ver advertencia arriba).

## Hoja de proyecto-cotejo.xlsx

Hoja maestra de cotejo/verificación editorial (distinta del `HOJA_DE_TRASPASO_lucas.md` roto de la sección Referencias). Vive en dos copias:
- `~/Documentos/obras-extraccion/Hoja_de_proyecto-cotejo_sin_url.xlsx` (original, sin columna de URL)
- `~/Documentos/gclucas-portafolio/Hoja de proyecto-cotejo.xlsx` (copia con URL pública, agregada 2026-09-04) — **gitignorada** (`*.xlsx` en `.gitignore`), nunca se sube al repo.

Estructura (hoja única "En español", 1011 filas, 24 bloques de serie por celdas fusionadas en A–D, 144 filas de obra): `No Serie / Nombre serie / Textos en Dossier / Textos en Portafolio / No de obra / Nombre obra / Medidas / Materiales / Año / Obra en Dossier / Obra en Portafolio / ID Interno / URL Pública`.

- **Hallazgo**: el `statementEs` que vive en `data/series.json` no siempre viene de la columna D ("Textos en Portafolio") — para `berser-k` (la cita de Fernando Gonzalez Gortázar), D está vacía en el Excel y el texto real está en C ("Textos en Dossier"). El pipeline `excel_to_json.py` hace algún tipo de fallback D→C que no está documentado; revisar el script si se toca esa lógica.
- **2026-09-04**: se agregaron dos columnas nuevas al final (N: `Statement EN`, O: `Materiales / Technique EN`) en la copia del repo, con las traducciones hechas esta sesión, para cotejo visual lado a lado con C/D y H. Mismo estilo y fusión de celdas que las columnas originales. Emparejado por `Nombre serie` (para N) e `ID Interno` (para O) — **de nuevo el gotcha de IDs como float** (ver Gotchas): la serie `archeology-road` tiene IDs numéricos (`2985001`, etc.) que Excel entrega como float y hubo que castear a string vía `int()` para matchear contra `data/works.json`.
- Esta hoja **no alimenta el build** (no la lee `build_site_v2.py`) — es solo para cotejo humano. Las columnas N/O son manuales, no se regeneran solas; si el Sheet fuente cambia, hay que repetir el volcado a mano o formalizarlo en `excel_to_json.py`.

## Gotchas (aprendidos a golpes)

- **IDs numéricos del Excel llegan como float** → castear a `int` antes de str. Ya manejado en `extract_pptx_v2.py` y `cloudinary_sync.py`; recordarlo en scripts nuevos.
- **SSL de Cloudflare debe quedarse en "Full"** (no Flexible, no Full Strict). Cambiar esto rompió el sitio antes (Error 522).
- **Git remote lleva el usuario embebido** (`thx1131@github.com`) para evitar credenciales cacheadas de otra cuenta (`sistemaskmmp`). No "limpiar" la URL.
- **Deploy que no actualiza**: revisar en el diff del commit que los archivos VIEJOS realmente se reemplazaron (no solo que se agregaron nuevos). Ya pasó: se copiaron carpetas nuevas pero index/css/js quedaron viejos.
- **Caché**: si GitHub está bien pero gclucas.art se ve viejo → Cloudflare → Caching → Purge Everything.
- **Conflicto de la serie Filippo** se resolvió con fingerprinting de imágenes a nivel de pixel; si reaparece ambigüedad serie/numeración, usar ese método.
- "Uploaded 0 files" en el deploy = el commit no cambió nada realmente; revisar `git status` antes de asumir bug de Cloudflare.
- **Archivo personal suelto en la raíz del repo, sin trackear**: `MP_1396036171.pdf` (ficha de pago interbancario BBVA/Infonavit a nombre de Luis, con CLABE). No tiene relación con el proyecto ni está en el historial de git. Nunca se debe agregar al repo — si reaparece un archivo así (descargas que caen por error en `~/Documentos/gclucas-portafolio/`), avisar a Luis para que lo mueva, no commitearlo.

## Bugs abiertos (backlog corto)

> Verificado por Claude 2026-09-04 contra el estado real del repo (ver "Verificación Claude" abajo). Los ítems 4 y 5 de la versión anterior de esta lista ya estaban resueltos y se quitaron.

1. **Dark mode arranca según preferencia del sistema; debe defaultear a light.** (js/darkmode.js) — confirmado: `getInitialTheme()` cae a `prefersDark ? 'dark' : 'light'`, y el listener de `matchMedia('(prefers-color-scheme: dark)')` reaplica ese fallback si el usuario cambia el tema del SO. Fix: hardcodear el fallback a `'light'` (y evaluar si el listener de cambios de sistema debe seguir existiendo).
2. **Bio tiene lorem ipsum** — esperando texto de Lucas. Confirmado en `data/site.json` (`bioEn`/`bioEs`) y en `bio/index.html` generado. Además `templates/home.html` tiene un **segundo párrafo de lorem ipsum hardcodeado directo en el template** (el de "Duis aute irure...") que no viene de `data/site.json` — ver punto 8 más abajo, es un problema aparte de disciplina de fuente única.
3. **SUE006 aparece "pendiente"** (sin imagen) en la serie visión de filippo — confirmado, `cloudinaryUrl: ""` en `data/works.json`. Reservado para imágenes que Lucas enviará.
4. ~~Carpeta huérfana `{build,templates` en la raíz del repo~~ — **resuelto 2026-09-04**, borrada junto con `work/nude-revisited/`.
5. ~~`work/nude-revisited/` es output huérfano~~ — **resuelto 2026-09-04**, carpeta borrada. Confirmó que "reviseted" no es un bug de build sino que **vive en el Google Sheet / `data/works.json`+`series.json`**; la decisión de naming sigue pendiente de Lucas (ver backlog de abajo).
6. **`templates/home.html` tiene bio parcialmente hardcodeada fuera de `data/site.json`.** El párrafo "Duis aute irure..." está escrito directo en el template y no sale del JSON — viola el principio 4 de Arquitectura (fuente única). Cuando llegue el texto real de Lucas, hay que asegurarse de que **ambos** párrafos salgan de `site.json`, no solo uno.
7. **Dark mode toggle podía verse opaco/con bajo contraste en modo oscuro** — resuelto 2026-09-04: el glyph de texto `◐` dependía de cómo cada fuente/SO lo renderizaba (en algunos casos no seguía `currentColor`). Se reemplazó por dos íconos SVG (sol/luna) con `stroke="currentColor"` en `templates/components/navbar.html`, garantizando que sigan el color del tema en ambos modos.
8. **Botones prev/next del modal de galería quedaban tapados por el scroll interno en imágenes altas / laptops de poca altura** — resuelto 2026-09-04: `.modal-nav` ahora usa `position: sticky; bottom: 0` dentro de `.modal-content`, así los botones quedan siempre visibles sin necesidad de scrollear.

## Sesión 2026-09-04: traducción EN + fixes de UI (commits `3b00bb6`, `ac4ca46`, `4af7165`)

- **Ficha de obra (modal de galería) reformateada**: orden fijo título (negrita) → dimensions → technique → date, sin las etiquetas "Technique:"/"Dimensions:". Cambios en `templates/series.html` (orden de los `<p>`), `js/gallery.js` (se quitaron los prefijos hardcodeados) y `css/main.css` (`.modal-info h3 { font-weight: 700 }`).
- **Color de texto**: `--text-light` pasó de `#1a1a1a` a `#333333` (carbón, no negro puro) en `css/main.css`.
- **Statements de críticos con formato de cita**: 4 series (`berser-k` → Fernando Gonzalez Gortázar, `pausa` → Ana Elena Mallet, `saga` → Rocío Cerón, `trece-lunas` → Carlos Monsiváis) tenían el nombre del autor pegado al final del párrafo del statement. Se separó a un campo nuevo `statementAuthor` en `data/series.json`, y `build_site_v2.py` lo renderiza como `<p class="statement-author">— {nombre}</p>` (cursiva, color accent) en vez de texto corrido. (`excel_to_json.py` no genera este campo, pero ya no importa: el script está retirado del flujo — ver Arquitectura.)

## Sesión 2026-09-05: auditoría de bugs/inconsistencias del sitio

Luis hizo una revisión manual del sitio y reportó 7 hallazgos (impacto alto/medio/bajo). Se resolvieron los de impacto alto y medio; los de pulido menor quedan en backlog abajo.

- **Formulario de contacto era un callejón sin salida silencioso**: `templates/contact.html` no tenía `action`, y `js/main.js` hacía `preventDefault()` + `alert('Thank you...')` + `reset()` sin enviar nada a ningún lado — el visitante creía que su mensaje se envió y Lucas nunca lo recibía. Resuelto: se quitó el `<form>` en `index.html`, `templates/home.html`, `contact/index.html` y `templates/contact.html`, reemplazado por una línea de links directos (`email · whatsapp · instagram`, ya funcionales). CSS (`.contact-form`, `.contact-info`) y JS (listener de submit) limpiados en consecuencia.
- **`/text/` es placeholder indexable**: tenía lorem ipsum y dos links "read more" a páginas que no existen (`/text/ficciones/`, y `/text/peligro-extincion/` que ni siquiera coincide con el slug real `peligro-de-extincion`), y estaba en `sitemap.xml` — Google la rastrearía y pegaría contra 404s. Se decidió **no borrar el contenido/templates** (esperando texto real de Lucas para definir el formato), solo hacerla no pública/no indexable mientras tanto: sacada de `sitemap.xml` (`build_sitemap` en `build_site_v2.py`), `<meta name="robots" content="noindex, nofollow">` agregado solo a esa página (nuevo placeholder `{{robots_meta}}` en `templates/base.html`, parámetro `noindex=False` en `_build_full_page`), y `Disallow: /text/` en `robots.txt` (estático, no lo genera el build). La página nunca estuvo linkeada desde navbar/footer, así que no hacía falta tocar navegación.
- **og:image genérico (picsum.photos random) en casi todas las páginas**: home, statement, work, bio y contact usaban `picsum.photos/1200/600?random=...` como imagen de preview social — cualquiera que compartiera el link en WhatsApp/redes veía una foto random sin relación con el arte. Solo las páginas de serie individual (`/work/{serie}/`) ya usaban su `coverImage` real. Resuelto: nuevo atributo `self.default_og_image` en `SiteBuilder.__init__` (usa `site_data.get('heroImage', ...)`, mismo fallback que ya usaba el hero de home: `obras/PEL004` en Cloudinary), reutilizado en esas 5 páginas. `/text/` se dejó con el picsum placeholder a propósito, ya que no se indexa de todas formas. Páginas de serie individual no se tocaron.
- **Statements vacíos mostraban "..." literal**: las 3 series sin `statementEn` (`h2o`, `naranja-dulce`, `trompe-l-oeil`) mostraban `<p>...</p>` en las tarjetas de `/work/`. Resuelto: `build_work_index` ahora omite el `<p>` del extracto si `statementEn` está vacío. **El `meta description` vacío de esas 3 páginas de serie individual queda pendiente a propósito**, hasta que Lucas mande esos textos — no se tocó.
- **`<title>` duplicado en TODAS las páginas** (hallazgo nuevo, no reportado por Luis, encontrado al verificar el fix anterior): `templates/base.html` tenía `<title>{{title}} | gclucas</title>`, pero cada page builder ya arma el título completo con el sufijo incluido (ej. `f"{series['titleEn']} | gclucas"`, o `"gclucas | visual artist"` para home) — resultado: `<title>pausa | gclucas | gclucas</title>` en cada página del sitio. Resuelto: `base.html` ahora usa `<title>{{title}}</title>` sin sufijo extra. `og:title`/`twitter:title` no tenían este problema (no llevaban sufijo agregado en el template).
- **Los 3 pulidos menores de arriba también se resolvieron** (misma sesión, segunda pasada, verificado con Playwright headless contra `python3 -m http.server`):
  - Extractos de statement: nuevo helper `_truncate(text, length=100)` en `build_site_v2.py` corta en el último espacio antes del límite (`rsplit(' ', 1)`) en vez de partir la palabra. Usado en el excerpt de `/work/` y también en el `meta description`/`og:description`/`twitter:description` de cada serie (antes `[:160]` directo, mismo problema).
  - Smooth scroll: el selector en `js/main.js` era `a[href^="#"]`, pero los links reales llevan path (`/#statement`). Ahora usa `a[href*="#"]`, separa `path`/`hash` del `href`, y solo hace `preventDefault()` + scroll si `path` coincide con `window.location.pathname` (si no, deja que el navegador navegue a home normal y salte el hash ahí — no se puede hacer smooth-scroll cross-page en un solo click).
  - `aria-label="close"` agregado al botón `×` del modal (`templates/series.html`).
- **Bug nuevo reportado por Luis, no en la lista original**: los botones "← previous / next →" del modal de galería eran casi invisibles en dark mode hasta pasar el mouse encima. Causa: `.modal-nav button` nunca definía `color` explícito, así que el navegador aplicaba su color de botón por defecto (casi negro) en vez de heredar el texto del tema — invisible sobre `--bg-dark: #1a1a1a`. El `:hover` sí forzaba `color: white`, por eso solo se veía al pasar el mouse. Resuelto con `color: var(--text-light)` / `var(--text-dark)` explícitos en `.modal-nav button` y `body.dark-mode .modal-nav button` (`css/main.css`).
- **Rediseño del bloque de contact-links** (reportado por Luis como bug de color + pedido de ajustes de layout, misma sesión, tercera pasada): los links de `.contact-links` (`email · whatsapp · instagram`) salían con azul default del navegador para Luis. **No se pudo reproducir en Chromium headless local ni contra la CSS ya deployada en producción** (se comparó byte a byte `css/main.css` local vs `https://gclucas.art/css/main.css` — sin diferencias, y el color computado ya daba `--text-light` correcto); posibles causas no descartadas: caché de navegador de Luis, o una extensión tipo Dark Reader que sobreescribe `<a>` sin `color` propio explícito (antes dependía 100% de `a { color: inherit }` global). Se resolvió de todos modos con una regla explícita y más robusta: `.contact-links a { color: var(--text-light) }` / `body.dark-mode .contact-links a { color: var(--text-dark) }` en `css/main.css` — ya no depende de la herencia genérica. El hover seguiya usando la regla global `a:hover { opacity: 0.7 }` sin cambios (confirmado con Playwright, `matches(':hover')` + `opacity: 0.7`). Además, en la misma pasada:
  - Alineación: `.contact-content` perdió `text-align: center` y `margin: 0 auto` — ahora queda flush-left con el `h1`/`h2` "contact" (medido con `getBoundingClientRect`: mismo `left` que el heading, antes quedaba centrado con ~240-340px de indentación fantasma).
  - Nueva línea de contexto `<p class="contact-intro">reach out through any of the following</p>` arriba del link, en `templates/contact.html` **y** `templates/home.html` (comparten el mismo bloque `.contact-content`/`.contact-links`, así que el fix aplica a ambos: la página `/contact/` standalone y la sección `#contact` embebida en home).
  - `.contact-links` subió de `14px` a `19px` (rango pedido: 18-20px).
  - Espacio vertical: se midió que el gap entre `h1`/`h2` y el bloque de contenido ya era `0px` en **todas** las páginas internas (statement, bio, contact) — no había ningún `margin`/`flex-centering` vertical de por medio ni antes ni después del cambio; lo que se percibía como "centrado en el viewport" es que la página de contacto es muy corta de contenido, no un bug de centering real. No se tocó spacing vertical porque no había nada que corregir ahí — la sensación de "más presencia" viene de la línea de intro + el font-size más grande.



- ~~Traducciones EN + técnicas/materiales estandarizados en inglés~~ — **hecho 2026-09-04**: `statementEn` de las 21 series con texto (las 3 vacías —trompe-l-oeil, h2o, naranja-dulce— siguen esperando statement) y el campo `technique` de `works.json` traducidos a inglés profesional. Los títulos en español (series y obras) se respetaron sin traducir, por instrucción explícita. (Ya no aplica la advertencia de que se perdería al re-exportar el Sheet: `data/*.json` es ahora la fuente canónica, el Sheet está retirado — ver Arquitectura.)
- Imagen hero
- 3 statements de serie faltantes
- Confirmar typo "reviseted" (¿o es intencional?)
- Resolución de naming filippo (sueño vs visión) — SUE006 reservado
- Imágenes de obra nuevas
- Email de contacto definitivo
- Nombre definitivo de la serie 03
- Convención de nombres para obras seriadas ("0 quilates 1/43", etc.)
- Textos finales del Portafolio 2025

## Backlog técnico scoped, no construido

- `actualizar.sh` — script que encadene todo el pipeline (excel → json → build → push)
- Script de ruteo de extracción de imágenes desde PowerPoint (discutido, no escrito)
- Sección `/text/` — oculta hasta que exista contenido literario real
- Evaluado y en pausa: CMS headless Git-based (Sveltia + build en Cloudflare Pages + Worker OAuth). Prerequisito: mover el build al CI de Pages. Decidir qué fuente manda (Sheets vs CMS) antes de implementar.

## Estilo de trabajo con Luis

- Respuestas concisas y directas. Sin listas de opciones infladas ni preámbulos.
- **Antes de generar código, confirmar el enfoque en 1-2 líneas.** Luego código completo, no por goteo.
- Commits convencionales: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`.
- Scripts de build viven en `build/`; scripts de pipeline en `obras-extraccion/`.
- Contacto Lucas: gclucas999@gmail.com · IG @lucas.asecas · WA +52 4151511029.

## Referencias

- `ARCHITECTURE.md` — decisiones técnicas completas (existe en el repo, sin cambios detectados)
- `HOJA_DE_TRASPASO_lucas.md` — ⚠️ **no existe en el repo ni en su historial de git**. Si vive en otro lugar (Drive, escritorio), aclarar la ruta; si no, quitar la referencia.
- Referencia visual: layout editorial dos columnas estilo Lafferty

## Verificación Claude (2026-09-04)

Contrastado contra el estado real del working tree antes de escribir en este documento:

- **Conteo de contenido**: `data/series.json` = 24 series, `data/works.json` = 144 obras (el doc decía "~143", diferencia despreciable).
- **Bugs #4 y #5 de la versión anterior (robots.txt/sitemap/.gitignore borrados, instagram sin punto) ya estaban resueltos** en el working tree — coincide con los commits `b13d489` y `7c019fb`. Se quitaron del backlog y se documentan como resueltos aquí para que no se dupliquen en un futuro traspaso.
- **Bug #1 (dark mode) sigue vigente**, confirmado leyendo `js/darkmode.js` línea por línea.
- **Bug #2 (bio lorem ipsum) sigue vigente** y es más amplio de lo que decía el doc: hay lorem ipsum en `data/site.json` Y un párrafo adicional hardcodeado en `templates/home.html` que ni siquiera pasa por el JSON.
- **Hallazgos nuevos no documentados antes**: carpeta `{build,templates` huérfana (no trackeada, basura de shell), carpeta `work/nude-revisited/` huérfana (build viejo pre-typo), y la referencia rota a `HOJA_DE_TRASPASO_lucas.md`.
- No se modificó ningún archivo de código ni se hizo commit — solo lectura y verificación. `README.md` existe pero no se auditó en profundidad (no estaba en la sección de Referencias); si sigue vigente como onboarding externo, vale la pena revisarlo contra Atelier v2.0 en algún momento.
