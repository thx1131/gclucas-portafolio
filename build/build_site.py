#!/usr/bin/env python3
"""
Atelier: Artist Portfolio Engine
build_site.py - Generate static HTML from JSON data

This script reads data from JSON files and generates static HTML pages
for the portfolio website.
"""

import json
import os
from pathlib import Path
from datetime import datetime

class SiteBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.templates_dir = self.base_dir / 'templates'
        self.output_dir = self.base_dir / 'work'
        
        # Load data
        self.series_data = self._load_json('series.json')
        self.works_data = self._load_json('works.json')
        self.site_data = self._load_json('site.json')
        
        # Load templates
        self.base_template = self._load_template('base.html')
        self.home_template = self._load_template('home.html')
        self.work_template = self._load_template('work.html')
        self.series_template = self._load_template('series.html')
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
    
    def _build_gallery_html(self, works):
        """Build gallery HTML for a series"""
        gallery_html = ""
        for work in works:
            dimensions = f"{work['dimensions']['height']}×{work['dimensions']['width']} {work['dimensions']['unit']}"
            gallery_html += f"""
            <div class="gallery-item" data-technique="{work['technique']}" data-dimensions="{dimensions}">
                <img src="{work['cloudinaryUrl']}" alt="{work['titleEn']}" loading="lazy">
                <div class="gallery-item-info">
                    <h4>{work['titleEn']}</h4>
                    <p>{work['year']}</p>
                </div>
            </div>
            """
        return gallery_html
    
    def _build_series_preview(self):
        """Build series preview for home page"""
        preview_html = ""
        for series in self.series_data:
            preview_html += f"""
            <a href="/work/{series['id']}/" class="series-card">
                <img src="{series['coverImage']}" alt="{series['titleEn']}" loading="lazy">
                <h3>{series['titleEn']}</h3>
                <div class="year">{series['year']}</div>
            </a>
            """
        return preview_html
    
    def _build_series_list(self):
        """Build series list for work page"""
        list_html = ""
        for series in self.series_data:
            list_html += f"""
            <a href="/work/{series['id']}/" class="series-card">
                <img src="{series['coverImage']}" alt="{series['titleEn']}" loading="lazy">
                <h3>{series['titleEn']}</h3>
                <p>{series['statementEn'][:100]}...</p>
                <div class="year">{series['year']}</div>
            </a>
            """
        return list_html
    
    def build_home(self):
        """Build index.html (home page)"""
        print("🏠 Building home page...")
        
        series_preview = self._build_series_preview()
        content = self._render_template(self.home_template, {
            'series_preview': series_preview
        })
        
        html = self._render_template(self.base_template, {
            'title': self.site_data['title'],
            'description': self.site_data['descriptionEn'],
            'og_image': 'https://picsum.photos/1200/600?random=og',
            'og_url': self.site_data['url'],
            'canonical_url': self.site_data['url'],
            'navbar': self.navbar_component,
            'content': content,
            'footer': self.footer_component
        })
        
        output_path = self.base_dir / 'index.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Created: {output_path}")
    
    def build_work_index(self):
        """Build work/index.html (series list)"""
        print("📂 Building work index...")
        
        series_list = self._build_series_list()
        content = self._render_template(self.work_template, {
            'series_list': series_list
        })
        
        html = self._render_template(self.base_template, {
            'title': 'work | gclucas',
            'description': 'Explore the series',
            'og_image': 'https://picsum.photos/1200/600?random=work',
            'og_url': f"{self.site_data['url']}/work/",
            'canonical_url': f"{self.site_data['url']}/work/",
            'navbar': self.navbar_component,
            'content': content,
            'footer': self.footer_component
        })
        
        output_dir = self.output_dir
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / 'index.html'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Created: {output_path}")
    
    def build_series_pages(self):
        """Build /work/[series-id]/index.html for each series"""
        print("🎨 Building series pages...")
        
        for series in self.series_data:
            series_id = series['id']
            works = self._get_works_by_series(series_id)
            
            gallery_html = self._build_gallery_html(works)
            
            content = self._render_template(self.series_template, {
                'series_title': series['titleEn'],
                'series_year': series['year'],
                'series_statement': f"<p>{series['statementEn']}</p>",
                'gallery': gallery_html
            })
            
            html = self._render_template(self.base_template, {
                'title': f"{series['titleEn']} | gclucas",
                'description': series['statementEn'][:160],
                'og_image': series['coverImage'],
                'og_url': f"{self.site_data['url']}/work/{series_id}/",
                'canonical_url': f"{self.site_data['url']}/work/{series_id}/",
                'navbar': self.navbar_component,
                'content': content,
                'footer': self.footer_component
            })
            
            # Create directory
            series_dir = self.output_dir / series_id
            series_dir.mkdir(exist_ok=True)
            
            # Write file
            output_path = series_dir / 'index.html'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✅ Created: {output_path} ({len(works)} works)")
    
    def build(self):
        """Build entire site"""
        print("\n" + "="*60)
        print("🎨 ATELIER - Artist Portfolio Engine")
        print("="*60)
        print(f"⏰ Building at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.build_home()
        self.build_work_index()
        self.build_series_pages()
        
        print("\n" + "="*60)
        print("✅ Site generation complete!")
        print("="*60 + "\n")


if __name__ == '__main__':
    builder = SiteBuilder()
    builder.build()
