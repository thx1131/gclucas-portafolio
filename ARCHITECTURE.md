# ATELIER: Artist Portfolio Engine

**v1.0**

A clean, scalable static site generator for visual artists. Built with vanilla HTML, CSS, and JavaScript. Designed to be reutilizable for any artist portfolio.

---

## 🎯 PHILOSOPHY

### Data Flow

```
CMS panel (admin/) or direct edit ─┐
                                     ├─→ JSON (source of truth, data/*.json)
                                     ┘         ↓ [build_site_v2.py, runs in Cloudflare Pages CI]
                                          HTML (static output)
                                                ↓ [git push / merged PR]
                                          GitHub + Cloudflare Pages (published)
```

**One truth per level.** (Excel/Sheets were the original editorial source; retired 2026-09-04 — `data/*.json` is now edited directly, either by hand or through the CMS panel in `admin/`.)

- **JSON:** Where you edit content (by hand, or via the CMS at `/admin/`) and what the technical system reads from
- **HTML:** What Google indexes and users see
- **GitHub:** Version history of everything

### Core Principles

1. **SEO First**
   - Each series gets its own URL: `/work/pixelogue/`
   - Each page has complete metadata (title, description, og:image, canonical)
   - No JavaScript for critical content
   - HTML is semantic and crawlable

2. **Sustainable Code**
   - No frameworks, no build complexity
   - Plain HTML, CSS, JavaScript
   - Python script for static generation
   - Easy to maintain and extend

3. **Artist-Friendly**
   - Edit via the CMS panel (`/admin/`, no code) or directly in `data/*.json`
   - Automatic page generation
   - No manual HTML editing needed

4. **Future-Proof**
   - Design supports easy migration to Supabase + API
   - JSON structure remains the same if we add a backend
   - Each piece (JSON, templates, CSS) can be replaced independently
   - Git history preserves the entire evolution

---

## 📁 FOLDER STRUCTURE

```
gclucas-portafolio/
│
├── index.html                          ← Landing page (generated)
│
├── build/
│   └── build_site.py                   ← Main generator script
│
├── templates/
│   ├── base.html                       ← Master template
│   ├── home.html                       ← Homepage content
│   ├── work.html                       ← Series list template
│   ├── series.html                     ← Individual series template
│   └── components/
│       ├── navbar.html
│       ├── footer.html
│       └── seo.html                    ← SEO metadata (if needed)
│
├── data/
│   ├── series.json                     ← 24 series metadata
│   ├── works.json                      ← 144+ individual works
│   └── site.json                       ← Global config (email, socials, etc)
│
├── work/                               ← Generated output
│   ├── index.html                      ← All series
│   ├── pixelogue/
│   │   └── index.html                  ← Pixelogue series page
│   ├── headless/
│   │   └── index.html                  ← Headless series page
│   └── ...                             ← More series
│
├── css/
│   ├── main.css                        ← Responsive styles + dark mode
│   └── darkmode.css                    ← Dark mode reference
│
├── js/
│   ├── main.js                         ← Navbar, smooth scroll, forms
│   ├── darkmode.js                     ← Dark mode toggle + localStorage
│   └── gallery.js                      ← Modal gallery, navigation
│
├── ARCHITECTURE.md                     ← This file
└── README.md                           ← Setup instructions
```

---

## 🔑 KEY DECISIONS

### 1. Why Separate `series.json` and `works.json`?

**Good:**
```json
// series.json
{ "id": "pixelogue", "statement": "..." }

// works.json
{ "id": "PIX001", "series": "pixelogue", ... }
```

**Bad (single file):**
```json
{
  "id": "pixelogue",
  "statement": "...",
  "works": [ { ... }, { ... }, { ... } ]  // Duplicated series data
}
```

**Reason:** When you change a series description, you only edit ONE place. No duplicated data.

### 2. Why Static HTML, Not JSON-Driven JavaScript?

**Bad (client-side rendering):**
```
User visits /work/pixelogue/ → JavaScript loads JSON → JS builds HTML
Problems: Slower first load, Google crawls empty page, Open Graph broken
```

**Good (server-side generation):**
```
Developer: python build_site.py
build_site.py reads JSON → generates /work/pixelogue/index.html
User visits /work/pixelogue/ → Gets complete HTML
Google: Indexes full page immediately, Open Graph works, SEO perfect
```

### 3. Why Python for Build Script?

- ✅ Easy to learn and modify
- ✅ Great for JSON manipulation
- ✅ Built-in on most systems
- ✅ No npm dependencies, no complex build tools

### 4. Why Immutable IDs?

**BAD:**
```json
{ "id": "visión-de-filippo", "title": "Vision of Filippo" }
// If you change title → change ID → all URLs break
```

**GOOD:**
```json
{ "id": "vision-filippo", "titleEn": "Vision of Filippo", "titleEs": "visión de filippo" }
// You can change titles without breaking URLs or references
```

### 5. Why `/work/pixelogue/` Not `/work/pixelogue.html`?

**Technical Advantage:**
- URLs look cleaner: `gclucas.art/work/pixelogue/`
- Internally stored as `/work/pixelogue/index.html` (Cloudflare handles it)
- Can easily add sub-pages later: `/work/pixelogue/more-human-than-human/`

### 6. Why Cloudinary Only, No Local Images?

**Benefits:**
- Automatic optimization (WebP, compression, resizing)
- Global CDN (fast anywhere in world)
- Cache busting with version parameters
- Responsive images without extra code

**Workflow:**
```
Original PNG → Upload to Cloudinary
                    ↓
            Multiple formats generated (WebP, JPEG, etc)
                    ↓
            Copy URL → Paste in works.json
                    ↓
            build_site.py generates HTML with optimized URL
```

---

## 📋 JSON SCHEMAS

### series.json

```json
[
  {
    "id": "pixelogue",                    // Immutable identifier
    "titleEn": "Pixelogue",
    "titleEs": "pixelogue",
    "year": 2019,
    "statementEn": "...",                 // Full description
    "statementEs": "...",
    "coverImage": "https://cloudinary...", // Hero image
    "order": 10                           // Display order
  }
]
```

### works.json

```json
[
  {
    "id": "PIX001",                       // Unique work ID
    "series": "pixelogue",                // Reference to series
    "titleEn": "More Human Than Human",
    "titleEs": "más humano que humano",
    "year": 2019,
    "technique": "acrylic, graphite on canvas",
    "techniqueEs": "acrílico, grafito sobre lienzo",
    "dimensions": {
      "height": 155,
      "width": 140,
      "unit": "cm"
    },
    "cloudinaryUrl": "https://res.cloudinary.com/...",
    "order": 1                            // Order within series
  }
]
```

### site.json

```json
{
  "title": "gclucas",
  "email": "gclucas999@gmail.com",
  "instagram": "https://instagram.com/lucasasecas",
  "statementEn": "...",
  "bioEn": "..."
}
```

---

## 🎨 DESIGN DECISIONS

### Color Palette (CSS Variables)

```css
:root {
  --bg-light: #ffffff;
  --text-light: #1a1a1a;
  --border-light: #e0e0e0;
  --accent-light: #666666;
}

body.dark-mode {
  --bg-dark: #1a1a1a;
  --text-dark: #f0f0f0;
  --border-dark: #333333;
  --accent-dark: #b0b0b0;
}
```

### Typography

- **Font Stack:** System fonts (`-apple-system, Segoe UI, etc`)
- **Size:** 16px base
- **Weight:** 300-400 (light to regular)
- **All lowercase:** Brand consistency

### Responsive Breakpoints

- **Desktop:** 1200px+
- **Tablet:** 768px - 1199px
- **Mobile:** < 768px
- **Small mobile:** < 390px

---

## 🔧 WORKFLOW

### For Content Editors (Artists)

```
1. Go to gclucas.art/admin/, log in with GitHub
2. Edit series/works/statement/bio text, reorder, or upload new photos
3. Save → opens a PR (editorial workflow)
4. Developer reviews the PR (Cloudflare Pages auto-preview) and merges
5. Merge → Cloudflare Pages runs build_site_v2.py and deploys
```

### For Developers

```
# Build the site
python3 build/build_site_v2.py

# Check output
ls work/

# Test locally
python3 -m http.server 8000

# Commit changes
git add . && git commit -m "feat: add new series" && git push
```

---

## 📈 ROADMAP

### v1.0 (Current)
- ✅ Static site generation
- ✅ Dark mode
- ✅ Responsive design
- ✅ Gallery with modal

### v2.0 (Current)
- [x] Multipágina + SEO (see Atelier v2.0, `build/build_site_v2.py`)
- [x] Git-based CMS panel for editing (`admin/`, Sveltia CMS — no Supabase/backend needed)

### v3.0 (Later)
- [ ] Blog / Articles section
- [ ] Timeline interactive view
- [ ] Multiple language support
- [ ] Email newsletter

---

## 🚀 HOW TO USE

### Initial Setup

```bash
# Clone repo
git clone https://github.com/thx1131/gclucas-portafolio
cd gclucas-portafolio

# Make sure Python 3 is installed
python --version

# Run generator
cd build
python build_site.py

# Output files are now in ../work/
```

### Make Changes

1. **Edit data files directly:**
   ```
   data/series.json   (shape: { "series": [...] })
   data/works.json    (shape: { "works": [...] })
   data/site.json
   ```

2. **Or edit via the CMS panel:** `gclucas.art/admin/` — see `admin/config.yml`.

3. **Regenerate HTML:**
   ```
   python3 build/build_site_v2.py
   ```

4. **Push to GitHub:**
   ```
   git add . && git commit -m "Update: new works" && git push
   ```

5. **Cloudflare Pages deploys automatically**

---

## 🔒 Naming Conventions

### Series IDs
- **Format:** kebab-case, lowercase
- **Examples:** `pixelogue`, `peligro-extincion`, `vision-filippo`
- **Rule:** Never change once created (SEO, URLs depend on it)

### Work IDs
- **Format:** SERIES-NUMBER (e.g., PIX001, PEL002)
- **Examples:** `PIX001`, `HEAD005`, `NUDE001`
- **Rule:** Unique and immutable

### Image Files (Cloudinary)
- **Format:** `serie/titulo-obra.webp`
- **Examples:** `pixelogue/more-human-than-human.webp`
- **Rule:** Clean, descriptive, no spaces

### Git Commits
- **Format:** Conventional Commits
- **Examples:**
  ```
  feat: add vision-filippo series
  fix: gallery modal scrolling on mobile
  style: improve typography spacing
  docs: update architecture
  refactor: split series and works JSON
  ```

---

## 📚 KEY FILES

| File | Purpose |
|------|---------|
| `build/build_site.py` | Main generator - reads JSON, writes HTML |
| `data/series.json` | Series metadata (24 series) |
| `data/works.json` | Works metadata (144+ works) |
| `data/site.json` | Global configuration |
| `templates/base.html` | Master template (all pages inherit) |
| `css/main.css` | Styles + dark mode + responsive |
| `js/main.js` | Navigation and smooth scroll |
| `js/darkmode.js` | Dark mode toggle logic |
| `js/gallery.js` | Modal gallery and navigation |

---

## ⚖️ LICENSE

Open source. Use freely for any artist portfolio.

---

**Built with ❤️ for visual artists**

Contact: Luis | Developer
