/**
 * VULCANO - JavaScript Principal
 * Funcionalidades globales, utilidades y manejo de interacciones
 */

'use strict';

// ========== CONFIGURACIÓN GLOBAL ==========
const VulcanoApp = {
  config: {
    animationDuration: 300,
    debounceDelay: 300,
    lazyLoadOffset: 200,
  },
  
  init() {
    this.setupNavigation();
    this.setupForms();
    this.setupAlerts();
    this.setupLazyLoading();
    this.setupTooltips();
    this.setupSmoothScroll();
    this.setupImagePreview();
    this.setupConfirmDialogs();
    this.setupAjaxActions();
    console.log('✅ Vulcano App initialized');
  }
};

// ========== NAVEGACIÓN ==========
VulcanoApp.setupNavigation = function() {
  // Toggle sidebar en móvil
  const sidebarToggle = document.querySelector('.sidebar-toggle');
  const sidebar = document.querySelector('.dashboard-sidebar');
  const mainContent = document.querySelector('.dashboard-main');
  
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('active');
      mainContent?.classList.toggle('expanded');
    });
    
    // Cerrar sidebar al hacer clic fuera en móvil
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 1024 && 
          !sidebar.contains(e.target) && 
          !sidebarToggle.contains(e.target) &&
          sidebar.classList.contains('active')) {
        sidebar.classList.remove('active');
        mainContent?.classList.remove('expanded');
      }
    });
  }
  
  // Marcar enlace activo en navegación
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link-dashboard, .nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
};

// ========== FORMULARIOS ==========
VulcanoApp.setupForms = function() {
  // Validación en tiempo real
  const forms = document.querySelectorAll('form[data-validate="true"]');
  forms.forEach(form => {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      input.addEventListener('blur', () => {
        this.validateField(input);
      });
      
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
        this.showToast('Por favor, corrige los errores en el formulario', 'error');
      } else {
        // Deshabilitar botón de envío para evitar doble submit
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.classList.add('loading');
        }
      }
    });
  });
  
  // Auto-resize de textareas
  document.querySelectorAll('textarea[data-autoresize="true"]').forEach(textarea => {
    textarea.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    });
  });
};

VulcanoApp.validateField = function(field) {
  const value = field.value.trim();
  const type = field.type;
  const required = field.hasAttribute('required');
  let isValid = true;
  let errorMessage = '';
  
  // Validar campo requerido
  if (required && !value) {
    isValid = false;
    errorMessage = 'Este campo es obligatorio';
  }
  
  // Validar email
  if (type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      isValid = false;
      errorMessage = 'Ingresa un email válido';
    }
  }
  
  // Validar longitud mínima
  const minLength = field.getAttribute('minlength');
  if (minLength && value.length < parseInt(minLength)) {
    isValid = false;
    errorMessage = `Mínimo ${minLength} caracteres`;
  }
  
  // Validar contraseñas coincidentes
  if (field.name === 'password2' || field.name === 'confirm_password') {
    const password1 = document.querySelector('input[name="password1"], input[name="password"]');
    if (password1 && value !== password1.value) {
      isValid = false;
      errorMessage = 'Las contraseñas no coinciden';
    }
  }
  
  // Aplicar clases de validación
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

// ========== ALERTAS Y TOASTS ==========
VulcanoApp.setupAlerts = function() {
  // Auto-cerrar alertas después de 5 segundos
  document.querySelectorAll('.alert[data-auto-dismiss="true"]').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });
  
  // Botones de cerrar alertas
  document.querySelectorAll('.alert .btn-close').forEach(btn => {
    btn.addEventListener('click', function() {
      const alert = this.closest('.alert');
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    });
  });
};

VulcanoApp.showToast = function(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast-notification toast-${type}`;
  toast.innerHTML = `
    <div class="toast-content">
      <span class="toast-icon">${this.getToastIcon(type)}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close">&times;</button>
    </div>
  `;
  
  // Estilos inline para el toast
  Object.assign(toast.style, {
    position: 'fixed',
    top: '20px',
    right: '20px',
    zIndex: '9999',
    padding: '16px 24px',
    borderRadius: '12px',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
    backgroundColor: type === 'success' ? '#10b981' : 
                     type === 'error' ? '#ef4444' : 
                     type === 'warning' ? '#f59e0b' : '#3b82f6',
    color: 'white',
    fontWeight: '500',
    animation: 'slideInRight 0.3s ease-out',
    maxWidth: '400px'
  });
  
  document.body.appendChild(toast);
  
  // Cerrar toast
  const closeToast = () => {
    toast.style.animation = 'slideOutRight 0.3s ease-out';
    setTimeout(() => toast.remove(), 300);
  };
  
  toast.querySelector('.toast-close').addEventListener('click', closeToast);
  
  if (duration > 0) {
    setTimeout(closeToast, duration);
  }
};

VulcanoApp.getToastIcon = function(type) {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };
  return icons[type] || icons.info;
};

// ========== LAZY LOADING DE IMÁGENES ==========
VulcanoApp.setupLazyLoading = function() {
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        const src = img.dataset.src;
        
        if (src) {
          img.src = src;
          img.classList.add('loaded');
          img.removeAttribute('data-src');
          observer.unobserve(img);
        }
      }
    });
  }, {
    rootMargin: `${this.config.lazyLoadOffset}px`
  });
  
  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });
};

// ========== TOOLTIPS ==========
VulcanoApp.setupTooltips = function() {
  document.querySelectorAll('[data-tooltip]').forEach(element => {
    element.addEventListener('mouseenter', function(e) {
      const tooltipText = this.dataset.tooltip;
      const tooltip = document.createElement('div');
      tooltip.className = 'tooltip-custom';
      tooltip.textContent = tooltipText;
      
      Object.assign(tooltip.style, {
        position: 'absolute',
        background: '#1a1a1a',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '6px',
        fontSize: '14px',
        zIndex: '10000',
        pointerEvents: 'none',
        whiteSpace: 'nowrap',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      });
      
      document.body.appendChild(tooltip);
      
      const rect = this.getBoundingClientRect();
      tooltip.style.top = (rect.top - tooltip.offsetHeight - 8) + 'px';
      tooltip.style.left = (rect.left + (rect.width - tooltip.offsetWidth) / 2) + 'px';
      
      this.tooltipElement = tooltip;
    });
    
    element.addEventListener('mouseleave', function() {
      if (this.tooltipElement) {
        this.tooltipElement.remove();
        this.tooltipElement = null;
      }
    });
  });
};

// ========== SMOOTH SCROLL ==========
VulcanoApp.setupSmoothScroll = function() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;
      
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
};

// ========== PREVIEW DE IMÁGENES ==========
VulcanoApp.setupImagePreview = function() {
  const fileInputs = document.querySelectorAll('input[type="file"][data-preview="true"]');
  
  fileInputs.forEach(input => {
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
            div.className = 'image-preview-item';
            div.innerHTML = `
              <img src="${e.target.result}" class="image-preview-img" alt="Preview ${index + 1}">
              <button type="button" class="image-preview-remove" data-index="${index}">
                <span>&times;</span>
              </button>
            `;
            
            previewContainer.appendChild(div);
            
            // Botón para eliminar preview
            div.querySelector('.image-preview-remove').addEventListener('click', function() {
              div.remove();
            });
          };
          
          reader.readAsDataURL(file);
        }
      });
    });
  });
  
  // Drag and drop para subida de imágenes
  const dropZones = document.querySelectorAll('.image-upload-area');
  dropZones.forEach(zone => {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      zone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }
    
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

// ========== DIÁLOGOS DE CONFIRMACIÓN ==========
VulcanoApp.setupConfirmDialogs = function() {
  document.querySelectorAll('[data-confirm]').forEach(element => {
    element.addEventListener('click', function(e) {
      const message = this.dataset.confirm || '¿Estás seguro de realizar esta acción?';
      if (!confirm(message)) {
        e.preventDefault();
        return false;
      }
    });
  });
};

// ========== ACCIONES AJAX ==========
VulcanoApp.setupAjaxActions = function() {
  // Marcar mensaje como leído
  document.querySelectorAll('[data-action="mark-read"]').forEach(btn => {
    btn.addEventListener('click', async function() {
      const messageId = this.dataset.messageId;
      try {
        const response = await fetch(`/ajax/mensaje/${messageId}/marcar-leido/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': VulcanoApp.getCsrfToken(),
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          this.closest('.message-item')?.classList.add('read');
          VulcanoApp.showToast('Mensaje marcado como leído', 'success');
        }
      } catch (error) {
        console.error('Error:', error);
        VulcanoApp.showToast('Error al marcar mensaje', 'error');
      }
    });
  });
  
  // Toggle proyecto destacado
  document.querySelectorAll('[data-action="toggle-featured"]').forEach(btn => {
    btn.addEventListener('click', async function() {
      const projectId = this.dataset.projectId;
      try {
        const response = await fetch(`/ajax/proyecto/${projectId}/destacar/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': VulcanoApp.getCsrfToken(),
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        
        if (data.success) {
          this.textContent = data.is_featured ? 'Quitar destacado' : 'Destacar';
          VulcanoApp.showToast(
            data.is_featured ? 'Proyecto destacado' : 'Proyecto sin destacar',
            'success'
          );
        }
      } catch (error) {
        console.error('Error:', error);
        VulcanoApp.showToast('Error al actualizar proyecto', 'error');
      }
    });
  });
};

// ========== UTILIDADES ==========
VulcanoApp.getCsrfToken = function() {
  return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
};

VulcanoApp.debounce = function(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

VulcanoApp.formatNumber = function(num) {
  return new Intl.NumberFormat('es-MX').format(num);
};

VulcanoApp.formatCurrency = function(amount) {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN'
  }).format(amount);
};

VulcanoApp.formatDate = function(date) {
  return new Intl.DateTimeFormat('es-MX', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(new Date(date));
};

// ========== INICIALIZACIÓN ==========
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => VulcanoApp.init());
} else {
  VulcanoApp.init();
}

// Exportar para uso global
window.VulcanoApp = VulcanoApp;