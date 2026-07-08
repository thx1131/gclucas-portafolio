// DARK MODE TOGGLE
const themeToggle = document.getElementById('themeToggle');
const htmlElement = document.documentElement;
const bodyElement = document.body;

// Detectar preferencia del sistema
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

// Obtener tema guardado o usar preferencia del sistema
function getInitialTheme() {
    const saved = localStorage.getItem('gclucas-theme');
    if (saved) {
        return saved;
    }
    return prefersDark ? 'dark' : 'light';
}

// Aplicar tema
function applyTheme(theme) {
    if (theme === 'dark') {
        bodyElement.classList.add('dark-mode');
        htmlElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('gclucas-theme', 'dark');
    } else {
        bodyElement.classList.remove('dark-mode');
        htmlElement.setAttribute('data-theme', 'light');
        localStorage.setItem('gclucas-theme', 'light');
    }
}

// Inicializar
const initialTheme = getInitialTheme();
applyTheme(initialTheme);

// Toggle al hacer click
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = localStorage.getItem('gclucas-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });
}

// Escuchar cambios en preferencia del sistema
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('gclucas-theme')) {
        applyTheme(e.matches ? 'dark' : 'light');
    }
});

console.log('darkmode.js loaded');
