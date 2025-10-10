/**
 * VULCANO - Gestión de Tema Claro/Oscuro
 * Persistencia en localStorage y sincronización
 */

'use strict';

const ThemeManager = {
  storageKey: 'vulcano-theme',
  
  init() {
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
      this.setTheme(savedTheme);
    } else {
      // Detectar preferencia del sistema
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      this.setTheme(prefersDark ? 'dark' : 'light');
    }
  },
  
  /**
   * Establece el tema activo
   */
  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.storageKey, theme);
    this.updateToggleButton(theme);
    
    // Disparar evento personalizado
    window.dispatchEvent(new CustomEvent('themeChange', { detail: { theme } }));
  },
  
  /**
   * Alterna entre tema claro y oscuro
   */
  toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
    
    // Animación suave
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    setTimeout(() => {
      document.body.style.transition = '';
    }, 300);
  },
  
  /**
   * Configura el botón de toggle
   */
  setupToggle() {
    const toggleButtons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
    
    toggleButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.toggleTheme();
        
        // Animación del botón
        button.style.transform = 'rotate(360deg)';
        setTimeout(() => {
          button.style.transform = '';
        }, 300);
      });
    });
  },
  
  /**
   * Actualiza el icono del botón según el tema
   */
  updateToggleButton(theme) {
    const buttons = document.querySelectorAll('.theme-toggle, [data-theme-toggle]');
    
    buttons.forEach(button => {
      const icon = button.querySelector('.theme-icon');
      if (icon) {
        icon.textContent = theme === 'light' ? '🌙' : '☀️';
      }
      
      button.setAttribute('aria-label', 
        theme === 'light' ? 'Activar modo oscuro' : 'Activar modo claro'
      );
      button.setAttribute('title',
        theme === 'light' ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'
      );
    });
  },
  
  /**
   * Observa cambios en la preferencia del sistema
   */
  watchSystemPreference() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    mediaQuery.addEventListener('change', (e) => {
      // Solo cambiar si no hay preferencia guardada explícitamente
      const hasSavedPreference = localStorage.getItem(this.storageKey);
      if (!hasSavedPreference) {
        this.setTheme(e.matches ? 'dark' : 'light');
      }
    });
  },
  
  /**
   * Obtiene el tema actual
   */
  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  },
  
  /**
   * Fuerza un tema específico
   */
  forceTheme(theme) {
    if (theme === 'light' || theme === 'dark') {
      this.setTheme(theme);
    }
  },
  
  /**
   * Resetea a la preferencia del sistema
   */
  resetToSystemPreference() {
    localStorage.removeItem(this.storageKey);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.setTheme(prefersDark ? 'dark' : 'light');
  }
};

// Inicializar inmediatamente para evitar flash
ThemeManager.init();

// Exportar para uso global
window.ThemeManager = ThemeManager;