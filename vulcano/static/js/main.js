/**
 * VULCANO - JavaScript Principal
 * Funcionalidades globales (sin manejar sidebar, ya lo hace sidebar.js)
 */

'use strict';

const VulcanoApp = {
  config: {
    animationDuration: 300,
    debounceDelay: 300,
    lazyLoadOffset: 200,
    toastDuration: 5000,
  },
  initialized: false,
  
  init() {
    if (this.initialized) return;
    this.initialized = true;
    
    // Quitar clase no-js
    document.documentElement.classList.remove('no-js');
    document.documentElement.classList.add('js');
    
    this.setupForms();
    this.setupAlerts();
    this.setupLazyLoading();
    this.setupTooltips();
    this.setupSmoothScroll();
    this.setupImagePreview();
    this.setupConfirmDialogs();
    this.setupScrollToTop();
    this.setupActiveLinks();
    
    console.log('✅ Vulcano App initialized');
  }
};

// ========== FORMULARIOS ==========
VulcanoApp.setupForms = function() {
  const forms = document.querySelectorAll('form[data-validate="true"]');
  
  forms.forEach(form => {
    if (form.dataset.validationAdded) return;
    form.dataset.validationAdded = 'true';
    
    const inputs = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
    
    inputs.forEach(input => {
      input.addEventListener('blur', () => this.validateField(input));
      
      input.addEventListener('input', () => {
        if (input.classList.contains('is-invalid')) {
          this.validateField(input);
        }
      });
    });
    
    form.addEventListener('submit', (e) => {
      let isValid = true;
      inputs.forEach(input => {
        if (!this.validateField(input)) {
          isValid = false;
        }
      });
      
      if (!isValid) {
        e.preventDefault();
        const firstInvalid = form.querySelector('.is-invalid');
        firstInvalid?.focus();
        this.showToast('Por favor, corrige los errores en el formulario', 'error');
        return false;
      }
      
      // Deshabilitar botón submit
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        
        // Re-habilitar después de 3 segundos (fallback)
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.classList.remove('loading');
        }, 3000);
      }
    });
  });
  
  // Auto-resize textareas
  document.querySelectorAll('textarea[data-autoresize="true"]').forEach(textarea => {
    const resize = () => {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    };
    
    textarea.addEventListener('input', resize);
    resize(); // Inicial
  });
};

VulcanoApp.validateField = function(field) {
  const value = field.value.trim();
  const type = field.type;
  const required = field.hasAttribute('required');
  let isValid = true;
  let errorMessage = '';
  
  if (required && !value) {
    isValid = false;
    errorMessage = 'Este campo es obligatorio';
  } else if (type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      isValid = false;
      errorMessage = 'Ingresa un correo válido';
    }
  } else if (field.hasAttribute('minlength') && value) {
    const minLength = parseInt(field.getAttribute('minlength'));
    if (value.length < minLength) {
      isValid = false;
      errorMessage = `Mínimo ${minLength} caracteres`;
    }
  } else if ((field.name === 'password2' || field.name === 'confirm_password') && value) {
    const password1 = document.querySelector('input[name="password1"], input[name="password"]');
    if (password1 && value !== password1.value) {
      isValid = false;
      errorMessage = 'Las contraseñas no coinciden';
    }
  }
  
  if (isValid) {
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
    this.hideFieldError(field);
  } else {
    field.classList.remove('is-valid');
    field.classList.add('is-invalid');
    this.showFieldError(field, errorMessage);
  }
  
  return isValid;
};

VulcanoApp.showFieldError = function(field, message) {
  let errorDiv = field.parentElement.querySelector('.invalid-feedback');
  if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    field.parentElement.appendChild(errorDiv);
  }
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
};

VulcanoApp.hideFieldError = function(field) {
  const errorDiv = field.parentElement.querySelector('.invalid-feedback');
  if (errorDiv) {
    errorDiv.style.display = 'none';
  }
};

// ========== ALERTAS ==========
VulcanoApp.setupAlerts = function() {
  document.querySelectorAll('.alert[data-auto-dismiss="true"]').forEach(alert => {
    if (alert.dataset.dismissTimerSet) return;
    alert.dataset.dismissTimerSet = 'true';
    
    const dismissAlert = () => {
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    };
    
    // Auto-cerrar después de 5 segundos si no está en hover/focus
    const timer = setTimeout(() => {
      if (!alert.matches(':hover, :focus-within')) {
        dismissAlert();
      }
    }, this.config.toastDuration);
    
    // Cancelar si interactúa
    alert.addEventListener('mouseenter', () => clearTimeout(timer), { once: true });
  });
};

VulcanoApp.showToast = function(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast-notification toast-${type}`;
  toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
  toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
  
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };
  
  toast.innerHTML = `
    <div class="d-flex align-items-center gap-2">
      <span aria-hidden="true">${icons[type] || icons.info}</span>
      <span>${message}</span>
      <button class="btn-close btn-close-white ms-auto" aria-label="Cerrar"></button>
    </div>
  `;
  
  Object.assign(toast.style, {
    position: 'fixed',
    top: '20px',
    right: '20px',
    zIndex: '9999',
    padding: '12px 20px',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    backgroundColor: type === 'success' ? '#10b981' : 
                     type === 'error' ? '#ef4444' : 
                     type === 'warning' ? '#f59e0b' : '#3b82f6',
    color: 'white',
    fontWeight: '500',
    maxWidth: '400px',
    animation: 'slideInRight 0.3s ease-out'
  });
  
  document.body.appendChild(toast);
  
  const closeToast = () => {
    toast.style.animation = 'slideOutRight 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  };
  
  toast.querySelector('.btn-close').addEventListener('click', closeToast);
  
  if (duration > 0) {
    setTimeout(closeToast, duration);
  }
};

// ========== LAZY LOADING ==========
VulcanoApp.setupLazyLoading = function() {
  if (!('IntersectionObserver' in window)) return;
  
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.dataset.src;
        
        if (src) {
          img.src = src;
          img.classList.add('loaded');
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      }
    });
  }, {
    rootMargin: `${this.config.lazyLoadOffset}px`
  });
  
  document.querySelectorAll('img[data-src]').forEach(img => imageObserver.observe(img));
};

// ========== TOOLTIPS ==========
VulcanoApp.setupTooltips = function() {
  // Inicializar tooltips de Bootstrap si está disponible
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      new bootstrap.Tooltip(el);
    });
  }
};

// ========== SMOOTH SCROLL ==========
VulcanoApp.setupSmoothScroll = function() {
  document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
    if (anchor.dataset.smoothScrollAdded) return;
    anchor.dataset.smoothScrollAdded = 'true';
    
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      const target = document.querySelector(targetId);
      
      if (target) {
        e.preventDefault();
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        target.scrollIntoView({
          behavior: reducedMotion ? 'auto' : 'smooth',
          block: 'start'
        });
        
        // Foco accesible
        if (target.tabIndex < 0) {
          target.tabIndex = -1;
        }
        target.focus();
      }
    });
  });
};

// ========== PREVIEW DE IMÁGENES ==========
VulcanoApp.setupImagePreview = function() {
  const fileInputs = document.querySelectorAll('input[type="file"][data-preview="true"]');
  
  fileInputs.forEach(input => {
    if (input.dataset.previewAdded) return;
    input.dataset.previewAdded = 'true';
    
    input.addEventListener('change', function(e) {
      const files = e.target.files;
      const previewContainer = document.querySelector(this.dataset.previewContainer || '#image-preview');
      
      if (!previewContainer) return;
      
      previewContainer.innerHTML = '';
      
      Array.from(files).forEach((file, index) => {
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          
          reader.onload = function(e) {
            const div = document.createElement('div');
            div.className = 'image-preview-item position-relative';
            div.innerHTML = `
              <img src="${e.target.result}" class="image-preview-img" alt="Vista previa ${index + 1}">
              <button type="button" class="image-preview-remove btn btn-danger btn-sm position-absolute top-0 end-0 m-2" 
                      data-index="${index}" aria-label="Eliminar imagen ${index + 1}">
                <i class="bi bi-x" aria-hidden="true"></i>
              </button>
            `;
            
            previewContainer.appendChild(div);
            
            div.querySelector('.image-preview-remove').addEventListener('click', function() {
              div.remove();
            });
          };
          
          reader.readAsDataURL(file);
        }
      });
    });
  });
  
  // Drag and drop
  const dropZones = document.querySelectorAll('.image-upload-area');
  dropZones.forEach(zone => {
    if (zone.dataset.dragDropAdded) return;
    zone.dataset.dragDropAdded = 'true';
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      zone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      }, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
      zone.addEventListener(eventName, () => zone.classList.add('dragover'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
      zone.addEventListener(eventName, () => zone.classList.remove('dragover'), false);
    });
    
    zone.addEventListener('drop', function(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      const input = this.querySelector('input[type="file"]');
      
      if (input) {
        input.files = files;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  });
};

// ========== CONFIRMACIÓN ==========
VulcanoApp.setupConfirmDialogs = function() {
  document.querySelectorAll('[data-confirm]').forEach(element => {
    if (element.dataset.confirmAdded) return;
    element.dataset.confirmAdded = 'true';
    
    element.addEventListener('click', function(e) {
      const message = this.dataset.confirm || '¿Estás seguro de realizar esta acción?';
      if (!confirm(message)) {
        e.preventDefault();
        return false;
      }
    });
  });
};

// ========== SCROLL TO TOP ==========
VulcanoApp.setupScrollToTop = function() {
  const scrollBtn = document.getElementById('scrollToTop');
  if (!scrollBtn) return;
  
  const toggleVisibility = () => {
    const shouldShow = window.pageYOffset > 300;
    scrollBtn.style.display = shouldShow ? 'block' : 'none';
    scrollBtn.setAttribute('aria-hidden', String(!shouldShow));
  };
  
  window.addEventListener('scroll', toggleVisibility, { passive: true });
  toggleVisibility();
  
  scrollBtn.addEventListener('click', () => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({
      top: 0,
      behavior: reducedMotion ? 'auto' : 'smooth'
    });
  });
};

// ========== ACTIVE LINKS ==========
VulcanoApp.setupActiveLinks = function() {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link-dashboard, .nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    }
  });
};

// ========== UTILIDADES ==========
VulcanoApp.getCsrfToken = function() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
};

VulcanoApp.debounce = function(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// ========== INICIALIZACIÓN ==========
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => VulcanoApp.init());
} else {
  VulcanoApp.init();
}

window.VulcanoApp = VulcanoApp;