/**
 * VULCANO - Lightbox para Galería de Imágenes
 * Visualización modal de imágenes con navegación
 */

'use strict';

const Lightbox = {
  currentIndex: 0,
  images: [],
  overlay: null,
  
  init() {
    this.createOverlay();
    this.setupTriggers();
    this.setupKeyboardNavigation();
    console.log('🖼️ Lightbox initialized');
  },
  
  /**
   * Crea el overlay del lightbox
   */
  createOverlay() {
    this.overlay = document.createElement('div');
    this.overlay.className = 'lightbox-overlay';
    this.overlay.innerHTML = `
      <div class="lightbox-content">
        <img src="" alt="" class="lightbox-image">
        <button class="lightbox-close" aria-label="Cerrar">&times;</button>
        <button class="lightbox-nav lightbox-prev" aria-label="Anterior">‹</button>
        <button class="lightbox-nav lightbox-next" aria-label="Siguiente">›</button>
        <div class="lightbox-counter"></div>
      </div>
    `;
    
    document.body.appendChild(this.overlay);
    
    // Event listeners
    this.overlay.querySelector('.lightbox-close').addEventListener('click', () => this.close());
    this.overlay.querySelector('.lightbox-prev').addEventListener('click', () => this.prev());
    this.overlay.querySelector('.lightbox-next').addEventListener('click', () => this.next());
    
    // Cerrar al hacer clic en el overlay (no en la imagen)
    this.overlay.addEventListener('click', (e) => {
      if (e.target === this.overlay) {
        this.close();
      }
    });
  },
  
  /**
   * Configura los elementos que activan el lightbox
   */
  setupTriggers() {
    document.querySelectorAll('[data-lightbox]').forEach((trigger, index) => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const gallery = trigger.dataset.lightbox || 'default';
        this.open(gallery, index);
      });
    });
  },
  
  /**
   * Abre el lightbox
   */
  open(gallery = 'default', startIndex = 0) {
    // Recopilar todas las imágenes de la galería
    this.images = Array.from(document.querySelectorAll(`[data-lightbox="${gallery}"]`))
      .map(el => ({
        src: el.href || el.dataset.src || el.src,
        alt: el.alt || el.dataset.alt || '',
        caption: el.dataset.caption || ''
      }));
    
    if (this.images.length === 0) return;
    
    this.currentIndex = startIndex;
    this.updateImage();
    this.overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Ocultar navegación si solo hay una imagen
    if (this.images.length === 1) {
      this.overlay.querySelector('.lightbox-prev').style.display = 'none';
      this.overlay.querySelector('.lightbox-next').style.display = 'none';
    } else {
      this.overlay.querySelector('.lightbox-prev').style.display = 'flex';
      this.overlay.querySelector('.lightbox-next').style.display = 'flex';
    }
  },
  
  /**
   * Cierra el lightbox
   */
  close() {
    this.overlay.classList.remove('active');
    document.body.style.overflow = '';
    
    // Limpiar después de la animación
    setTimeout(() => {
      this.currentIndex = 0;
      this.images = [];
    }, 300);
  },
  
  /**
   * Navega a la imagen anterior
   */
  prev() {
    this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
    this.updateImage();
  },
  
  /**
   * Navega a la imagen siguiente
   */
  next() {
    this.currentIndex = (this.currentIndex + 1) % this.images.length;
    this.updateImage();
  },
  
  /**
   * Actualiza la imagen mostrada
   */
  updateImage() {
    const image = this.images[this.currentIndex];
    const imgElement = this.overlay.querySelector('.lightbox-image');
    const counter = this.overlay.querySelector('.lightbox-counter');
    
    // Fade out
    imgElement.style.opacity = '0';
    
    setTimeout(() => {
      imgElement.src = image.src;
      imgElement.alt = image.alt;
      
      // Fade in cuando se carga
      imgElement.onload = () => {
        imgElement.style.opacity = '1';
      };
      
      // Actualizar contador
      counter.textContent = `${this.currentIndex + 1} / ${this.images.length}`;
    }, 150);
  },
  
  /**
   * Configura navegación por teclado
   */
  setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
      if (!this.overlay.classList.contains('active')) return;
      
      switch(e.key) {
        case 'Escape':
          this.close();
          break;
        case 'ArrowLeft':
          this.prev();
          break;
        case 'ArrowRight':
          this.next();
          break;
      }
    });
  },
  
  /**
   * Abre lightbox con una imagen específica
   */
  openImage(src, alt = '', caption = '') {
    this.images = [{ src, alt, caption }];
    this.currentIndex = 0;
    this.updateImage();
    this.overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Ocultar navegación
    this.overlay.querySelector('.lightbox-prev').style.display = 'none';
    this.overlay.querySelector('.lightbox-next').style.display = 'none';
  }
};

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Lightbox.init());
} else {
  Lightbox.init();
}

// Exportar para uso global
window.Lightbox = Lightbox;