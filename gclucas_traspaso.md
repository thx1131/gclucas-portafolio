# CLAUDE.md — gclucas-portafolio

Contexto para Claude Code. Leer completo antes de tocar código. Última actualización: 2026-09-09 (CMS Sveltia para Lucas, en implementación — ver sección dedicada).

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
data/series.json + data/works.json (FUENTE CANÓNICA — se edita directo o vía CMS)
  → build/build_site_v2.py
  → HTML estático pre-generado (SEO: meta/OG únicos por página)
  → git push → Cloudflare Pages
```

⚠️ **Cambio 2026-09-09**: `data/series.json` y `data/works.json` dejaron de ser un array en la raíz — ahora son `{"series": [...]}` y `{"works": [...]}` respectivamente (`data/site.json` no cambió, sigue siendo un objeto). Motivo: los collections de tipo "file" del CMS (ver sección CMS abajo) necesitan que cada archivo sea un objeto con nombre de campo, no un array suelto. `build_site_v2.py` y `build_site.py` ya están actualizados (`self._load_json('series.json')['series']`, ídem `works`). Verificado con build antes/después: HTML generado idéntico, único diff es `lastmod` del sitemap por fecha.

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
7. **Home es scroll de secciones (`/#statement`, `/#bio`, `/#contact`) por diseño de Lucas, pero cada sección también existe como página independiente para SEO** (`/statement/`, `/bio/`, `/contact/`) — decisión de producto, no un descuido a "simplificar" fusionando en una sola página. **El contenido de esas 3 secciones (statement, bio, contact) se define una sola vez y se consume desde ambos lados** — ver "Partials compartidos" abajo. `work` es la única sección de home con contraparte independiente que **no** comparte partial a propósito: el home muestra un preview curado (grid sin excerpt ni contador) y `/work/` muestra el catálogo completo (con excerpt de statement y contador de obras) — son vistas distintas por diseño, no data duplicada.

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

## CMS para Lucas: Sveltia (2026-09-09, en implementación)

Objetivo: Lucas edita texto (statement/bio/contacto) y series/obras, incluyendo subir fotos nuevas, sin tocar código ni JSON a mano, y sin depender de Luis para cada cambio chico.

**Por qué Sveltia y no otra cosa**: git-based (sin backend/DB propio), fork moderno de Decap CMS compatible con su formato de `config.yml`, encaja directo con el modelo de datos actual (`data/*.json`). Ya estaba evaluado antes de hoy (ver commits previos), y el prerequisito que lo bloqueaba (mover el build a CI de Pages) ya está resuelto del lado de código desde el 2026-09-04 — solo falta confirmar que el dashboard de Cloudflare Pages esté configurado (ver sección de arriba).

**Hecho (Claude, 2026-09-09)**:
- `data/series.json` y `data/works.json` envueltos en `{"series": [...]}` / `{"works": [...]}` (ver nota arriba) — requerido por el formato de "file collections" del CMS.
- `admin/index.html` + `admin/config.yml`: define 3 colecciones — `site` (statement/bio/contacto, con los campos técnicos de `site.json` como `title`/`url`/`colors`/`language` ocultos para que el CMS no los borre al guardar), `series` y `works` (listas editables, con `id`/`order` marcados con hint de "no cambiar en algo ya publicado").
- `publish_mode: editorial_workflow` — cada guardado de Lucas abre un PR en vez de commitear directo a `main`, así Luis sigue siendo el gatekeeper editorial (rol que ya tenía) revisando el preview automático de Cloudflare Pages antes de mergear.
- Imágenes: `media_library` configurado como `cloudinary` (cloud `dt2w4nxz6`) para que Lucas pueda subir fotos nuevas directo desde el panel, en vez de pegar URLs a mano.

**Hecho 2026-09-09 (Luis + Claude)**:
- OAuth App creada en GitHub para `thx1131/gclucas-portafolio`.
- Worker `sveltia-cms-auth` (clon del proyecto open source oficial, sin modificar) desplegado en la cuenta de Cloudflare de Luis: `https://sveltia-cms-auth.thx1131.workers.dev`. El código fuente vive solo en `sveltia/sveltia-cms-auth` en GitHub — no se vendorizó dentro de este repo, es infraestructura aparte del sitio estático. Para volver a desplegar o actualizar: clonar ese repo y correr `wrangler deploy` logueado con la cuenta de Luis.
- Secrets del Worker configurados vía `wrangler secret put` (nunca escritos a un archivo): `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `ALLOWED_DOMAINS=gclucas.art`.
- `admin/config.yml`: `base_url` actualizado con la URL real del Worker.

**Pendiente, fuera del repo (requiere acceso a las cuentas de Luis, no lo puede hacer Claude)**:
1. Confirmar/crear en el dashboard de Cloudflare Pages el build command (ver sección de arriba) — si no está hecho, un commit del CMS actualiza el JSON pero el HTML publicado no se regenera solo.
2. ~~Verificar que el callback URL de la OAuth App en GitHub sea exactamente `https://sveltia-cms-auth.thx1131.workers.dev/callback`~~ — confirmado por Luis 2026-09-09.
3. Reemplazar en `admin/config.yml` el `api_key` de Cloudinary (no es secreto, se copia del dashboard de Cloudinary).
4. Crear un upload preset "unsigned" en Cloudinary (Settings → Upload → Add upload preset) para que el widget de subida del CMS funcione sin backend propio.
5. Primera prueba real: Lucas sube una foto nueva desde `/admin/` → verificar que la URL que devuelve el widget de Cloudinary sirva con `f_auto,q_auto` igual que las URLs existentes en `data/works.json` (`obras/ID`). Si no, ajustar la config del media_library o el preset en Cloudinary.

**No decidido todavía**: si el flujo de `Hoja de proyecto-cotejo.xlsx` (cotejo/QA editorial, no es fuente de contenido) sigue vigente una vez que Lucas edita directo por CMS, o si conviene reemplazarlo por revisar los PRs del CMS.

## Arquitectura: partials compartidos entre home-scroll y páginas independientes (2026-09-07)

**Problema que resolvió esto**: `templates/home.html` (secciones `#statement`, `#bio`, `#contact`) y sus páginas independientes (`templates/statement.html`, `bio.html`, `contact.html`) tenían el contenido **copiado a mano dos veces**. En la práctica esto causó que el rediseño de tarjetas de contacto (sesión 2026-09-06) se aplicara solo a `templates/contact.html` y `contact/index.html`, mientras que la sección `#contact` del home seguía con el markup viejo (`.contact-links`, "email · whatsapp · instagram" en línea) — el bug reportado por Luis de "no se ve el cambio" en realidad sí estaba aplicado, solo que en la mitad de los lugares donde vivía ese contenido. Al mismo tiempo se encontró que `statement` y `bio` ya habían divergido silenciosamente: el home tenía una oración extra en `statement` y un segundo párrafo extra en `bio` que **no existían** en `data/site.json` (nadie los había puesto ahí cuando se hardcodeó el home originalmente).

**Por qué no es Jinja de verdad**: `build_site_v2.py` no usa un motor de templates real — `_render_template()` es un `.replace("{{var}}", valor)` sobre strings planos (ver método, línea ~88). Meter Jinja habría significado reescribir el generador entero. Se usa la misma idea (un placeholder que se rellena una vez) pero con lo que ya existe.

**Solución — partial file + variable compartida construida una sola vez en el builder**:
1. `templates/partials/statement-content.html`, `bio-content.html`, `contact-content.html` — cada uno contiene **solo el bloque de valor** (el `<div class="statement-content">`, `.bio-content`, o `.contact-cards` con sus `{{placeholders}}` de datos), sin el `<h1>`/`<h2>` ni el `<section>` que envuelve — eso sigue viviendo en cada template porque sí difiere legítimamente entre home (`<h2>`, `.section`) y standalone (`<h1>`, `.{seccion}-page`).
2. En `SiteBuilder.__init__` (`build_site_v2.py`), después de cargar `site_data`, se renderizan una sola vez: `self.statement_content_html`, `self.bio_content_html`, `self.contact_content_html` — strings ya resueltos contra `data/site.json`.
3. `build_home()`, `build_statement()`, `build_bio()` y `build_contact()` inyectan **el mismo string** vía `{{statement_content}}` / `{{bio_content}}` / `{{contact_content}}` en su template respectivo. No hay dos copias del HTML en ningún lado — hay dos lugares que lo consumen.
4. **`data/site.json`**: `statementEn`, `statementEs`, `bioEn`, `bioEs` pasaron de string único a **array de párrafos** (`["párrafo 1", "párrafo 2", ...]`), porque el home ya mostraba 2 párrafos en `statement` y `bio` que el JSON no tenía — se migró ese texto extra al JSON en vez de perderlo, y el builder ahora hace `"".join(f"<p>{p}</p>" for p in ...)`. `statementEs`/`bioEs` quedaron como array de 1 elemento (no se les agregó el párrafo extra en inglés porque no existía traducción — y de todos modos **son campos muertos**, `build_site_v2.py` nunca los lee; el sitio es solo-inglés, principio 5).
5. `exhibitions` (bloque debajo de `.bio-content` en `/bio/`) **no** se partializó — solo vive en `templates/bio.html`, porque el home nunca lo mostró y no hay divergencia que resolver ahí.
6. `work` (home preview vs `/work/` catálogo completo) **se revisó y se dejó fuera a propósito** — no es contenido duplicado, son dos vistas distintas del mismo dato por diseño (ver principio 7 de Arquitectura).

**Regla para la próxima sección que se edite**: si el contenido vive tanto en `home.html` como en una página independiente, el fix va en el partial (`templates/partials/`) y/o en la variable compartida del builder — nunca en el HTML de un solo lado. Antes de dar un cambio de contenido por terminado, verificar que `grep` del texto viejo no aparezca en **ninguno** de los dos HTML generados (home Y standalone), no solo en el que se pidió cambiar.

**Verificado 2026-09-07**: build corrido con `python3 build/build_site_v2.py`; comparación programática (regex + comparación de strings) confirma que `.statement-content`, `.bio-content` y `.contact-cards` son **idénticos byte a byte** entre `index.html` y `statement/index.html` / `bio/index.html` / `contact/index.html`. Footer solo-copyright en `/contact/` intacto (no se tocó esa lógica). `.bio-cv`/exhibitions sigue solo en `/bio/` standalone.

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
6. ~~`templates/home.html` tiene bio parcialmente hardcodeada fuera de `data/site.json`~~ — **resuelto 2026-09-07** junto con el rediseño de partials compartidos (ver sección de Arquitectura arriba): `bioEn` en `data/site.json` ahora es un array con ambos párrafos, y `home.html`/`bio.html` consumen el mismo `bio_content` renderizado una sola vez.
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
- **Mismo bug de color, pendiente en el footer** (reportado por Luis en una cuarta pasada, el fix anterior solo cubrió `.contact-links` de `/contact/`, no `templates/components/footer.html`): `.footer-socials a` tampoco tenía `color` explícito, mismo patrón de fondo — dependía 100% de `a { color: inherit }` genérico. Resuelto igual que `.contact-links`: `color: var(--text-light)` / `body.dark-mode .footer-socials a { color: var(--text-dark) }` en `css/main.css` (se usó `--text-light`/`--text-dark`, no `--accent-*`, porque el computed color del footer ya era `rgb(51,51,51)` = `--text-light` antes del fix — es el mismo tono que el copyright, no hay tratamiento "secundario" separado en el diseño actual). Hover intacto vía `a:hover { opacity: 0.7 }` global.
- **Espacio muerto entre el bloque de contact-links y la línea del footer**: el `<p class="contact-links">` heredaba `margin-bottom: 16px` de la regla genérica `p { margin-bottom: var(--spacing-base) }`, dejando ese aire antes del `border-top` de `.footer`. Se agregó `.contact-links { margin-bottom: 0 }` — el gap medido bajó de 16px a 0px en la página `/contact/` (en la sección `#contact` de home el efecto es marginal porque ahí ya hay 80px de padding de `.section` antes del footer).

## Sesión 2026-09-05 (continuación): ajustes de diseño footer/galería/modal/navegador de series

- **Footer condicional en `/contact/`**: los links instagram/whatsapp/email del footer se ocultan solo en `/contact/` (que ya los muestra arriba, en `.contact-links`); el resto del sitio (home, work, series, bio) conserva el footer con los 3 links, sin cambios. Implementado sin hardcodear dos versiones del componente: `templates/components/footer.html` ahora tiene un placeholder `{{footer_socials}}` en vez del `<div class="footer-socials">` fijo; `build_site_v2.py` guarda ese bloque en `self.footer_socials_html` (construido una vez en `__init__`) y `_build_full_page()` recibió un parámetro nuevo `hide_footer_links=False` que decide si rellena `{{footer_socials}}` con ese HTML o con `""`. `build_contact()` es el único caller que pasa `hide_footer_links=True`.
- **Año quitado de la vista grid de la galería**: cada `.gallery-item` mostraba título + `<p>{{year}}</p>` debajo. Se quitó el `<p>` en `build_series_pages()` (`build_site_v2.py`) — el año sigue en `data/works.json`, solo no se renderiza ahí (sí sigue apareciendo en la ficha/modal individual, `#modalYear`).
- **Font-size del título en la ficha de galería (modal)**: `.modal-info h3` no tenía `font-size` propio, así que heredaba el tamaño grande de `h3` global, muy por encima de `.modal-info p` (dimensions/technique/year, 14px). Se agregó `font-size: 14px` explícito en `.modal-info h3` (`css/main.css`), conservando el `font-weight: 700` que ya tenía.
- **Navegador prev/next de series duplicado arriba de la galería**: ya existía uno al final de la página (`← serie anterior · work · serie siguiente →`). Se pidió el mismo navegador también al inicio. En vez de duplicar el HTML a mano, se extrajo la lógica a un método nuevo `_build_series_nav(prev_s, next_s)` en `build_site_v2.py` (antes vivía inline dentro de `build_series_pages()`); ahora se llama una sola vez por serie y el mismo string se pasa a dos placeholders del template: `{{series_nav_top}}` (nuevo, agregado en `templates/series.html` justo después de `.series-header`) y `{{series_nav}}` (el de siempre, al final, sin cambios de posición). Misma clase CSS (`.series-nav`) en ambos → layout y comportamiento idénticos arriba y abajo.
- Verificado corriendo `python3 build/build_site_v2.py` y revisando el HTML generado: `/contact/` sin `.footer-socials`, resto de páginas con los 3 links; `.gallery-item-info` solo con `<h4>`; `.series-nav` aparece 2 veces en cada página de serie.

## Sesión 2026-09-06: rediseño de `/contact/` a tarjetas (revierte ocultar datos crudos)

- **`.contact-links` (línea `email · whatsapp · instagram`) reemplazada por 2-3 tarjetas en fila**, pedido por Luis inspirándose en la *estructura* de contacto de otro proyecto de referencia (grid de tarjetas con label + valor) — explícitamente no su estilo visual; se mantuvo el lenguaje tipográfico de gclucas (sans-serif `--font-sans`, todo en minúsculas, sin small-caps ni serif importados). Cambios:
  - `templates/contact.html`: el `<p class="contact-links">` se reemplazó por `<div class="contact-cards">` con 3 `<a class="contact-card">`, cada una con `<span class="contact-card-label">` (etiqueta) + `<span class="contact-card-value">` (valor real).
  - `css/main.css`: nuevas clases `.contact-cards` (grid `repeat(auto-fit, minmax(220px, 1fr))`, gap 20px), `.contact-card` (borde 1px `--border-light`/`--border-dark`, padding 32px 24px, hover oscurece/aclara el borde a `--accent-light`/`--accent-dark`, transición `var(--transition)`), `.contact-card-label` (~12-13px, `--accent-light`/`--accent-dark`, letter-spacing sutil) y `.contact-card-value` (tamaño body normal, `--text-light`/`--text-dark`). `.contact-page .contact-content` subió su `max-width` a 900px (de los 600px genéricos) para que quepan las 3 tarjetas en fila.
  - Responsive: `.contact-cards` pasa a `grid-template-columns: 1fr` en el breakpoint existente `@media (max-width: 768px)`, mismo patrón que `.series-grid`/`.series-list`.
  - **Solo se tocó `/contact/`** (vía `templates/contact.html`, regenerado con `build_site_v2.py`). La sección `#contact` embebida en home (`templates/home.html`/`index.html`) comparte el bloque `.contact-content` pero sigue usando `.contact-links` (línea simple, sin tocar) — no se pidió cambiarla, y por eso el nuevo `.contact-cards`/`.contact-card` son clases nuevas, no una reescritura de `.contact-links`, para no heredar el layout de tarjetas ahí sin querer. ⚠️ **Superado 2026-09-07**: esto era exactamente la causa raíz del bug reportado por Luis (el fix vivía solo de un lado) — ver sesión siguiente, ahora `#contact` de home y `/contact/` comparten el mismo partial y muestran las mismas tarjetas.
  - **Revierte la decisión previa de ocultar los datos de contacto crudos**: el rediseño de la sesión 2026-09-05 (tercera pasada, ver arriba) mostraba solo las palabras genéricas "email · whatsapp · instagram" como texto de link, sin exponer la dirección/número/handle real. Ahora las tarjetas de `/contact/` muestran el valor real como texto visible — `email` → `gclucas999@gmail.com` completo, `instagram` → `@lucas.asecas`. Excepción: `whatsapp` sigue sin mostrar el número crudo, por pedido explícito de Luis — el valor visible es un CTA genérico ("send a message"), aunque el link ya apunta a `https://wa.me/524151511029` igual que antes.
  - Footer **no tocado**: sigue el comportamiento de la sesión anterior (footer completo en todo el sitio, solo copyright en `/contact/`, ver `hide_footer_links` arriba).
  - Verificado: `python3 build/build_site_v2.py` regenera `contact/index.html` con las 3 tarjetas y el footer solo-copyright intacto.

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

## Sesión 2026-09-07: elimina duplicación home-scroll / páginas independientes

Luis reportó que el fix de tarjetas de contacto de la sesión anterior "no se veía" — no era caché: el fix estaba pusheado y correcto en `/contact/`, pero la sección `#contact` del home nunca se tocó porque vive en un HTML aparte (`templates/home.html`) copiado a mano desde `templates/contact.html`. Aclarado por Luis: la duplicación scroll-home / página-independiente **es intencional** (pedido de Lucas: sitio de una sola página con scroll, pero cada sección indexable por separado para SEO) — el bug no es la duplicación en sí, sino que un lado se actualizaba y el otro no.

- Ver sección nueva **"Arquitectura: partials compartidos..."** arriba (justo después de la migración a Cloudflare CI) para el detalle completo de la solución.
- Resumen: `templates/partials/{statement,bio,contact}-content.html` + 3 strings renderizados una vez en `SiteBuilder.__init__` (`build_site_v2.py`) e inyectados vía el mismo placeholder en `home.html` y en la página independiente correspondiente.
- De paso se corrigieron dos divergencias que ya existían antes de esta sesión (encontradas al comparar ambos lados): el home tenía una oración de `statement` y un párrafo de `bio` que nunca estaban en `data/site.json` — se migraron al JSON (ahora arrays de párrafos) en vez de perderse.
- `work` (preview en home vs catálogo en `/work/`) se revisó y quedó **fuera** de este refactor a propósito — no es texto duplicado, son dos vistas distintas del mismo dato por diseño.

## Backlog técnico scoped, no construido

- `actualizar.sh` — script que encadene el pipeline restante (build → push) para cambios locales
- Script de ruteo de extracción de imágenes desde PowerPoint (discutido, no escrito)
- Sección `/text/` — oculta hasta que exista contenido literario real

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
