/**
 * VULCANO - Filtros y Búsqueda de Proyectos
 * Filtrado dinámico, búsqueda y ordenamiento
 */

'use strict';

const ProjectFilters = {
  currentCategory: '',
  currentSearch: '',
  currentSort: '-created_at',
  initialized: false,
  
  init() {
    if (this.initialized) return;
    this.initialized = true;
    
    this.initFromURL();
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
      if (button.dataset.filterAdded) return;
      button.dataset.filterAdded = 'true';
      
      button.addEventListener('click', () => {
        // Actualizar estado activo
        filterButtons.forEach(btn => {
          btn.classList.remove('active');
          btn.removeAttribute('aria-current');
        });
        
        button.classList.add('active');
        button.setAttribute('aria-current', 'true');
        
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
    
    if (searchInput && !searchInput.dataset.searchAdded) {
      searchInput.dataset.searchAdded = 'true';
      
      const debouncedSearch = this.debounce((value) => {
        this.currentSearch = value;
        this.applyFilters();
      }, 300);
      
      searchInput.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
      });
      
      // Limpiar búsqueda
      const clearBtn = searchInput.parentElement.querySelector('.search-clear, [data-search-clear]');
      if (clearBtn) {
        clearBtn.addEventListener('click', () => {
          searchInput.value = '';
          this.currentSearch = '';
          this.applyFilters();
          searchInput.focus();
        });
      }
    }
  },
  
  /**
   * Configura selector de ordenamiento
   */
  setupSortSelect() {
    const sortSelect = document.querySelector('.sort-select, [data-sort]');
    
    if (sortSelect && !sortSelect.dataset.sortAdded) {
      sortSelect.dataset.sortAdded = 'true';
      
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
    const clearButtons = document.querySelectorAll('[data-clear-filters]');
    
    clearButtons.forEach(button => {
      if (button.dataset.clearAdded) return;
      button.dataset.clearAdded = 'true';
      
      button.addEventListener('click', (e) => {
        e.preventDefault();
        this.clearAllFilters();
      });
    });
  },
  
  /**
   * Aplica filtros actuales (recarga la página con query params)
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
    
    // Actualizar URL
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
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.classList.remove('active');
      btn.removeAttribute('aria-current');
    });
    
    const allBtn = document.querySelector('.filter-btn[data-category=""]');
    if (allBtn) {
      allBtn.classList.add('active');
      allBtn.setAttribute('aria-current', 'true');
    }
    
    const searchInput = document.querySelector('.search-input, [data-search]');
    if (searchInput) searchInput.value = '';
    
    const sortSelect = document.querySelector('.sort-select, [data-sort]');
    if (sortSelect) sortSelect.value = '-created_at';
    
    // Aplicar
    window.location.href = window.location.pathname;
  },
  
  /**
   * Filtrado del lado del cliente (opcional, para UX sin recarga)
   */
  filterClientSide() {
    const projectCards = document.querySelectorAll('.project-card[data-category]');
    let visibleCount = 0;
    
    projectCards.forEach(card => {
      const category = card.dataset.category || '';
      const title = (card.dataset.title || '').toLowerCase();
      const description = (card.dataset.description || '').toLowerCase();
      const searchLower = this.currentSearch.toLowerCase();
      
      const categoryMatch = !this.currentCategory || category === this.currentCategory;
      const searchMatch = !this.currentSearch || 
                         title.includes(searchLower) || 
                         description.includes(searchLower);
      
      if (categoryMatch && searchMatch) {
        card.style.display = '';
        card.removeAttribute('aria-hidden');
        
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
          card.style.animation = 'fadeInUp 0.4s ease-out';
        }
        visibleCount++;
      } else {
        card.style.display = 'none';
        card.setAttribute('aria-hidden', 'true');
      }
    });
    
    this.updateEmptyState(visibleCount);
    
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
          aValue = new Date(a.dataset.created || 0);
          bValue = new Date(b.dataset.created || 0);
          return aValue - bValue;
          
        case '-created_at':
        default:
          aValue = new Date(a.dataset.created || 0);
          bValue = new Date(b.dataset.created || 0);
          return bValue - aValue;
      }
    });
    
    cards.forEach(card => container.appendChild(card));
  },
  
  /**
   * Actualiza mensaje de estado vacío
   */
  updateEmptyState(count) {
    let emptyState = document.querySelector('.empty-state-filters');
    
    if (count === 0 && !emptyState) {
      emptyState = document.createElement('div');
      emptyState.className = 'empty-state empty-state-filters text-center py-5';
      emptyState.setAttribute('role', 'status');
      emptyState.innerHTML = `
        <div class="empty-state-icon" aria-hidden="true">🔍</div>
        <h3 class="empty-state-title h4">No se encontraron proyectos</h3>
        <p class="empty-state-text text-muted">Intenta ajustar tus filtros o búsqueda</p>
        <button class="btn btn-primary mt-3" data-clear-filters>Limpiar filtros</button>
      `;
      
      const container = document.querySelector('.projects-grid');
      if (container && container.parentElement) {
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
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), wait);
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
        document.querySelectorAll('.filter-btn').forEach(btn => {
          btn.classList.remove('active');
          btn.removeAttribute('aria-current');
        });
        activeBtn.classList.add('active');
        activeBtn.setAttribute('aria-current', 'true');
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

// Inicializar
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => ProjectFilters.init());
} else {
  ProjectFilters.init();
}

window.ProjectFilters = ProjectFilters;