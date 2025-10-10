/**
 * VULCANO - Filtros y Búsqueda de Proyectos
 * Filtrado dinámico, búsqueda y ordenamiento
 */

'use strict';

const ProjectFilters = {
  currentCategory: '',
  currentSearch: '',
  currentSort: '-created_at',
  
  init() {
    this.setupCategoryFilters();
    this.setupSearch();
    this.setupSortSelect();
    this.setupClearFilters();
    console.log('🔍 Project Filters initialized');
  },
  
  /**
   * Configura filtros de categoría
   */
  setupCategoryFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn[data-category]');
    
    filterButtons.forEach(button => {
      button.addEventListener('click', () => {
        // Actualizar estado activo
        filterButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Aplicar filtro
        this.currentCategory = button.dataset.category;
        this.applyFilters();
      });
    });
  },
  
  /**
   * Configura búsqueda con debounce
   */
  setupSearch() {
    const searchInput = document.querySelector('.search-input, [data-search]');
    
    if (searchInput) {
      const debouncedSearch = this.debounce((value) => {
        this.currentSearch = value;
        this.applyFilters();
      }, 300);
      
      searchInput.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
      });
      
      // Limpiar búsqueda
      const clearBtn = searchInput.parentElement.querySelector('.search-clear');
      if (clearBtn) {
        clearBtn.addEventListener('click', () => {
          searchInput.value = '';
          this.currentSearch = '';
          this.applyFilters();
        });
      }
    }
  },
  
  /**
   * Configura selector de ordenamiento
   */
  setupSortSelect() {
    const sortSelect = document.querySelector('.sort-select, [data-sort]');
    
    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        this.currentSort = e.target.value;
        this.applyFilters();
      });
    }
  },
  
  /**
   * Configura botón para limpiar filtros
   */
  setupClearFilters() {
    const clearButton = document.querySelector('[data-clear-filters]');
    
    if (clearButton) {
      clearButton.addEventListener('click', () => {
        this.clearAllFilters();
      });
    }
  },
  
  /**
   * Aplica filtros actuales
   */
  applyFilters() {
    const params = new URLSearchParams();
    
    if (this.currentCategory) {
      params.append('category', this.currentCategory);
    }
    
    if (this.currentSearch) {
      params.append('search', this.currentSearch);
    }
    
    if (this.currentSort && this.currentSort !== '-created_at') {
      params.append('sort', this.currentSort);
    }
    
    // Actualizar URL y recargar
    const url = params.toString() ? `?${params.toString()}` : window.location.pathname;
    window.location.href = url;
  },
  
  /**
   * Limpia todos los filtros
   */
  clearAllFilters() {
    this.currentCategory = '';
    this.currentSearch = '';
    this.currentSort = '-created_at';
    
    // Limpiar UI
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.filter-btn[data-category=""]').forEach(btn => btn.classList.add('active'));
    
    const searchInput = document.querySelector('.search-input, [data-search]');
    if (searchInput) searchInput.value = '';
    
    const sortSelect = document.querySelector('.sort-select, [data-sort]');
    if (sortSelect) sortSelect.value = '-created_at';
    
    // Aplicar
    this.applyFilters();
  },
  
  /**
   * Filtrado del lado del cliente (para resultados ya cargados)
   */
  filterClientSide() {
    const projectCards = document.querySelectorAll('.project-card');
    let visibleCount = 0;
    
    projectCards.forEach(card => {
      const category = card.dataset.category || '';
      const title = card.dataset.title?.toLowerCase() || '';
      const description = card.dataset.description?.toLowerCase() || '';
      const searchLower = this.currentSearch.toLowerCase();
      
      // Verificar categoría
      const categoryMatch = !this.currentCategory || category === this.currentCategory;
      
      // Verificar búsqueda
      const searchMatch = !this.currentSearch || 
                         title.includes(searchLower) || 
                         description.includes(searchLower);
      
      // Mostrar u ocultar
      if (categoryMatch && searchMatch) {
        card.style.display = '';
        card.style.animation = 'fadeInUp 0.4s ease-out';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });
    
    // Mostrar mensaje si no hay resultados
    this.updateEmptyState(visibleCount);
    
    // Ordenar si es necesario
    if (this.currentSort) {
      this.sortClientSide();
    }
  },
  
  /**
   * Ordenamiento del lado del cliente
   */
  sortClientSide() {
    const container = document.querySelector('.projects-grid');
    if (!container) return;
    
    const cards = Array.from(container.querySelectorAll('.project-card'))
      .filter(card => card.style.display !== 'none');
    
    cards.sort((a, b) => {
      let aValue, bValue;
      
      switch(this.currentSort) {
        case 'title':
          aValue = a.dataset.title || '';
          bValue = b.dataset.title || '';
          return aValue.localeCompare(bValue);
          
        case '-title':
          aValue = a.dataset.title || '';
          bValue = b.dataset.title || '';
          return bValue.localeCompare(aValue);
          
        case 'popular':
        case '-views_count':
          aValue = parseInt(a.dataset.views) || 0;
          bValue = parseInt(b.dataset.views) || 0;
          return bValue - aValue;
          
        case 'created_at':
          aValue = new Date(a.dataset.created);
          bValue = new Date(b.dataset.created);
          return aValue - bValue;
          
        case '-created_at':
        default:
          aValue = new Date(a.dataset.created);
          bValue = new Date(b.dataset.created);
          return bValue - aValue;
      }
    });
    
    // Re-insertar en orden
    cards.forEach(card => container.appendChild(card));
  },
  
  /**
   * Actualiza mensaje de estado vacío
   */
  updateEmptyState(count) {
    let emptyState = document.querySelector('.empty-state-filters');
    
    if (count === 0 && !emptyState) {
      emptyState = document.createElement('div');
      emptyState.className = 'empty-state empty-state-filters';
      emptyState.innerHTML = `
        <div class="empty-state-icon">🔍</div>
        <h3 class="empty-state-title">No se encontraron proyectos</h3>
        <p class="empty-state-text">Intenta ajustar tus filtros o búsqueda</p>
        <button class="btn btn-primary" data-clear-filters>Limpiar filtros</button>
      `;
      
      const container = document.querySelector('.projects-grid');
      if (container) {
        container.parentElement.appendChild(emptyState);
      }
      
      // Configurar botón
      emptyState.querySelector('[data-clear-filters]').addEventListener('click', () => {
        this.clearAllFilters();
      });
    } else if (count > 0 && emptyState) {
      emptyState.remove();
    }
  },
  
  /**
   * Debounce helper
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  /**
   * Obtiene parámetros actuales de la URL
   */
  getCurrentFilters() {
    const params = new URLSearchParams(window.location.search);
    return {
      category: params.get('category') || '',
      search: params.get('search') || '',
      sort: params.get('sort') || '-created_at'
    };
  },
  
  /**
   * Inicializa filtros desde URL
   */
  initFromURL() {
    const filters = this.getCurrentFilters();
    
    this.currentCategory = filters.category;
    this.currentSearch = filters.search;
    this.currentSort = filters.sort;
    
    // Actualizar UI
    if (this.currentCategory) {
      const activeBtn = document.querySelector(`.filter-btn[data-category="${this.currentCategory}"]`);
      if (activeBtn) {
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        activeBtn.classList.add('active');
      }
    }
    
    if (this.currentSearch) {
      const searchInput = document.querySelector('.search-input, [data-search]');
      if (searchInput) searchInput.value = this.currentSearch;
    }
    
    if (this.currentSort) {
      const sortSelect = document.querySelector('.sort-select, [data-sort]');
      if (sortSelect) sortSelect.value = this.currentSort;
    }
  }
};

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    ProjectFilters.init();
    ProjectFilters.initFromURL();
  });
} else {
  ProjectFilters.init();
  ProjectFilters.initFromURL();
}

// Exportar para uso global
window.ProjectFilters = ProjectFilters;