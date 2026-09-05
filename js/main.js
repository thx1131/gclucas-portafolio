// NAVBAR TOGGLE
const navbarToggle = document.getElementById('navbarToggle');
const navbarMenu = document.getElementById('navbarMenu');

if (navbarToggle) {
    navbarToggle.addEventListener('click', () => {
        navbarMenu.classList.toggle('active');
        navbarToggle.classList.toggle('active');
    });
}

// Cerrar menú al hacer click en un link
document.querySelectorAll('.navbar-menu a').forEach(link => {
    link.addEventListener('click', () => {
        navbarMenu.classList.remove('active');
        navbarToggle.classList.remove('active');
    });
});

// SMOOTH SCROLL
// Los links del sitio son "/#statement", "/#bio", etc. (con path), no "#statement" solo.
document.querySelectorAll('a[href*="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        const hashIndex = href.indexOf('#');
        const path = href.slice(0, hashIndex) || '/';
        const hash = href.slice(hashIndex);

        // Solo interceptamos si el ancla vive en la página actual;
        // si no, dejamos que el navegador navegue normal (ej. a home) y salte el hash ahí.
        if (path !== window.location.pathname) return;

        const target = document.querySelector(hash);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

console.log('main.js loaded');
