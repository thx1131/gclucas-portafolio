// GALLERY MODAL
const galleryModal = document.getElementById('galleryModal');
const modalImage = document.getElementById('modalImage');
const modalTitle = document.getElementById('modalTitle');
const modalYear = document.getElementById('modalYear');
const modalTechnique = document.getElementById('modalTechnique');
const modalDimensions = document.getElementById('modalDimensions');
const modalClose = document.getElementById('modalClose');
const modalPrev = document.getElementById('modalPrev');
const modalNext = document.getElementById('modalNext');

let currentGalleryItems = [];
let currentIndex = 0;

// Abrir modal
function openGallery(items, index) {
    currentGalleryItems = items;
    currentIndex = index;
    updateModal();
    galleryModal.classList.add('active');
}

// Cerrar modal
function closeGallery() {
    galleryModal.classList.remove('active');
    currentGalleryItems = [];
    currentIndex = 0;
}

// Actualizar contenido del modal
function updateModal() {
    if (!currentGalleryItems.length) return;
    
    const item = currentGalleryItems[currentIndex];
    modalImage.src = item.image;
    modalImage.alt = item.title;
    modalTitle.textContent = item.title;
    modalYear.textContent = item.year;
    modalTechnique.textContent = `Technique: ${item.technique}`;
    modalDimensions.textContent = `Dimensions: ${item.dimensions}`;
}

// Navegación
function prevImage() {
    currentIndex = (currentIndex - 1 + currentGalleryItems.length) % currentGalleryItems.length;
    updateModal();
}

function nextImage() {
    currentIndex = (currentIndex + 1) % currentGalleryItems.length;
    updateModal();
}

// Event listeners
if (modalClose) {
    modalClose.addEventListener('click', closeGallery);
}

if (modalPrev) {
    modalPrev.addEventListener('click', prevImage);
}

if (modalNext) {
    modalNext.addEventListener('click', nextImage);
}

// Cerrar modal al hacer click fuera
if (galleryModal) {
    galleryModal.addEventListener('click', (e) => {
        if (e.target === galleryModal) {
            closeGallery();
        }
    });
}

// Navegar con teclado
document.addEventListener('keydown', (e) => {
    if (!galleryModal.classList.contains('active')) return;
    
    if (e.key === 'ArrowLeft') prevImage();
    if (e.key === 'ArrowRight') nextImage();
    if (e.key === 'Escape') closeGallery();
});

// Delegar clicks en items de galería
document.addEventListener('click', (e) => {
    if (e.target.closest('.gallery-item img')) {
        const item = e.target.closest('.gallery-item');
        const galleryContainer = item.closest('.gallery');
        
        if (galleryContainer) {
            const items = Array.from(galleryContainer.querySelectorAll('.gallery-item')).map(el => ({
                image: el.querySelector('img').src,
                title: el.querySelector('h4')?.textContent || '',
                year: el.querySelector('.year')?.textContent || '',
                technique: el.dataset.technique || '',
                dimensions: el.dataset.dimensions || ''
            }));
            
            const index = Array.from(galleryContainer.querySelectorAll('.gallery-item')).indexOf(item);
            openGallery(items, index);
        }
    }
});

console.log('gallery.js loaded');
