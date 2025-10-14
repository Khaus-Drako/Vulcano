/**
 * VULCANO - Gestión de Tema Claro/Oscuro
 * Sincronizado con Bootstrap 5 y preferencias del sistema
 */

'use strict';

const ThemeManager = {
  storageKey: 'vulcano-theme',
  initialized: false,
  
  init() {
    if (this.initialized) return;
    this.initialized = true;
    
    this.loadTheme();
    this.setupToggle();
    this.watchSystemPreference();
    console.log('🎨 Theme Manager initialized');
  },
  
  /**
   * Carga el tema guardado o detecta preferencia del sistema
   */
  loadTheme() {
    const savedTheme = localStorage.getItem(this.storageKey);
    
    if (savedTheme) {
      this.setTheme(savedTheme, false);
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light', false);
    }
  },
  
  /**
   * Establece el tema activo
   * @param {string} theme - 'light' o 'dark'
   * @param {boolean} animate - Si se debe animar la transición
   */
  setTheme(theme, animate = true) {
    const root = document.documentElement;
    const validTheme = theme === 'dark' ? 'dark' : 'light';
    
    // Aplicar a HTML
    root.setAttribute('data-theme', validTheme);
    root.setAttribute('data-bs-theme', validTheme); // Bootstrap 5.3+
    
    // Guardar preferencia
    localStorage.setItem(this.storageKey, validTheme);
    
    // Actualizar UI
    this.updateToggleButton(validTheme);
    
    // Animación suave
    if (animate && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
      setTimeout(() => {
        document.body.style.transition = '';
      }, 300);
    }
    
    // Evento personalizado
    window.dispatchEvent(new CustomEvent('themeChange', { 
      detail: { theme: validTheme } 
    }));
  },
  
  /**
   * Alterna entre tema claro y oscuro
   */
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme, true);
  },
  
  /**
   * Configura el botón de toggle
   */
  setupToggle() {
    const toggleButtons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
    
    toggleButtons.forEach(button => {
      // Evitar múltiples listeners
      if (button.dataset.themeListenerAdded) return;
      button.dataset.themeListenerAdded = 'true';
      
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleTheme();
        
        // Animación del botón (solo si no hay preferencia de movimiento reducido)
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          button.style.transition = 'transform 0.3s ease';
          button.style.transform = 'rotate(360deg)';
          setTimeout(() => {
            button.style.transform = '';
            setTimeout(() => {
              button.style.transition = '';
            }, 300);
          }, 300);
        }
      });
    });
  },
  
  /**
   * Actualiza el icono del botón según el tema
   */
  updateToggleButton(theme) {
    const buttons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
    const isDark = theme === 'dark';
    
    buttons.forEach(button => {
      const icon = button.querySelector('.theme-icon');
      if (icon) {
        icon.textContent = isDark ? '☀️' : '🌙';
      }
      
      const label = isDark ? 'Activar modo claro' : 'Activar modo oscuro';
      button.setAttribute('aria-label', label);
      button.setAttribute('title', label);
      button.setAttribute('aria-pressed', String(isDark));
    });
  },
  
  /**
   * Observa cambios en la preferencia del sistema
   */
  watchSystemPreference() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Listener moderno
    const handleChange = (e) => {
      const hasSavedPreference = localStorage.getItem(this.storageKey);
      if (!hasSavedPreference) {
        this.setTheme(e.matches ? 'dark' : 'light', true);
      }
    };
    
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      // Fallback para navegadores antiguos
      mediaQuery.addListener(handleChange);
    }
  },
  
  /**
   * Obtiene el tema actual
   */
  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  },
  
  /**
   * Fuerza un tema específico (útil para preview)
   */
  forceTheme(theme) {
    if (theme === 'light' || theme === 'dark') {
      this.setTheme(theme, true);
    }
  },
  
  /**
   * Resetea a la preferencia del sistema
   */
  resetToSystemPreference() {
    localStorage.removeItem(this.storageKey);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.setTheme(prefersDark ? 'dark' : 'light', true);
  }
};

// Inicialización temprana para evitar flash
(function() {
  const savedTheme = localStorage.getItem('vulcano-theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = prefersDark ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-bs-theme', theme);
  }
})();

// Inicializar cuando esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
  ThemeManager.init();
}

// Exportar
window.ThemeManager = ThemeManager;