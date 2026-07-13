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
"""

import json
import os
from pathlib import Path
from datetime import datetime, date

class SiteBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.templates_dir = self.base_dir / 'templates'
        self.output_dir = self.base_dir
        
        # Load data
        self.series_data = self._load_json('series.json')
        self.works_data = self._load_json('works.json')
        self.site_data = self._load_json('site.json')
        
        # Load templates
        self.base_template = self._load_template('base.html')
        self.home_template = self._load_template('home.html')
        self.statement_template = self._load_template('statement.html')
        self.work_template = self._load_template('work.html')
        self.series_template = self._load_template('series.html')
        self.text_template = self._load_template('text.html')
        self.text_detail_template = self._load_template('text-detail.html')
        self.bio_template = self._load_template('bio.html')
        self.contact_template = self._load_template('contact.html')
        
        # Components
        self.navbar_component = self._load_template('components/navbar.html')
        self.footer_component = self._load_template('components/footer.html')
    
    def _load_json(self, filename):
        """Load JSON file from data directory"""
        path = self.data_dir / filename
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: {filename} not found at {path}")
            return []
    
    def _load_template(self, filename):
        """Load template file from templates directory"""
        path = self.templates_dir / filename
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Error: {filename} not found at {path}")
            return ""
    
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
        """Get all works for a series"""
        return [w for w in self.works_data if w['series'] == series_id]

    def _format_dimensions(self, dims):
        """Formatea dimensions en sus variantes: normal, 3D, variables, raw, vacío"""
        if not dims:
            return ""
        if dims.get('variable'):
            return "variable dimensions"
        if 'raw' in dims:
            return dims['raw']
        parts = [str(dims['height']), str(dims['width'])]
        if 'depth' in dims:
            parts.append(str(dims['depth']))
        return "×".join(parts) + f" {dims.get('unit', 'cm')}"
    
    def _save_html(self, path, content):
        """Save HTML file"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _build_full_page(self, content, title, description, og_image, og_url, canonical_url):
        """Wraps content with base template, navbar, footer, SEO"""
        full_content = self._render_template(self.base_template, {
            'title': title,
            'description': description,
            'og_image': og_image,
            'og_url': og_url,
            'canonical_url': canonical_url,
            'navbar': self.navbar_component,
            'content': content,
            'footer': self.footer_component
        })
        return full_content
    
    # PAGE BUILDERS
    
    def build_home(self):
        """Build / (index.html)"""
        print("🏠 Building home page...")
        
        series_preview = ""
        for series in self.series_data:
            series_preview += f"""
            <a href="/work/{series['id']}/" class="series-card">
                <img src="{series['coverImage']}" alt="{series['titleEn']}" loading="lazy">
                <h3>{series['titleEn']}</h3>
                <div class="year">{series['year']}</div>
            </a>
            """
        
        content = self._render_template(self.home_template, {
            'series_preview': series_preview,
            'hero_image': self.site_data.get('heroImage',
                'https://res.cloudinary.com/dt2w4nxz6/image/upload/f_auto,q_auto/obras/PEL004')
        })
        
        html = self._build_full_page(
            content,
            "gclucas | visual artist",
            self.site_data['descriptionEn'],
            "https://picsum.photos/1200/600?random=og",
            self.site_data['url'],
            self.site_data['url']
        )
        
        output_path = self.output_dir / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_statement(self):
        """Build /statement/index.html"""
        print("📝 Building statement page...")
        
        content = self._render_template(self.statement_template, {
            'statement_text': f"<p>{self.site_data['statementEn']}</p>"
        })
        
        html = self._build_full_page(
            content,
            "statement | gclucas",
            "Artist's statement",
            "https://picsum.photos/1200/600?random=statement",
            f"{self.site_data['url']}/statement/",
            f"{self.site_data['url']}/statement/"
        )
        
        output_path = self.output_dir / 'statement' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_work_index(self):
        """Build /work/index.html"""
        print("📂 Building work index...")
        
        series_list = ""
        for series in self.series_data:
            works_count = len(self._get_works_by_series(series['id']))
            series_list += f"""
            <a href="/work/{series['id']}/" class="series-card">
                <img src="{series['coverImage']}" alt="{series['titleEn']}" loading="lazy">
                <h3>{series['titleEn']}</h3>
                <p>{series['statementEn'][:100]}...</p>
                <div class="year">{series['year']} • {works_count} works</div>
            </a>
            """
        
        content = self._render_template(self.work_template, {
            'series_list': series_list
        })
        
        html = self._build_full_page(
            content,
            "work | gclucas",
            "Explore the series",
            "https://picsum.photos/1200/600?random=work",
            f"{self.site_data['url']}/work/",
            f"{self.site_data['url']}/work/"
        )
        
        output_path = self.output_dir / 'work' / 'index.html'
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
                <div class="gallery-item" data-technique="{work['technique']}" data-dimensions="{dimensions}">
                    <img src="{work['cloudinaryUrl']}" alt="{work['titleEn']}" loading="lazy">
                    <div class="gallery-item-info">
                        <h4>{work['titleEn']}</h4>
                        <p>{work['year']}</p>
                    </div>
                </div>
                """

            prev_s = self.series_data[i - 1] if i > 0 else None
            next_s = self.series_data[i + 1] if i < len(self.series_data) - 1 else None
            nav = '<div class="series-nav">'
            nav += f'<a href="/work/{prev_s["id"]}/">← {prev_s["titleEn"]}</a>' if prev_s else '<span></span>'
            nav += '<a href="/work/">work</a>'
            nav += f'<a href="/work/{next_s["id"]}/">{next_s["titleEn"]} →</a>' if next_s else '<span></span>'
            nav += '</div>'

            content = self._render_template(self.series_template, {
                'series_title': series['titleEn'],
                'series_year': series['year'],
                'series_statement': f"<p>{series['statementEn']}</p>",
                'gallery': gallery_html,
                'series_nav': nav
            })

            html = self._build_full_page(
                content,
                f"{series['titleEn']} | gclucas",
                series['statementEn'][:160],
                series['coverImage'],
                f"{self.site_data['url']}/work/{series_id}/",
                f"{self.site_data['url']}/work/{series_id}/"
            )

            output_path = self.output_dir / 'work' / series_id / 'index.html'
            self._save_html(output_path, html)
            print(f"✅ Created: {output_path} ({len(works)} works)")
    
    def build_text_index(self):
        """Build /text/index.html"""
        print("📚 Building texts index...")
        
        texts_list = """
        <div class="texts-grid">
            <article class="text-card">
                <h3>Ficciones</h3>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                <a href="/text/ficciones/">read more</a>
            </article>
            <article class="text-card">
                <h3>Sobre Peligro de Extinción</h3>
                <p>Exploración del concepto de extinción en la obra contemporánea.</p>
                <a href="/text/peligro-extincion/">read more</a>
            </article>
        </div>
        """
        
        content = self._render_template(self.text_template, {
            'texts_list': texts_list
        })
        
        html = self._build_full_page(
            content,
            "texts | gclucas",
            "Writings and reflections",
            "https://picsum.photos/1200/600?random=texts",
            f"{self.site_data['url']}/text/",
            f"{self.site_data['url']}/text/"
        )
        
        output_path = self.output_dir / 'text' / 'index.html'
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
            'bio_text': f"<p>{self.site_data['bioEn']}</p>",
            'exhibitions': exhibitions_html
        })
        
        html = self._build_full_page(
            content,
            "bio | gclucas",
            "Artist biography and exhibitions",
            "https://picsum.photos/1200/600?random=bio",
            f"{self.site_data['url']}/bio/",
            f"{self.site_data['url']}/bio/"
        )
        
        output_path = self.output_dir / 'bio' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_contact(self):
        """Build /contact/index.html"""
        print("📞 Building contact page...")
        
        content = self._render_template(self.contact_template, {
            'email': self.site_data['email'],
            'whatsapp_number': self.site_data['whatsapp_number'],
            'instagram': self.site_data['instagram']
        })
        
        html = self._build_full_page(
            content,
            "contact | gclucas",
            "Get in touch",
            "https://picsum.photos/1200/600?random=contact",
            f"{self.site_data['url']}/contact/",
            f"{self.site_data['url']}/contact/"
        )
        
        output_path = self.output_dir / 'contact' / 'index.html'
        self._save_html(output_path, html)
        print(f"✅ Created: {output_path}")
    
    def build_sitemap(self):
        """Build /sitemap.xml — se regenera con las URLs reales en cada build"""
        print("🗺️  Building sitemap...")

        base_url = self.site_data['url'].rstrip('/')
        today = date.today().isoformat()
        static_paths = ['/', '/statement/', '/work/', '/text/', '/bio/', '/contact/']
        paths = static_paths + [f"/work/{s['id']}/" for s in self.series_data]

        entries = "\n".join(
            f"  <url>\n    <loc>{base_url}{p}</loc>\n    <lastmod>{today}</lastmod>\n  </url>"
            for p in paths
        )
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{entries}\n"
            "</urlset>\n"
        )

        output_path = self.output_dir / 'sitemap.xml'
        output_path.write_text(xml, encoding='utf-8')
        print(f"✅ Created: {output_path} ({len(paths)} URLs)")
    
    def build(self):
        """Build entire site"""
        print("\n" + "="*60)
        print("🎨 ATELIER v2.0 - Multipágina SEO-Optimizado")
        print("="*60)
        print(f"⏰ Building at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
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
        print("\nPáginas generadas:")
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
