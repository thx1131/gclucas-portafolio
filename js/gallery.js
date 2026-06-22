/* ============================================
   GALLERY - GENERAR GALERÍAS DINÁMICAMENTE
   ============================================ */

class Gallery {
    constructor() {
        this.galeriaContainer = document.getElementById('galeria-container');
        this.textosContainer = document.getElementById('textos-container');
        this.dataUrl = 'data/obras.json';
        
        this.init();
    }

    async init() {
        try {
            const data = await this.loadData();
            this.renderGalerias(data.series);
            this.renderTextos(data.textos);
        } catch (error) {
            console.error('Error cargando datos:', error);
        }
    }

    async loadData() {
        const response = await fetch(this.dataUrl);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    renderGalerias(series) {
        this.galeriaContainer.innerHTML = '';

        series.forEach(serie => {
            // Crear contenedor de serie
            const serieDiv = document.createElement('div');
            serieDiv.className = 'galeria-serie';

            // Título y descripción de serie
            const serieHeader = document.createElement('div');
            serieHeader.innerHTML = `
                <h3>${serie.nombre}</h3>
                <p class="galeria-serie-desc">${serie.descripcion}</p>
            `;
            serieDiv.appendChild(serieHeader);

            // Grid de obras
            const obrasGrid = document.createElement('div');
            obrasGrid.className = 'obras-grid';

            serie.obras.forEach(obra => {
                const obraCard = document.createElement('div');
                obraCard.className = 'obra-card';
                
                obraCard.innerHTML = `
                    <div class="obra-image">
                        <img src="${obra.imagen_thumb}" 
                             alt="${obra.titulo}" 
                             data-full="${obra.imagen}"
                             loading="lazy">
                    </div>
                    <div class="obra-info">
                        <div class="obra-titulo">${obra.titulo}</div>
                        <div class="obra-meta">${obra.año} | ${obra.tecnica}</div>
                        <div class="obra-meta">${obra.dimensiones}</div>
                    </div>
                `;

                // Event listener para abrir modal
                obraCard.addEventListener('click', () => {
                    this.openModal(obra, serie.obras);
                });

                obrasGrid.appendChild(obraCard);
            });

            serieDiv.appendChild(obrasGrid);
            this.galeriaContainer.appendChild(serieDiv);
        });
    }

    renderTextos(textos) {
        this.textosContainer.innerHTML = '';

        textos.forEach(texto => {
            const textoItem = document.createElement('div');
            textoItem.className = 'texto-item';

            const textoHeader = document.createElement('div');
            textoHeader.className = 'texto-header';
            textoHeader.innerHTML = `
                <div>
                    <div class="texto-title">${texto.titulo}</div>
                    <div class="texto-preview">${texto.preview}</div>
                </div>
                <div class="texto-toggle">▼</div>
            `;

            const textoContent = document.createElement('div');
            textoContent.className = 'texto-content';
            textoContent.innerHTML = texto.contenido
                .split('\n\n')
                .map(p => `<p>${p}</p>`)
                .join('');

            // Event listener para expandir/contraer
            textoHeader.addEventListener('click', () => {
                textoItem.classList.toggle('open');
            });

            textoItem.appendChild(textoHeader);
            textoItem.appendChild(textoContent);
            this.textosContainer.appendChild(textoItem);
        });
    }

    openModal(obra, obrasDelaSerie) {
        // Crear modal
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'obraModal';

        // Encontrar índice de la obra actual
        const currentIndex = obrasDelaSerie.findIndex(o => o.id === obra.id);

        modal.innerHTML = `
            <div class="modal-content">
                <span class="modal-close">&times;</span>
                
                <div class="modal-image">
                    <img src="${obra.imagen}" alt="${obra.titulo}">
                </div>

                <div class="modal-info">
                    <h3>${obra.titulo}</h3>
                    <p><strong>año:</strong> ${obra.año}</p>
                    <p><strong>técnica:</strong> ${obra.tecnica}</p>
                    <p><strong>dimensiones:</strong> ${obra.dimensiones}</p>
                </div>

                <div class="modal-nav">
                    ${currentIndex > 0 ? `<button class="modal-prev">← anterior</button>` : ''}
                    ${currentIndex < obrasDelaSerie.length - 1 ? `<button class="modal-next">siguiente →</button>` : ''}
                </div>
            </div>
        `;

        // Agregar modal al DOM
        document.body.appendChild(modal);

        // Event listeners
        const closeBtn = modal.querySelector('.modal-close');
        const prevBtn = modal.querySelector('.modal-prev');
        const nextBtn = modal.querySelector('.modal-next');

        closeBtn.addEventListener('click', () => {
            modal.remove();
        });

        // Cerrar al hacer click afuera
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Navegación
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                modal.remove();
                this.openModal(obrasDelaSerie[currentIndex - 1], obrasDelaSerie);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                modal.remove();
                this.openModal(obrasDelaSerie[currentIndex + 1], obrasDelaSerie);
            });
        }

        // Cerrar con tecla ESC
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new Gallery();
});