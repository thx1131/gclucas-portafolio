#!/usr/bin/env python3
"""
Atelier: Artist Portfolio Engine v2.0
build_site.py - Generate static multipágina HTML from JSON data

Genera todas las páginas:
/ (home)
/statement
/work (lista de series)
/work/[series-id] (serie individual)
/text (lista de textos)
/text/[text-id] (texto individual)
/bio
/contact

Cada página se genera una vez por idioma (ver LANGS): el idioma default
(site.json → "language") vive en la raíz y el otro bajo su prefijo (/es/...).
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, date

# Idiomas del sitio. El default (site.json → "language") se publica en la raíz (/work/...)
# y el resto bajo su código (/es/work/...). Cambiar el default es cambiar ese campo.
LANGS = ('en', 'es')

# Textos de interfaz por idioma. Cada clave entra a los templates como {{t_<clave>}}.
# El contenido (títulos, statements, técnicas) NO va acá: sale de data/*.json (campos ...En / ...Es).
UI = {
    'en': {
        'og_locale': 'en_US',
        'nav_statement': 'statement',
        'nav_work': 'work',
        'nav_bio': 'bio',
        'nav_contact': 'contact',
        'theme_toggle': 'Toggle dark mode',
        'lang_switch': 'Ver en español',
        'hero_alt': 'gclucas — visual artist',
        'hero_tagline': 'visual artist exploring contradictions & transitions',
        'explore_series': 'explore the series',
        'exhibitions': 'exhibitions',
        'texts': 'texts',
        'texts_subtitle': 'writings and reflections',
        'read_more': 'read more',
        'send_message': 'send a message',
        'modal_close': 'close',
        'modal_prev': '← previous',
        'modal_next': 'next →',
        'works_count': 'works',
        'variable_dimensions': 'variable dimensions',
        'title_home': 'gclucas | visual artist',
        'desc_statement': "Artist's statement",
        'desc_work': 'Explore the series',
        'desc_texts': 'Writings and reflections',
        'desc_bio': 'Artist biography and exhibitions',
        'desc_contact': 'Get in touch',
    },
    'es': {
        'og_locale': 'es_MX',
        'nav_statement': 'statement',
        'nav_work': 'obra',
        'nav_bio': 'bio',
        'nav_contact': 'contacto',
        'theme_toggle': 'Cambiar a modo oscuro',
        'lang_switch': 'View in English',
        'hero_alt': 'gclucas — artista visual',
        'hero_tagline': 'artista visual que explora contradicciones y transiciones',
        'explore_series': 'explora las series',
        'exhibitions': 'exposiciones',
        'texts': 'textos',
        'texts_subtitle': 'escritos y reflexiones',
        'read_more': 'leer más',
        'send_message': 'enviar un mensaje',
        'modal_close': 'cerrar',
        'modal_prev': '← anterior',
        'modal_next': 'siguiente →',
        'works_count': 'obras',
        'variable_dimensions': 'dimensiones variables',
        'title_home': 'gclucas | artista visual',
        'desc_statement': 'Statement del artista',
        'desc_work': 'Explora las series',
        'desc_texts': 'Escritos y reflexiones',
        'desc_bio': 'Biografía y exposiciones del artista',
        'desc_contact': 'Ponte en contacto',
    },
}

# Muchas obras traen techniqueEs todavía en inglés ("oil/canvas", "acrilic/canvas").
# En vez de reescribir ~150 archivos de data/works/, la versión en español traduce
# esos términos al renderizar; un techniqueEs ya en español pasa sin cambios.
TECHNIQUE_ES = [
    (r'\boil\b', 'óleo'),
    (r'\bacr[yi]lic\b', 'acrílico'),
    (r'\bcanvas\b', 'tela'),
    (r'\bgraphite\b', 'grafito'),
    (r'\bpaper\b', 'papel'),
    (r'\bphotography\b', 'fotografía'),
    (r'\bspray\b', 'aerosol'),
]

class SiteBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.templates_dir = self.base_dir / 'templates'
        self.output_dir = self.base_dir
        
        # Load data
        self.series_data = self._load_series_folder()
        self.works_data = self._load_works_folder()
        self.site_data = self._load_json('site.json')
        
        # Templates crudos (con los {{t_...}} / {{base}} sin resolver). _set_language()
        # los localiza y los deja como atributos (self.base_template, self.home_template, ...).
        self._raw_templates = {
            'base_template': self._load_template('base.html'),
            'home_template': self._load_template('home.html'),
            'statement_template': self._load_template('statement.html'),
            'work_template': self._load_template('work.html'),
            'series_template': self._load_template('series.html'),
            'text_template': self._load_template('text.html'),
            # opcional: aún no se renderiza ninguna página con este template (ver backlog /text/)
            'text_detail_template': self._load_template('text-detail.html', optional=True),
            'bio_template': self._load_template('bio.html'),
            'contact_template': self._load_template('contact.html'),

            # Partials: contenido compartido entre el home-scroll (#statement/#bio/#contact)
            # y su página independiente (/statement/, /bio/, /contact/) — una sola fuente,
            # renderizada una vez por idioma en _set_language() y reusada en build_home()
            # y en cada build_*() de abajo.
            # Ver "Arquitectura: partials compartidos" en gclucas_traspaso.md.
            'statement_content_partial': self._load_template('partials/statement-content.html'),
            'bio_content_partial': self._load_template('partials/bio-content.html'),
            'contact_content_partial': self._load_template('partials/contact-content.html'),

            # Components
            'navbar_component': self._load_template('components/navbar.html'),
            'footer_component': self._load_template('components/footer.html'),
        }

        self.default_lang = self.site_data.get('language', 'en')
        if self.default_lang not in LANGS:
            sys.exit(f"❌ Error fatal: site.json language='{self.default_lang}' no está en LANGS {LANGS}")

        # Socials del footer: se ocultan solo en /contact/, que ya los muestra arriba
        self.footer_socials_html = (
            '<div class="footer-socials">\n'
            '            <a href="https://instagram.com/lucas.asecas" target="_blank" rel="noopener noreferrer">instagram</a>\n'
            '            <a href="https://wa.me/524151511029" target="_blank" rel="noopener noreferrer">whatsapp</a>\n'
            '            <a href="mailto:gclucas999@gmail.com">email</a>\n'
            '        </div>'
        )

        # Imagen real usada como og:image genérico (home, statement, work, bio, contact).
        # Las páginas de serie individual usan su propio coverImage, no esto.
        self.default_og_image = self.site_data.get('heroImage',
            'https://res.cloudinary.com/dt2w4nxz6/image/upload/f_auto,q_auto/obras/PEL004')

        self._set_language(self.default_lang)

    def _lang_prefix(self, lang):
        """Prefijo de URL de un idioma: '' para el default (raíz), '/es' para el otro."""
        return '' if lang == self.default_lang else f'/{lang}'

    def _set_language(self, lang):
        """Deja el builder listo para generar las páginas de `lang`: prefijo de URL,
        carpeta de salida, textos de interfaz y templates/partials ya localizados."""
        self.lang = lang
        self.prefix = self._lang_prefix(lang)
        self.lang_output_dir = self.output_dir / lang if self.prefix else self.output_dir
        self.t = UI[lang]

        ui_vars = {f't_{key}': value for key, value in self.t.items()}
        ui_vars['base'] = self.prefix
        ui_vars['lang'] = lang
        for name, raw in self._raw_templates.items():
            setattr(self, name, self._render_template(raw, ui_vars))

        # Contenido de cada partial, renderizado una sola vez por idioma contra site_data.
        # El mismo string se inyecta tal cual en home.html y en la página independiente.
        self.statement_content_html = self._render_template(self.statement_content_partial, {
            'statement_text': "".join(f"<p>{p}</p>" for p in self._loc(self.site_data, 'statement'))
        })
        self.bio_content_html = self._render_template(self.bio_content_partial, {
            'bio_text': "".join(f"<p>{p}</p>" for p in self._loc(self.site_data, 'bio'))
        })
        self.contact_content_html = self._render_template(self.contact_content_partial, {
            'email': self.site_data['email'],
            'whatsapp_number': self.site_data['whatsapp_number'],
            'instagram': self.site_data['instagram']
        })

    def _loc(self, obj, field):
        """Campo de contenido en el idioma actual (titleEn/titleEs, statementEn/statementEs, ...).
        Si falta o está vacío en español, cae al inglés para no publicar un hueco."""
        return obj.get(f'{field}{self.lang.capitalize()}') or obj.get(f'{field}En') or ''

    def _series_years(self, series):
        """Año de una serie como texto: "2008", o "2006–2008" si trae yearEnd
        (opcional: año final de una serie hecha a lo largo de varios años)."""
        year, year_end = series['year'], series.get('yearEnd')
        if year_end and year_end != year:
            return f"{year}–{year_end}"
        return str(year)

    def _technique(self, work):
        """Técnica de una obra en el idioma actual. El inglés vive en 'technique' (sin sufijo)
        y el español en 'techniqueEs', que se normaliza con TECHNIQUE_ES."""
        if self.lang != 'es':
            return work.get('technique') or ''
        text = work.get('techniqueEs') or work.get('technique') or ''
        for pattern, replacement in TECHNIQUE_ES:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        text = re.sub(r'\s*,\s*', ', ', text)
        return re.sub(r'\s*/\s*', '/', text).strip()

    def _url(self, path, lang=None):
        """URL absoluta de `path` ('/work/saga/') en `lang` (default: el idioma actual)."""
        lang = lang or self.lang
        return f"{self.site_data['url'].rstrip('/')}{self._lang_prefix(lang)}{path}"

    def _optimized_image_url(self, url):
        """Inserta f_auto,q_auto en una URL de Cloudinary si no la trae ya.
        Necesario porque el widget de subida del CMS (admin/) devuelve la URL
        cruda del media_library, sin esa transformación, a diferencia de las
        URLs de la pipeline original (obras-extraccion) que ya la traen fija."""
        marker = '/image/upload/'
        if marker not in url:
            return url
        rest = url.split(marker, 1)[1]
        if 'f_auto' in rest.split('/', 1)[0]:
            return url
        return url.replace(marker, f'{marker}f_auto,q_auto/', 1)

    def _load_json(self, filename):
        """Load JSON file from data directory. Siempre requerido: aborta el build si falta o es inválido."""
        path = self.data_dir / filename
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            sys.exit(f"❌ Error fatal: {filename} not found at {path}")
        except json.JSONDecodeError as e:
            sys.exit(f"❌ Error fatal: {filename} tiene JSON inválido ({e})")

    def _load_works_folder(self):
        """Carga data/works/ (folder collection del CMS: un archivo JSON por obra).
        El orden de lectura del filesystem no es curatorial (alfabético por id),
        a diferencia del viejo works.json de array único — ver _get_works_by_series,
        que ordena explícitamente por el campo 'order' de cada obra."""
        folder = self.data_dir / 'works'
        if not folder.is_dir():
            sys.exit(f"❌ Error fatal: {folder} not found")
        works = []
        for path in sorted(folder.glob('*.json')):
            with open(path, 'r', encoding='utf-8') as f:
                works.append(json.load(f))
        return works

    def _load_series_folder(self):
        """Carga data/series/ (folder collection del CMS: un archivo JSON por serie).
        A diferencia de works, el orden de self.series_data importa en todo el builder
        (navegación prev/next entre series, sitemap, etc.), así que se ordena acá mismo
        por el campo 'order' de cada serie — el orden de lectura del filesystem
        (alfabético por id) ya no es curatorial como lo era el viejo series.json."""
        folder = self.data_dir / 'series'
        if not folder.is_dir():
            sys.exit(f"❌ Error fatal: {folder} not found")
        series = []
        for path in sorted(folder.glob('*.json')):
            with open(path, 'r', encoding='utf-8') as f:
                series.append(json.load(f))
        series.sort(key=lambda s: s.get('order') if s.get('order') is not None else 0)
        return series

    def _load_template(self, filename, optional=False):
        """Load template file from templates directory.
        optional=True: falta tolerada (ningún page builder lo usa todavía), devuelve "" y solo avisa."""
        path = self.templates_dir / filename
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            if optional:
                print(f"⚠️  Aviso: {filename} not found at {path} (opcional, no bloquea el build)")
                return ""
            sys.exit(f"❌ Error fatal: {filename} not found at {path}")
    
    def _render_template(self, template, variables):
        """Replace variables in template"""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def _get_series_by_id(self, series_id):
        """Get series data by ID"""
        for series in self.series_data:
            if series['id'] == series_id:
                return series
        return None
    
    def _get_works_by_series(self, series_id):
        """Get all works for a series, ordered by el campo 'order' de cada obra
        (ya no por posición física en el archivo, ver _load_works_folder)."""
        works = [w for w in self.works_data if w['series'] == series_id]
        return sorted(works, key=lambda w: w.get('order') if w.get('order') is not None else 0)

    def _build_series_nav(self, prev_s, next_s):
        """HTML del navegador prev/next entre series. Se reusa arriba y abajo de la galería."""
        nav = '<div class="series-nav">'
        nav += f'<a href="{self.prefix}/work/{prev_s["id"]}/">← {self._loc(prev_s, "title")}</a>' if prev_s else '<span></span>'
        nav += f'<a href="{self.prefix}/work/">{self.t["nav_work"]}</a>'
        nav += f'<a href="{self.prefix}/work/{next_s["id"]}/">{self._loc(next_s, "title")} →</a>' if next_s else '<span></span>'
        nav += '</div>'
        return nav

    def _format_dimensions(self, dims):
        """Formatea dimensions en sus variantes: normal, 3D, variables, raw, vacío.
        El formulario de Obras en el CMS guarda las 6 subclaves siempre (height/width/
        unit/depth/variable/raw), vacías o null si no aplican — a diferencia de las 144
        obras originales, que solo tienen las claves que usan. Por eso todo acá chequea
        contenido real (valores truthy / is not None), nunca solo si la clave existe."""
        if not dims:
            return ""
        if dims.get('variable'):
            return self.t['variable_dimensions']
        if dims.get('raw'):
            return dims['raw']
        if not dims.get('height') or not dims.get('width'):
            return ""
        parts = [str(dims['height']), str(dims['width'])]
        if dims.get('depth') is not None:
            parts.append(str(dims['depth']))
        return "×".join(parts) + f" {dims.get('unit') or 'cm'}"
    
    def _truncate(self, text, length=100):
        """Corta texto a `length` caracteres sin partir una palabra a la mitad"""
        if len(text) <= length:
            return text
        return text[:length].rsplit(' ', 1)[0] + "..."

    def _save_html(self, path, content):
        """Save HTML file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _build_full_page(self, content, title, description, og_image, path, noindex=False, hide_footer_links=False):
        """Wraps content with base template, navbar, footer, SEO.
        path: ruta de la página sin prefijo de idioma ('/', '/work/saga/'); de ahí salen
        canonical, og:url, los hreflang y el link del selector de idioma.
        hide_footer_links=True: oculta instagram/whatsapp/email del footer (usado en /contact/, que ya los muestra arriba)."""
        robots_meta = (
            '<meta name="robots" content="noindex, nofollow">' if noindex else ''
        )
        page_url = self._url(path)
        alt_lang = next(l for l in LANGS if l != self.lang)
        # hreflang: le dice a Google que /x/ y /es/x/ son la misma página en otro idioma
        alternates = '' if noindex else "\n    ".join(
            [f'<link rel="alternate" hreflang="{l}" href="{self._url(path, l)}">' for l in LANGS]
            + [f'<link rel="alternate" hreflang="x-default" href="{self._url(path, self.default_lang)}">']
        )
        navbar_html = self._render_template(self.navbar_component, {
            'alt_lang': alt_lang,
            'alt_url': f"{self._lang_prefix(alt_lang)}{path}"
        })
        footer_html = self._render_template(self.footer_component, {
            'footer_socials': '' if hide_footer_links else self.footer_socials_html
        })
        full_content = self._render_template(self.base_template, {
            'title': title,
            'description': description,
            'og_image': og_image,
            'og_url': page_url,
            'canonical_url': page_url,
            'alternates': alternates,
            'robots_meta': robots_meta,
            'navbar': navbar_html,
            'content': content,
            'footer': footer_html
        })
        return full_content
    
    # PAGE BUILDERS
    
    def build_home(self):
        """Build / (index.html)"""
        print("🏠 Building home page...")
        
        series_preview = ""
        for series in self.series_data:
            series_preview += f"""
            <a href="{self.prefix}/work/{series['id']}/" class="series-card">
                <img src="{self._optimized_image_url(series['coverImage'])}" alt="{self._loc(series, 'title')}" loading="lazy">
                <h3>{self._loc(series, 'title')}</h3>
                <div class="year">{self._series_years(series)}</div>
            </a>
            """
        
        content = self._render_template(self.home_template, {
            'series_preview': series_preview,
            'hero_image': self.site_data.get('heroImage',
                'https://res.cloudinary.com/dt2w4nxz6/image/upload/f_auto,q_auto/obras/PEL004'),
            'statement_content': self.statement_content_html,
            'bio_content': self.bio_content_html,
            'contact_content': self.contact_content_html
        })
        
        html = self._build_full_page(
            content,
            self.t['title_home'],
            self._loc(self.site_data, 'description'),
            self.default_og_image,
            '/'
        )
        
        output_path = self.lang_output_dir / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_statement(self):
        """Build /statement/index.html"""
        print("📝 Building statement page...")
        
        content = self._render_template(self.statement_template, {
            'statement_content': self.statement_content_html
        })
        
        html = self._build_full_page(
            content,
            f"{self.t['nav_statement']} | gclucas",
            self.t['desc_statement'],
            self.default_og_image,
            '/statement/'
        )
        
        output_path = self.lang_output_dir / 'statement' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_work_index(self):
        """Build /work/index.html"""
        print("📂 Building work index...")
        
        series_list = ""
        for series in self.series_data:
            works_count = len(self._get_works_by_series(series['id']))
            statement = self._loc(series, 'statement')
            excerpt = f"<p>{self._truncate(statement)}</p>" if statement else ""
            series_list += f"""
            <a href="{self.prefix}/work/{series['id']}/" class="series-card">
                <img src="{self._optimized_image_url(series['coverImage'])}" alt="{self._loc(series, 'title')}" loading="lazy">
                <h3>{self._loc(series, 'title')}</h3>
                {excerpt}
                <div class="year">{self._series_years(series)} • {works_count} {self.t['works_count']}</div>
            </a>
            """
        
        content = self._render_template(self.work_template, {
            'series_list': series_list
        })
        
        html = self._build_full_page(
            content,
            f"{self.t['nav_work']} | gclucas",
            self.t['desc_work'],
            self.default_og_image,
            '/work/'
        )
        
        output_path = self.lang_output_dir / 'work' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_series_pages(self):
        """Build /work/[series-id]/index.html for each series"""
        print("🎨 Building series pages...")

        for i, series in enumerate(self.series_data):
            series_id = series['id']
            works = self._get_works_by_series(series_id)

            gallery_html = ""
            for work in works:
                dimensions = self._format_dimensions(work['dimensions'])
                gallery_html += f"""
                <div class="gallery-item" data-technique="{self._technique(work)}" data-dimensions="{dimensions}" data-year="{work['year']}">
                    <img src="{self._optimized_image_url(work['cloudinaryUrl'])}" alt="{self._loc(work, 'title')}" loading="lazy">
                    <div class="gallery-item-info">
                        <h4>{self._loc(work, 'title')}</h4>
                    </div>
                </div>
                """

            prev_s = self.series_data[i - 1] if i > 0 else None
            next_s = self.series_data[i + 1] if i < len(self.series_data) - 1 else None
            nav = self._build_series_nav(prev_s, next_s)

            statement = self._loc(series, 'statement')
            statement_html = f"<p>{statement}</p>" if statement else ""
            if series.get('statementAuthor'):
                statement_html += f'<p class="statement-author">— {series["statementAuthor"]}</p>'

            content = self._render_template(self.series_template, {
                'series_title': self._loc(series, 'title'),
                'series_year': self._series_years(series),
                'series_statement': statement_html,
                'series_nav_top': nav,
                'gallery': gallery_html,
                'series_nav': nav
            })

            html = self._build_full_page(
                content,
                f"{self._loc(series, 'title')} | gclucas",
                self._truncate(statement, 160),
                self._optimized_image_url(series['coverImage']),
                f"/work/{series_id}/"
            )

            output_path = self.lang_output_dir / 'work' / series_id / 'index.html'
            self._save_html(output_path, html)
            print(f"✅ Created: {output_path} ({len(works)} works)")
    
    def build_text_index(self):
        """Build /text/index.html"""
        print("📚 Building texts index...")
        
        texts_list = f"""
        <div class="texts-grid">
            <article class="text-card">
                <h3>Ficciones</h3>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                <a href="{self.prefix}/text/ficciones/">{self.t['read_more']}</a>
            </article>
            <article class="text-card">
                <h3>Sobre Peligro de Extinción</h3>
                <p>Exploración del concepto de extinción en la obra contemporánea.</p>
                <a href="{self.prefix}/text/peligro-extincion/">{self.t['read_more']}</a>
            </article>
        </div>
        """
        
        content = self._render_template(self.text_template, {
            'texts_list': texts_list
        })
        
        html = self._build_full_page(
            content,
            f"{self.t['texts']} | gclucas",
            self.t['desc_texts'],
            "https://picsum.photos/1200/600?random=texts",
            '/text/',
            noindex=True  # placeholder content (lorem ipsum, links a páginas inexistentes) — no indexar hasta que haya texto real
        )
        
        output_path = self.lang_output_dir / 'text' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_bio(self):
        """Build /bio/index.html"""
        print("👤 Building bio page...")
        
        exhibitions_html = ""
        for exhibition in self.site_data.get('exhibitions', []):
            exhibitions_html += f"""
            <div class="exhibition">
                <p><strong>{exhibition.get('year')}</strong> • {exhibition.get('title')}</p>
                <p>{exhibition.get('location')}</p>
            </div>
            """
        
        content = self._render_template(self.bio_template, {
            'bio_content': self.bio_content_html,
            'exhibitions': exhibitions_html
        })
        
        html = self._build_full_page(
            content,
            f"{self.t['nav_bio']} | gclucas",
            self.t['desc_bio'],
            self.default_og_image,
            '/bio/'
        )
        
        output_path = self.lang_output_dir / 'bio' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_contact(self):
        """Build /contact/index.html"""
        print("📞 Building contact page...")
        
        content = self._render_template(self.contact_template, {
            'contact_content': self.contact_content_html
        })
        
        html = self._build_full_page(
            content,
            f"{self.t['nav_contact']} | gclucas",
            self.t['desc_contact'],
            self.default_og_image,
            '/contact/',
            hide_footer_links=True
        )

        output_path = self.lang_output_dir / 'contact' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_sitemap(self):
        """Build /sitemap.xml — se regenera con las URLs reales en cada build"""
        print("🗺️  Building sitemap...")

        today = date.today().isoformat()
        # /text/ excluido a propósito: contenido placeholder, no indexable todavía (ver noindex en build_text_index)
        static_paths = ['/', '/statement/', '/work/', '/bio/', '/contact/']
        paths = static_paths + [f"/work/{s['id']}/" for s in self.series_data]

        # Una entrada por página y por idioma, cada una con sus alternates (hreflang)
        entries = []
        for p in paths:
            alternates = "".join(
                f'    <xhtml:link rel="alternate" hreflang="{l}" href="{self._url(p, l)}"/>\n'
                for l in LANGS
            )
            for lang in LANGS:
                entries.append(
                    f"  <url>\n    <loc>{self._url(p, lang)}</loc>\n{alternates}"
                    f"    <lastmod>{today}</lastmod>\n  </url>"
                )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(entries) + "\n"
            "</urlset>\n"
        )

        output_path = self.output_dir / 'sitemap.xml'
        output_path.write_text(xml, encoding='utf-8')
        print(f"✅ Created: {output_path} ({len(entries)} URLs)")
    
    def build(self):
        """Build entire site"""
        print("\n" + "="*60)
        print("🎨 ATELIER v2.0 - Multipágina SEO-Optimizado")
        print("="*60)
        print(f"⏰ Building at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for lang in LANGS:
            self._set_language(lang)
            print(f"\n🌐 Idioma: {lang} → {self.prefix or '/'}")
            self.build_home()
            self.build_statement()
            self.build_work_index()
            self.build_series_pages()
            self.build_text_index()
            self.build_bio()
            self.build_contact()
        self.build_sitemap()
        
        print("\n" + "="*60)
        print("✅ Multipágina site generation complete!")
        print("="*60)
        print(f"\nPáginas generadas (por idioma: {', '.join(LANGS)}):")
        print("  / (home)")
        print("  /statement")
        print("  /work (todas las series)")
        print("  /work/[series-id] (cada serie)")
        print("  /text (lista de textos)")
        print("  /bio")
        print("  /contact")
        print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    builder = SiteBuilder()
    builder.build()
