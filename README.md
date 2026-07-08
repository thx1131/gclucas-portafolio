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
cd build
python build_site.py

# View output
ls ../work/
```

### Test Locally

```bash
# Start local server
python -m http.server 8000

# Open browser
# http://localhost:8000
```

---

## 📝 EDITING CONTENT

### Option 1: Edit JSON Directly

1. Open `data/series.json` or `data/works.json`
2. Make changes
3. Run `python build/build_site.py`
4. Commit and push

### Option 2: Edit Excel, Export CSV

1. Open Excel spreadsheet
2. Make changes
3. Export as CSV
4. Run `python build/excel_to_json.py` (coming soon)
5. Run `python build/build_site.py`
6. Commit and push

---

## 🎨 HOW IT WORKS

```
data/series.json + data/works.json
         ↓
   build_site.py
         ↓
/work/pixelogue/index.html
/work/headless/index.html
/work/... (more series)
```

Each time you run `build_site.py`, all HTML files are regenerated from JSON.

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
├── data/                   ← JSON data
│   ├── series.json
│   ├── works.json
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
│   └── build_site.py
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
python build/build_site.py
```

4. Commit:
```bash
git add . && git commit -m "feat: add new-series" && git push
```

---

## 🌐 DEPLOYMENT

### GitHub Pages / Cloudflare Pages

The `work/` folder (and `index.html`) are automatically deployed via GitHub Pages or Cloudflare Pages.

**Workflow:**
1. Push to GitHub
2. Cloudflare Pages deploys automatically
3. Changes live in ~1 minute

---

## 📊 DATA STRUCTURE

### series.json
- Metadata for each series (title, year, description)
- Used to generate `/work/series-name/` pages
- Referenced by works.json via `series` field

### works.json
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
# Try python3
python3 build/build_site.py
```

### "FileNotFoundError: data/series.json"
Make sure you're running from the project root:
```bash
cd gclucas-portafolio
python build/build_site.py
```

### "Images not loading"
Check Cloudinary URLs in `data/works.json`. Should be:
```
https://res.cloudinary.com/dt2w4nxz6/image/upload/...
```

---

## 🚀 FUTURE ROADMAP

- [ ] Admin panel (Supabase)
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
