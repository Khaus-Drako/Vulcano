// Sidebar Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.dashboard-sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const toggleIcon = sidebarToggle.querySelector('i');
    
    // Cargar el estado del sidebar desde localStorage
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        toggleIcon.classList.replace('bi-chevron-left', 'bi-chevron-right');
    }
    
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        
        // Cambiar el ícono según el estado
        if (sidebar.classList.contains('collapsed')) {
            toggleIcon.classList.replace('bi-list', 'bi-x');
            localStorage.setItem('sidebarCollapsed', 'true');
        } else {
            toggleIcon.classList.replace('bi-x', 'bi-list');
            localStorage.setItem('sidebarCollapsed', 'false');
        }
    });
    
    // Mostrar tooltips cuando el sidebar está colapsado
    const navLinks = document.querySelectorAll('.nav-link-dashboard');
    navLinks.forEach(link => {
        const text = link.querySelector('.nav-text')?.textContent.trim();
        if (text) {
            link.setAttribute('title', text);
        }
    });
});