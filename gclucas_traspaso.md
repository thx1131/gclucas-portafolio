# CLAUDE.md — gclucas-portafolio

Contexto para Claude Code. Leer completo antes de tocar código. Actualizado: 2026-09-04.

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
Google Sheets (fuente EDITORIAL)
  → export Excel
  → excel_to_json.py
  → data/series.json + data/works.json (fuente TÉCNICA)
  → build/build_site_v2.py
  → HTML estático pre-generado (SEO: meta/OG únicos por página)
  → git push → Cloudflare Pages
```

Principios fijos:
1. **HTML pre-generado**, nunca renderizado client-side. Vanilla HTML/CSS/JS, cero frameworks.
2. **URLs limpias**: `/work/pixelogue/` (carpeta + index.html), nunca `.html` visible.
3. **IDs inmutables**: formato 3 letras + 3 dígitos (`PEL001`). Jamás cambian, aunque la serie se renombre.
4. **Disciplina de fuente única**: todo cambio editorial entra por Google Sheets → JSON. NUNCA parchear JSON o HTML generado a mano.
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
- `excel_to_json.py` — inventario + URLs → `series.json` y `works.json`

Regla: editaste `data/` o `templates/` → regenera antes de push. Solo `css/` o `js/` → push directo.

## Gotchas (aprendidos a golpes)

- **IDs numéricos del Excel llegan como float** → castear a `int` antes de str. Ya manejado en `extract_pptx_v2.py` y `cloudinary_sync.py`; recordarlo en scripts nuevos.
- **SSL de Cloudflare debe quedarse en "Full"** (no Flexible, no Full Strict). Cambiar esto rompió el sitio antes (Error 522).
- **Git remote lleva el usuario embebido** (`thx1131@github.com`) para evitar credenciales cacheadas de otra cuenta (`sistemaskmmp`). No "limpiar" la URL.
- **Deploy que no actualiza**: revisar en el diff del commit que los archivos VIEJOS realmente se reemplazaron (no solo que se agregaron nuevos). Ya pasó: se copiaron carpetas nuevas pero index/css/js quedaron viejos.
- **Caché**: si GitHub está bien pero gclucas.art se ve viejo → Cloudflare → Caching → Purge Everything.
- **Conflicto de la serie Filippo** se resolvió con fingerprinting de imágenes a nivel de pixel; si reaparece ambigüedad serie/numeración, usar ese método.
- "Uploaded 0 files" en el deploy = el commit no cambió nada realmente; revisar `git status` antes de asumir bug de Cloudflare.

## Bugs abiertos (backlog corto)

> Verificado por Claude 2026-09-04 contra el estado real del repo (ver "Verificación Claude" abajo). Los ítems 4 y 5 de la versión anterior de esta lista ya estaban resueltos y se quitaron.

1. **Dark mode arranca según preferencia del sistema; debe defaultear a light.** (js/darkmode.js) — confirmado: `getInitialTheme()` cae a `prefersDark ? 'dark' : 'light'`, y el listener de `matchMedia('(prefers-color-scheme: dark)')` reaplica ese fallback si el usuario cambia el tema del SO. Fix: hardcodear el fallback a `'light'` (y evaluar si el listener de cambios de sistema debe seguir existiendo).
2. **Bio tiene lorem ipsum** — esperando texto de Lucas. Confirmado en `data/site.json` (`bioEn`/`bioEs`) y en `bio/index.html` generado. Además `templates/home.html` tiene un **segundo párrafo de lorem ipsum hardcodeado directo en el template** (el de "Duis aute irure...") que no viene de `data/site.json` — ver punto 8 más abajo, es un problema aparte de disciplina de fuente única.
3. **SUE006 aparece "pendiente"** (sin imagen) en la serie visión de filippo — confirmado, `cloudinaryUrl: ""` en `data/works.json`. Reservado para imágenes que Lucas enviará.
4. **Carpeta huérfana `{build,templates` en la raíz del repo.** Contiene una subcarpeta literal `components,data,css,js,work,images}` — restos de un `mkdir {build,templates,...}` corrido en un shell sin expansión de llaves. No está trackeada en git (no aparece en `git status` ni `git ls-files`), así que es basura local segura de borrar: `rm -rf "{build,templates"`.
5. ~~`work/nude-revisited/` es output huérfano~~ — **resuelto 2026-09-04**, carpeta borrada (junto con `{build,templates`). Confirmó que "reviseted" no es un bug de build sino que **vive en el Google Sheet / `data/works.json`+`series.json`**; la decisión de naming sigue pendiente de Lucas (ver backlog de abajo).
6. **`templates/home.html` tiene bio parcialmente hardcodeada fuera de `data/site.json`.** El párrafo "Duis aute irure..." está escrito directo en el template y no sale del JSON — viola el principio 4 de Arquitectura (fuente única). Cuando llegue el texto real de Lucas, hay que asegurarse de que **ambos** párrafos salgan de `site.json`, no solo uno.

## Backlog esperando input de Lucas (no bloquear trabajo técnico por esto)

- ~~Traducciones EN + técnicas/materiales estandarizados en inglés~~ — **hecho 2026-09-04**: `statementEn` de las 21 series con texto (las 3 vacías —trompe-l-oeil, h2o, naranja-dulce— siguen esperando statement) y el campo `technique` de `works.json` traducidos a inglés profesional. Los títulos en español (series y obras) se respetaron sin traducir, por instrucción explícita. **⚠️ Se parchó `data/series.json` y `data/works.json` a mano, saltándose el flujo Sheets → JSON del punto 4 de Arquitectura** — la próxima vez que se exporte el Google Sheet, esta traducción se pierde si el Sheet no se actualiza también. Pendiente: volcar estas traducciones al Sheet fuente para que no se sobrescriban.
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
