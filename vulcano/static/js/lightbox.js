/**
 * VULCANO - Lightbox para Galería de Imágenes
 * Visualización modal con navegación y accesibilidad
 */

'use strict';

const Lightbox = {
  currentIndex: 0,
  images: [],
  overlay: null,
  initialized: false,
  
  init() {
    if (this.initialized) return;
    this.initialized = true;
    
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
    this.overlay.setAttribute('role', 'dialog');
    this.overlay.setAttribute('aria-modal', 'true');
    this.overlay.setAttribute('aria-label', 'Galería de imágenes');
    
    this.overlay.innerHTML = `
      <div class="lightbox-content">
        <img src="" alt="" class="lightbox-image">
        <button class="lightbox-close" aria-label="Cerrar galería">
          <i class="bi bi-x" aria-hidden="true"></i>
        </button>
        <button class="lightbox-nav lightbox-prev" aria-label="Imagen anterior">
          <i class="bi bi-chevron-left" aria-hidden="true"></i>
        </button>
        <button class="lightbox-nav lightbox-next" aria-label="Imagen siguiente">
          <i class="bi bi-chevron-right" aria-hidden="true"></i>
        </button>
        <div class="lightbox-counter" aria-live="polite" aria-atomic="true"></div>
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
      if (trigger.dataset.lightboxAdded) return;
      trigger.dataset.lightboxAdded = 'true';
      
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const gallery = trigger.dataset.lightbox || 'default';
        this.open(gallery, index);
      });
      
      // Accesibilidad: permitir Enter/Space
      if (trigger.tagName !== 'A' && trigger.tagName !== 'BUTTON') {
        trigger.setAttribute('role', 'button');
        trigger.setAttribute('tabindex', '0');
        
        trigger.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            const gallery = trigger.dataset.lightbox || 'default';
            this.open(gallery, index);
          }
        });
      }
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
    
    // Mostrar overlay
    this.overlay.classList.add('active');
    this.overlay.removeAttribute('aria-hidden');
    
    // Bloquear scroll del body
    document.body.style.overflow = 'hidden';
    
    // Guardar el elemento con foco para restaurarlo al cerrar
    this.previousFocus = document.activeElement;
    
    // Enfocar el botón de cerrar
    setTimeout(() => {
      this.overlay.querySelector('.lightbox-close').focus();
    }, 100);
    
    // Ocultar navegación si solo hay una imagen
    const prevBtn = this.overlay.querySelector('.lightbox-prev');
    const nextBtn = this.overlay.querySelector('.lightbox-next');
    
    if (this.images.length === 1) {
      prevBtn.style.display = 'none';
      nextBtn.style.display = 'none';
    } else {
      prevBtn.style.display = 'flex';
      nextBtn.style.display = 'flex';
    }
  },
  
  /**
   * Cierra el lightbox
   */
  close() {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    this.overlay.classList.remove('active');
    this.overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    
    // Restaurar foco
    if (this.previousFocus) {
      this.previousFocus.focus();
      this.previousFocus = null;
    }
    
    // Limpiar después de la animación
    const cleanupDelay = reducedMotion ? 0 : 300;
    setTimeout(() => {
      this.currentIndex = 0;
      this.images = [];
    }, cleanupDelay);
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
    
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    // Fade out
    if (!reducedMotion) {
      imgElement.style.opacity = '0';
    }
    
    const transitionDelay = reducedMotion ? 0 : 150;
    
    setTimeout(() => {
      imgElement.src = image.src;
      imgElement.alt = image.alt || `Imagen ${this.currentIndex + 1} de ${this.images.length}`;
      
      // Fade in cuando se carga
      imgElement.onload = () => {
        if (!reducedMotion) {
          imgElement.style.opacity = '1';
        }
      };
      
      // Actualizar contador
      counter.textContent = `${this.currentIndex + 1} / ${this.images.length}`;
      
      // Anunciar a lectores de pantalla
      counter.setAttribute('aria-label', `Imagen ${this.currentIndex + 1} de ${this.images.length}`);
    }, transitionDelay);
  },
  
  /**
   * Configura navegación por teclado
   */
  setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
      if (!this.overlay.classList.contains('active')) return;
      
      switch(e.key) {
        case 'Escape':
          e.preventDefault();
          this.close();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          this.prev();
          break;
        case 'ArrowRight':
          e.preventDefault();
          this.next();
          break;
        case 'Home':
          e.preventDefault();
          this.currentIndex = 0;
          this.updateImage();
          break;
        case 'End':
          e.preventDefault();
          this.currentIndex = this.images.length - 1;
          this.updateImage();
          break;
      }
    });
  },
  
  /**
   * Abre lightbox con una imagen específica (API pública)
   */
  openImage(src, alt = '', caption = '') {
    this.images = [{ src, alt, caption }];
    this.currentIndex = 0;
    this.updateImage();
    this.overlay.classList.add('active');
    this.overlay.removeAttribute('aria-hidden');
    document.body.style.overflow = 'hidden';
    
    // Ocultar navegación
    this.overlay.querySelector('.lightbox-prev').style.display = 'none';
    this.overlay.querySelector('.lightbox-next').style.display = 'none';
    
    // Guardar y enfocar
    this.previousFocus = document.activeElement;
    setTimeout(() => {
      this.overlay.querySelector('.lightbox-close').focus();
    }, 100);
  }
};

// Inicializar
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Lightbox.init());
} else {
  Lightbox.init();
}

window.Lightbox = Lightbox;