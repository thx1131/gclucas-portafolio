/* ============================================
   DARKMODE TOGGLE
   ============================================ */

class DarkmodeToggle {
    constructor() {
        this.toggle = document.getElementById('darkmodeToggle');
        this.body = document.body;
        this.storageKey = 'gclucas-darkmode';
        
        this.init();
    }

    init() {
        // Cargar preferencia guardada o usar preferencia del sistema
        this.loadTheme();
        
        // Event listener al botón
        this.toggle.addEventListener('click', () => this.toggleTheme());
    }

    loadTheme() {
        // Verificar localStorage
        const savedTheme = localStorage.getItem(this.storageKey);
        
        if (savedTheme) {
            // Si hay preferencia guardada, usarla
            if (savedTheme === 'dark') {
                this.enableDarkMode();
            } else {
                this.disableDarkMode();
            }
        } else {
            // Si no hay preferencia guardada, usar preferencia del sistema
            if (this.prefersDarkMode()) {
                this.enableDarkMode();
            } else {
                this.disableDarkMode();
            }
        }
    }

    prefersDarkMode() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    toggleTheme() {
        if (this.body.classList.contains('dark-mode')) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode();
        }
    }

    enableDarkMode() {
        this.body.classList.add('dark-mode');
        localStorage.setItem(this.storageKey, 'dark');
    }

    disableDarkMode() {
        this.body.classList.remove('dark-mode');
        localStorage.setItem(this.storageKey, 'light');
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new DarkmodeToggle();
});