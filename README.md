# gclucas-portafolio

Artist portfolio website for **GC Lucas**, visual artist exploring contradictions and transitions through painting, engraving, photography, and installation.

**Live:** https://gclucas.art

---

## 🚀 QUICK START

### Prerequisites
- Python 3.7+
- Git
- A text editor (VSCode, VSCodium, etc)

### Setup

```bash
# Clone repository
git clone https://github.com/thx1131/gclucas-portafolio
cd gclucas-portafolio

# Generate HTML from JSON
python3 build/build_site_v2.py

# View output
ls work/
```

> Cloudflare Pages debe correr este mismo comando en cada push a `main` (ver sección de Deployment para el estado real). Corré el comando local para probar cambios antes de pushear.

### Test Locally

```bash
# Start local server
python -m http.server 8000

# Open browser
# http://localhost:8000
```

---

## 📝 EDITING CONTENT

### Option 1: CMS panel (Lucas, no code)

1. Go to `gclucas.art/admin/`, log in with GitHub
2. Edit text, reorder series/works, or upload new photos
3. Save → opens a PR automatically (editorial workflow)
4. Luis reviews the PR (Cloudflare Pages generates an automatic preview link) and merges it
5. Merge → Cloudflare Pages rebuilds and publishes

Config lives in `admin/config.yml`. Setup checklist (GitHub OAuth App, Cloudflare Worker, Cloudinary preset) is in `gclucas_traspaso.md`.

### Option 2: Edit JSON directly (Luis)

1. Open `data/series.json` or `data/works.json` (each is `{"series": [...]}` / `{"works": [...]}`)
2. Make changes
3. Run `python3 build/build_site_v2.py`
4. Commit and push

The old Excel/Sheets editing flow was retired — `data/*.json` is the single source of truth, edited either via the CMS or directly.

---

## 🎨 HOW IT WORKS

```
admin/ (CMS panel, PR-based) ─┐
                               ├─→ data/series.json + data/works.json + data/site.json
data/*.json edited by hand ───┘         ↓
                                  build_site_v2.py
                                         ↓
                              /work/pixelogue/index.html
                              /work/headless/index.html
                              /work/... (more series)
```

Each time `build_site_v2.py` runs (in Cloudflare Pages CI, or locally to test), all HTML files are regenerated from JSON.

---

## 📂 PROJECT STRUCTURE

```
gclucas-portafolio/
├── index.html              ← Landing page (generated)
├── work/                   ← Series pages (generated)
│   ├── index.html
│   ├── pixelogue/
│   ├── headless/
│   └── ...
├── admin/                  ← CMS panel (Sveltia)
│   ├── index.html
│   └── config.yml
├── data/                   ← JSON data
│   ├── series.json         ← { "series": [...] }
│   ├── works.json           ← { "works": [...] }
│   └── site.json
├── templates/              ← HTML templates
│   ├── base.html
│   ├── home.html
│   ├── series.html
│   └── components/
├── css/                    ← Styles
│   ├── main.css
│   └── darkmode.css
├── js/                     ← JavaScript
│   ├── main.js
│   ├── darkmode.js
│   └── gallery.js
├── build/                  ← Build scripts
│   └── build_site_v2.py
├── ARCHITECTURE.md         ← Design decisions
└── README.md              ← This file
```

---

## 🎯 FEATURES

- ✅ **Static site** - Fast, secure, SEO-friendly
- ✅ **Dark mode** - Toggle + system preference detection
- ✅ **Responsive** - Mobile, tablet, desktop
- ✅ **Gallery modal** - Click images, navigate with arrows/keyboard
- ✅ **Semantic HTML** - Clean, crawlable by Google
- ✅ **No frameworks** - Vanilla HTML, CSS, JavaScript
- ✅ **Git history** - Complete evolution of the portfolio

---

## 🔧 DEVELOPMENT

### Add a New Series

1. Add entry to `data/series.json`:
```json
{
  "id": "new-series",
  "titleEn": "New Series",
  "year": 2024,
  "statementEn": "Description here...",
  "coverImage": "https://cloudinary-url.jpg",
  "order": 60
}
```

2. Add works to `data/works.json`:
```json
{
  "id": "NEW001",
  "series": "new-series",
  "titleEn": "Work Title",
  "year": 2024,
  "technique": "technique here",
  "dimensions": {"height": 100, "width": 80, "unit": "cm"},
  "cloudinaryUrl": "https://cloudinary-url.jpg",
  "order": 1
}
```

3. Run generator:
```bash
python3 build/build_site_v2.py
```

4. Commit:
```bash
git add . && git commit -m "feat: add new-series" && git push
```

---

## 🌐 DEPLOYMENT

### Cloudflare Pages

Build command: `python3 build/build_site_v2.py` · Build output directory: `/` · Root directory: `/`. Python version pinned via `.python-version` (3.13), no `requirements.txt` needed (stdlib only).

**Workflow:**
1. Push to `main` (directly, or via a merged CMS PR)
2. Cloudflare Pages runs the build command and regenerates the HTML
3. Changes live in ~1 minute

Every branch/PR (including the ones the CMS opens) also gets an automatic Cloudflare Pages preview deploy — use that to review a Lucas edit before merging.

---

## 📊 DATA STRUCTURE

### series.json
- Shape: `{ "series": [ {...}, {...} ] }`
- Metadata for each series (title, year, description)
- Used to generate `/work/series-name/` pages
- Referenced by works.json via `series` field

### works.json
- Shape: `{ "works": [ {...}, {...} ] }`
- Metadata for each individual work (144+ total)
- Fields: id, series, title, year, technique, dimensions, cloudinaryUrl
- Used to generate gallery items within series pages

### site.json
- Global configuration (email, social links, copyright, colors)
- Used in all pages' footer and meta tags

---

## 🎨 CUSTOMIZATION

### Colors
Edit `css/main.css`:
```css
:root {
  --bg-light: #ffffff;
  --text-light: #1a1a1a;
  /* etc */
}
```

### Typography
Edit `css/main.css`:
```css
:root {
  --font-sans: /* your font stack */;
  --font-size-base: 16px;
  /* etc */
}
```

### Layout
Edit `templates/` files (base.html, home.html, series.html)

---

## 📖 DOCUMENTATION

For detailed architecture decisions, see **[ARCHITECTURE.md](./ARCHITECTURE.md)**

---

## 🐛 TROUBLESHOOTING

### "Python not found"
```bash
python3 build/build_site_v2.py
```

### "FileNotFoundError: data/series.json"
Make sure you're running from the project root:
```bash
cd gclucas-portafolio
python3 build/build_site_v2.py
```

### "Images not loading"
Check Cloudinary URLs in `data/works.json`. Should be:
```
https://res.cloudinary.com/dt2w4nxz6/image/upload/...
```

---

## 🚀 FUTURE ROADMAP

- [x] Admin panel (Sveltia CMS, git-based — see `admin/`)
- [ ] Blog/articles section
- [ ] Timeline interactive view
- [ ] Multi-language support
- [ ] Email newsletter

---

## 📞 CONTACT

**GC Lucas**
- Email: gclucas999@gmail.com
- Phone: +52 4151511029
- Instagram: @lucasasecas

**Developer**
- Luis (VSCodium, Manjaro Linux)

---

**Built with ❤️ for artists**
