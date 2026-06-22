/* ============================================
   MAIN - LÓGICA GENERAL DEL SITIO
   ============================================ */

class SiteMain {
    constructor() {
        this.hamburger = document.getElementById('hamburger');
        this.navLinks = document.querySelector('.nav-links');
        this.navbar = document.querySelector('.navbar');
        
        this.init();
    }

    init() {
        this.setupHamburgerMenu();
        this.setupNavLinks();
        this.setupNavbarScroll();
        this.setupContactForm();
    }

    /* ============================================
       HAMBURGER MENU
       ============================================ */
    setupHamburgerMenu() {
        this.hamburger.addEventListener('click', () => {
            this.navLinks.classList.toggle('active');
            this.hamburger.classList.toggle('active');
        });

        // Cerrar menú al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.navbar')) {
                this.navLinks.classList.remove('active');
                this.hamburger.classList.remove('active');
            }
        });
    }

    /* ============================================
       NAV LINKS - CERRAR MENÚ AL HACER CLICK
       ============================================ */
    setupNavLinks() {
        const links = this.navLinks.querySelectorAll('a');
        
        links.forEach(link => {
            link.addEventListener('click', () => {
                this.navLinks.classList.remove('active');
                this.hamburger.classList.remove('active');
            });
        });
    }

    /* ============================================
       NAVBAR SCROLL - EFECTO AL SCROLLEAR
       ============================================ */
    setupNavbarScroll() {
        let lastScrollY = 0;
        let ticking = false;

        window.addEventListener('scroll', () => {
            lastScrollY = window.scrollY;
            
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    if (lastScrollY > 50) {
                        this.navbar.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.1)';
                    } else {
                        this.navbar.style.boxShadow = 'none';
                    }
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    /* ============================================
       CONTACT FORM
       ============================================ */
    setupContactForm() {
        const form = document.getElementById('contactForm');
        
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const nombre = form.querySelector('input[type="text"]').value;
                const email = form.querySelector('input[type="email"]').value;
                const mensaje = form.querySelector('textarea').value;
                
                // Crear enlace mailto con subject y body
                const subject = encodeURIComponent(`Nuevo contacto desde el sitio - ${nombre}`);
                const body = encodeURIComponent(`Nombre: ${nombre}\nEmail: ${email}\n\nMensaje:\n${mensaje}`);
                
                // Enviar por email
                window.location.href = `mailto:gclucas999@gmail.com?subject=${subject}&body=${body}`;
                
                // Mostrar mensaje de confirmación
                this.showFormMessage(form, 'Abriendo tu cliente de email...');
                
                // Limpiar formulario después de 1 segundo
                setTimeout(() => {
                    form.reset();
                }, 1000);
            });
        }
    }

    showFormMessage(form, message) {
        const button = form.querySelector('button');
        const originalText = button.textContent;
        
        button.textContent = message;
        button.disabled = true;
        
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 2000);
    }
}

/* ============================================
   UTILIDADES GLOBALES
   ============================================ */

// Smooth scroll para navegación interna
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        // Si es un link válido (no es solo "#")
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            
            const target = document.querySelector(href);
            const offset = 80; // Altura del navbar fijo
            const targetPosition = target.offsetTop - offset;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

/* ============================================
   INICIALIZAR
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    new SiteMain();
    
    // Log para verificar que todo cargó
    console.log('✓ Sitio cargado correctamente');
    console.log('✓ Gallery cargada');
    console.log('✓ Darkmode activado');
});