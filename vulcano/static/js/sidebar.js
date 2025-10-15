/**
 * VULCANO - Gestión del Sidebar
 * Toggle, colapso y persistencia de estado
 */

'use strict';

const SidebarManager = {
  storageKey: 'vulcano-sidebar-collapsed',
  initialized: false,
  sidebar: null,
  toggle: null,
  mainContent: null,
  
  init() {
    if (this.initialized) return;
    this.initialized = true;
    
    this.sidebar = document.getElementById('sidebar') || document.querySelector('.dashboard-sidebar');
    this.toggle = document.getElementById('sidebarToggle') || document.querySelector('.sidebar-toggle');
    this.mainContent = document.getElementById('main-content') || document.querySelector('.dashboard-main');
    
    if (!this.sidebar || !this.toggle) {
      console.log('ℹ️ Sidebar not found, skipping initialization');
      return;
    }
    
    this.loadState();
    this.setupToggle();
    this.setupTooltips();
    this.handleResize();
    
    console.log('📂 Sidebar Manager initialized');
  },
  
  /**
   * Carga el estado guardado del sidebar
   */
  loadState() {
    const isCollapsed = localStorage.getItem(this.storageKey) === 'true';
    const isMobile = window.innerWidth <= 1024;
    
    if (isCollapsed && !isMobile) {
      this.sidebar.classList.add('collapsed');
      document.body.classList.add('sidebar-collapsed');
      
      if (this.mainContent) {
        this.mainContent.classList.add('expanded');
      }
      
      this.updateToggleIcon(true);
      this.updateAriaState(false);
    } else {
      this.updateAriaState(true);
    }
  },
  
  /**
   * Configura el toggle del sidebar
   */
  setupToggle() {
    if (this.toggle.dataset.sidebarListenerAdded) return;
    this.toggle.dataset.sidebarListenerAdded = 'true';
    
    this.toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggleSidebar();
    });
    
    // Cerrar sidebar en móvil al hacer clic fuera
    document.addEventListener('click', (e) => {
      const isMobile = window.innerWidth <= 1024;
      if (isMobile && 
          this.sidebar.classList.contains('active') &&
          !this.sidebar.contains(e.target) && 
          !this.toggle.contains(e.target)) {
        this.closeSidebar();
      }
    });
    
    // Cerrar con ESC en móvil
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.sidebar.classList.contains('active')) {
        this.closeSidebar();
        this.toggle.focus();
      }
    });
  },
  
  /**
   * Alterna el estado del sidebar
   */
  toggleSidebar() {
    const isMobile = window.innerWidth <= 1024;
    
    if (isMobile) {
      // En móvil: mostrar/ocultar con clase active
      this.sidebar.classList.toggle('active');
      const isOpen = this.sidebar.classList.contains('active');
      this.updateAriaState(isOpen);
      this.updateToggleIcon(false);
    } else {
      // En desktop: colapsar/expandir
      const isCollapsed = this.sidebar.classList.toggle('collapsed');
      
      // 🔥 Sincronizar con body y main-content
      document.body.classList.toggle('sidebar-collapsed', isCollapsed);
      
      if (this.mainContent) {
        this.mainContent.classList.toggle('expanded', isCollapsed);
      }
      
      localStorage.setItem(this.storageKey, String(isCollapsed));
      this.updateToggleIcon(isCollapsed);
      this.updateAriaState(!isCollapsed);
    }
  },
  
  /**
   * Cierra el sidebar (solo móvil)
   */
  closeSidebar() {
    this.sidebar.classList.remove('active');
    this.updateAriaState(false);
  },
  
  /**
   * Actualiza el ícono del toggle
   */
  updateToggleIcon(isCollapsed) {
    const icon = this.toggle.querySelector('i');
    if (!icon) return;
    
    const isMobile = window.innerWidth <= 1024;
    const isActive = this.sidebar.classList.contains('active');
    
    if (isMobile) {
      icon.className = isActive ? 'bi bi-x' : 'bi bi-list';
    } else {
      icon.className = 'bi bi-list';
    }
  },
  
  /**
   * Actualiza atributos ARIA
   */
  updateAriaState(isExpanded) {
    this.toggle.setAttribute('aria-expanded', String(isExpanded));
    this.sidebar.setAttribute('aria-hidden', String(!isExpanded));
  },
  
  /**
   * Configura tooltips para links cuando está colapsado
   */
  setupTooltips() {
    const navLinks = this.sidebar.querySelectorAll('.nav-link-dashboard');
    navLinks.forEach(link => {
      const textEl = link.querySelector('.nav-text');
      if (textEl) {
        const text = textEl.textContent.trim();
        link.setAttribute('data-tooltip', text);
        link.setAttribute('title', text);
      }
    });
  },
  
  /**
   * Maneja cambios de tamaño de ventana
   */
  handleResize() {
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        const isMobile = window.innerWidth <= 1024;
        
        if (isMobile) {
          // En móvil: limpiar estados de desktop
          this.sidebar.classList.remove('collapsed');
          document.body.classList.remove('sidebar-collapsed');
          
          if (this.mainContent) {
            this.mainContent.classList.remove('expanded');
          }
          
          if (!this.sidebar.classList.contains('active')) {
            this.updateAriaState(false);
          }
        } else {
          // En desktop: limpiar estados de móvil y restaurar
          this.sidebar.classList.remove('active');
          
          if (this.mainContent) {
            this.mainContent.classList.remove('expanded');
          }
          
          this.loadState();
        }
        
        this.updateToggleIcon(this.sidebar.classList.contains('collapsed'));
      }, 250);
    });
  }
};

// Inicializar
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => SidebarManager.init());
} else {
  SidebarManager.init();
}

window.SidebarManager = SidebarManager;