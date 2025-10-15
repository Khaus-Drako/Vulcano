# Base de diseño moderna para Vulcano
El rediseño mantendrá la lógica actual pero mejorará significativamente la apariencia visual. Aquí está el plan de rediseño:

1. Sistema de Diseño
   - Variables CSS actualizadas (ya implementadas)
   - Sistema de componentes modular
   - Mejores microinteracciones
   - Soporte mejorado para modo oscuro

2. Archivos CSS a crear/actualizar:
   - `variables.css` (sistema de diseño base)
   - `components/` (carpeta nueva)
     - `buttons.css`
     - `cards.css`
     - `forms.css`
     - `navigation.css`
     - `tables.css`
     - `typography.css`
   - `layouts/` (carpeta nueva)
     - `dashboard.css`
     - `auth.css`
     - `projects.css`
     - `sidebar.css`
   - `utilities/` (carpeta nueva)
     - `animations.css`
     - `spacing.css`
     - `flex.css`
     - `grid.css`

3. JavaScript Modular
   - `js/modules/` (carpeta nueva)
     - `theme.js` (selector de tema)
     - `sidebar.js` (navegación)
     - `filters.js` (filtros de proyectos)
     - `forms.js` (validación)
     - `lightbox.js` (galería de imágenes)
     - `animations.js` (microinteracciones)

4. Organización de assets:
   ```
   static/
   ├── css/
   │   ├── components/
   │   ├── layouts/
   │   ├── utilities/
   │   ├── variables.css
   │   └── main.css
   ├── js/
   │   ├── modules/
   │   └── main.js
   └── images/
       ├── icons/
       └── illustrations/
   ```

¿Procedo con la implementación del nuevo diseño siguiendo esta estructura?