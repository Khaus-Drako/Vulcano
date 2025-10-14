# 🧪 CASOS DE PRUEBA MANUALES - VULCANO PLATFORM

## Información del Documento

- **Proyecto:** Vulcano Platform
- **Versión:** 1.0.0
- **Fecha:** 2024
- **Responsable QA:** QA Team
- **Entorno:** Windows 11, Oracle 21c XE, Django 5.2.6

---

## 📋 ÍNDICE DE PRUEBAS

1. [Configuración y Conectividad](#1-configuración-y-conectividad)
2. [Autenticación y Autorización](#2-autenticación-y-autorización)
3. [Gestión de Proyectos (CRUD)](#3-gestión-de-proyectos-crud)
4. [Sistema de Mensajería](#4-sistema-de-mensajería)
5. [Interfaz de Usuario](#5-interfaz-de-usuario)
6. [Dashboards por Rol](#6-dashboards-por-rol)
7. [Seguridad](#7-seguridad)
8. [Rendimiento](#8-rendimiento)

---

## 1. CONFIGURACIÓN Y CONECTIVIDAD

### TC-001: Verificar Conexión a Oracle Database

**Prioridad:** Crítica  
**Precondiciones:** Oracle 21c XE instalado y corriendo

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir PowerShell en directorio del proyecto | PowerShell abierto |
| 2 | Activar entorno virtual: `.venv\Scripts\Activate.ps1` | Entorno activado |
| 3 | Ejecutar: `python manage.py dbshell` | Conexión exitosa a Oracle |
| 4 | Ejecutar query: `SELECT 1 FROM DUAL;` | Retorna `1` |
| 5 | Salir: `EXIT;` | Cierra conexión |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-002: Verificar Carga de Variables de Entorno

**Prioridad:** Alta  
**Precondiciones:** Archivo `.env` configurado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Ejecutar: `python manage.py shell` | Shell de Django abierto |
| 2 | Ejecutar: `from django.conf import settings` | Import exitoso |
| 3 | Ejecutar: `print(settings.SECRET_KEY)` | Muestra SECRET_KEY |
| 4 | Ejecutar: `print(settings.DEBUG)` | Muestra `False` o `True` |
| 5 | Ejecutar: `print(settings.DATABASES['default']['NAME'])` | Muestra nombre de BD |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-003: Verificar Migraciones

**Prioridad:** Crítica  
**Precondiciones:** Base de datos accesible

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Ejecutar: `python manage.py showmigrations` | Muestra lista de migraciones |
| 2 | Verificar que todas tienen `[X]` | Todas aplicadas |
| 3 | Ejecutar: `python manage.py migrate --check` | Sin migraciones pendientes |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-004: Verificar Carga de Archivos Estáticos

**Prioridad:** Media  
**Precondiciones:** Servidor de desarrollo corriendo

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Iniciar servidor: `python manage.py runserver` | Servidor inicia en puerto 8000 |
| 2 | Abrir navegador en `http://127.0.0.1:8000/` | Página carga correctamente |
| 3 | Abrir DevTools (F12) → Network | Panel de red abierto |
| 4 | Recargar página (Ctrl+R) | Archivos CSS/JS cargan (status 200) |
| 5 | Verificar `static/css/main.css` | Carga exitosamente |
| 6 | Verificar `static/js/main.js` | Carga exitosamente |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 2. AUTENTICACIÓN Y AUTORIZACIÓN

### TC-005: Registro de Usuario - Cliente

**Prioridad:** Crítica  
**Precondiciones:** Servidor corriendo

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a `/register/` | Página de registro carga |
| 2 | Llenar formulario:<br>- Username: `cliente_manual`<br>- Email: `cliente@test.com`<br>- Password: `ClientePass123!`<br>- Confirm Password: `ClientePass123!`<br>- First Name: `Cliente`<br>- Last Name: `Test`<br>- Role: `Cliente` | Formulario completo |
| 3 | Click en "Crear Cuenta" | Redirige a página de login |
| 4 | Verificar mensaje de éxito | Mensaje: "Cuenta creada exitosamente" |
| 5 | Intentar login con credenciales | Login exitoso |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-006: Registro de Usuario - Arquitecto

**Prioridad:** Crítica  
**Precondiciones:** Servidor corriendo

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a `/register/` | Página de registro carga |
| 2 | Llenar formulario:<br>- Username: `arquitecto_manual`<br>- Email: `arq@test.com`<br>- Password: `ArqPass123!`<br>- Confirm Password: `ArqPass123!`<br>- First Name: `Arquitecto`<br>- Last Name: `Test`<br>- Role: `Arquitecto`<br>- Company: `Estudio Test` | Formulario completo |
| 3 | Click en "Crear Cuenta" | Redirige a login |
| 4 | Login con credenciales | Login exitoso |
| 5 | Verificar perfil creado con rol correcto | Rol: "Arquitecto" |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-007: Login con Credenciales Válidas

**Prioridad:** Crítica  
**Precondiciones:** Usuario registrado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a `/login/` | Página de login carga |
| 2 | Ingresar username: `arquitecto_manual` | Campo lleno |
| 3 | Ingresar password: `ArqPass123!` | Campo lleno (oculto) |
| 4 | Click en "Iniciar Sesión" | Redirige a dashboard |
| 5 | Verificar navbar muestra usuario logueado | Nombre de usuario visible |
| 6 | Verificar acceso a opciones de usuario | Menú desplegable con opciones |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-008: Login con Credenciales Inválidas

**Prioridad:** Alta  
**Precondiciones:** Ninguna

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a `/login/` | Página de login carga |
| 2 | Ingresar username: `usuario_inexistente` | Campo lleno |
| 3 | Ingresar password: `PasswordIncorrecto123` | Campo lleno |
| 4 | Click en "Iniciar Sesión" | Permanece en página de login |
| 5 | Verificar mensaje de error | "Credenciales inválidas" o similar |
| 6 | Verificar que no se creó sesión | Usuario no logueado |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-009: Logout

**Prioridad:** Alta  
**Precondiciones:** Usuario logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Click en menú de usuario en navbar | Menú desplegable abierto |
| 2 | Click en "Cerrar Sesión" | Redirige a home |
| 3 | Verificar que navbar no muestra usuario | Botones "Login" y "Registro" visibles |
| 4 | Intentar acceder a `/dashboard/` | Redirige a login |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-010: Acceso a Página Protegida sin Login

**Prioridad:** Crítica  
**Precondiciones:** Usuario NO logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar directamente a `/dashboard/` | Redirige a `/login/?next=/dashboard/` |
| 2 | Navegar a `/proyectos/crear/` | Redirige a login |
| 3 | Navegar a `/mensajes/` | Redirige a login |
| 4 | Verificar URL contiene parámetro `next` | URL: `/login/?next=...` |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 3. GESTIÓN DE PROYECTOS (CRUD)

### TC-011: Crear Proyecto - Arquitecto

**Prioridad:** Crítica  
**Precondiciones:** Usuario arquitecto logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a `/proyectos/crear/` | Formulario de proyecto carga |
| 2 | Llenar campos:<br>- Título: `Casa Moderna Test`<br>- Descripción: `Proyecto de prueba con diseño minimalista`<br>- Categoría: `Residencial`<br>- Estado: `Borrador`<br>- Ubicación: `Ciudad de México, México`<br>- Área: `250.50`<br>- Presupuesto: `3500000` | Formulario completo |
| 3 | Seleccionar fecha inicio: `hoy` | Fecha seleccionada |
| 4 | Seleccionar fecha fin: `6 meses adelante` | Fecha seleccionada |
| 5 | Marcar "Publicar Proyecto" | Checkbox marcado |
| 6 | Click en "Crear Proyecto" | Redirige a detalle del proyecto |
| 7 | Verificar proyecto creado | Datos correctos mostrados |
| 8 | Verificar slug generado | URL: `/proyectos/casa-moderna-test-xxxx/` |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-012: Subir Imágenes a Proyecto

**Prioridad:** Alta  
**Precondiciones:** Proyecto creado, arquitecto logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a editar proyecto | Formulario de edición carga |
| 2 | Scroll hasta sección "Imágenes" | Área de upload visible |
| 3 | Click en "Seleccionar archivos" | Explorador de archivos abre |
| 4 | Seleccionar 3 imágenes JPG (< 5MB cada una) | Archivos seleccionados |
| 5 | Verificar preview de imágenes | 3 previsualizaciones visibles |
| 6 | Click en "Actualizar Proyecto" | Proyecto actualizado |
| 7 | Recargar página | 3 imágenes mostradas en galería |
| 8 | Verificar imagen principal marcada | Primera imagen con badge "Principal" |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-013: Editar Proyecto

**Prioridad:** Alta  
**Precondiciones:** Proyecto propio creado, arquitecto logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a detalle del proyecto | Proyecto mostrado |
| 2 | Click en botón "Editar" | Formulario de edición carga |
| 3 | Cambiar título a: `Casa Moderna Test - Actualizada` | Campo actualizado |
| 4 | Cambiar estado a: `En Progreso` | Estado actualizado |
| 5 | Actualizar presupuesto a: `4000000` | Presupuesto actualizado |
| 6 | Click en "Actualizar Proyecto" | Redirige a detalle |
| 7 | Verificar cambios guardados | Datos actualizados correctamente |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-014: Eliminar Proyecto

**Prioridad:** Alta  
**Precondiciones:** Proyecto propio creado, arquitecto logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a detalle del proyecto | Proyecto mostrado |
| 2 | Click en botón "Eliminar" | Página de confirmación carga |
| 3 | Leer advertencias | Información clara de consecuencias |
| 4 | Escribir título del proyecto en campo de confirmación | Texto coincide |
| 5 | Botón "Eliminar Proyecto" se habilita | Botón activo |
| 6 | Click en "Eliminar Proyecto" | Modal de confirmación adicional |
| 7 | Confirmar eliminación | Redirige a dashboard |
| 8 | Verificar proyecto eliminado | No aparece en listado |
| 9 | Intentar acceder al slug del proyecto eliminado | Error 404 |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-015: Ver Detalle de Proyecto Público

**Prioridad:** Media  
**Precondiciones:** Proyecto publicado existe, usuario NO logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a home `/` | Listado de proyectos visible |
| 2 | Click en tarjeta de proyecto | Detalle del proyecto carga |
| 3 | Verificar elementos visibles:<br>- Título<br>- Descripción<br>- Galería de imágenes<br>- Información del arquitecto<br>- Especificaciones (área, presupuesto, etc.) | Todos los elementos mostrados |
| 4 | Click en thumbnails de galería | Cambia imagen principal |
| 5 | Scroll hasta sección de arquitecto | Información del arquitecto visible |
| 6 | Verificar contador de vistas incrementa | Número de vistas +1 |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-016: Intentar Editar Proyecto de Otro Arquitecto

**Prioridad:** Crítica (Seguridad)  
**Precondiciones:** 2 arquitectos con proyectos propios

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Login como Arquitecto A | Logueado exitosamente |
| 2 | Crear proyecto | Proyecto A creado |
| 3 | Copiar URL del proyecto | URL copiada |
| 4 | Logout | Sesión cerrada |
| 5 | Login como Arquitecto B | Logueado exitosamente |
| 6 | Navegar a editar proyecto de A: `/proyectos/proyecto-a/editar/` | Error 403 Forbidden o redirige |
| 7 | Verificar que no puede modificar | Sin acceso a formulario |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 4. SISTEMA DE MENSAJERÍA

### TC-017: Enviar Mensaje Simple

**Prioridad:** Alta  
**Precondiciones:** 2 usuarios registrados (cliente y arquitecto)

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Login como cliente | Logueado exitosamente |
| 2 | Navegar a `/mensajes/nuevo/` | Formulario de mensaje carga |
| 3 | Seleccionar destinatario: Arquitecto Test | Arquitecto seleccionado |
| 4 | Ingresar asunto: `Consulta sobre proyecto` | Asunto ingresado |
| 5 | Ingresar cuerpo: `Hola, me interesa conocer más sobre sus proyectos de casas modernas.` | Mensaje escrito |
| 6 | Click en "Enviar Mensaje" | Redirige a inbox |
| 7 | Verificar mensaje en enviados | Mensaje aparece con badge "Enviado" |
| 8 | Logout y login como arquitecto | Cambio de usuario |
| 9 | Navegar a `/mensajes/` | Inbox carga |
| 10 | Verificar mensaje nuevo | Badge "Nuevo" visible, contador actualizado |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-018: Responder Mensaje

**Prioridad:** Alta  
**Precondiciones:** Mensaje recibido

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Login como arquitecto | Logueado |
| 2 | Navegar a inbox | Mensajes listados |
| 3 | Click en mensaje no leído | Detalle del mensaje carga |
| 4 | Verificar mensaje se marca como leído | Badge "Leído" aparece |
| 5 | Click en botón "Responder" | Formulario de respuesta pre-llenado |
| 6 | Verificar destinatario pre-seleccionado | Cliente correcto |
| 7 | Verificar asunto: `Re: Consulta sobre proyecto` | Asunto con "Re:" |
| 8 | Escribir respuesta: `Gracias por tu interés, con gusto te atiendo.` | Mensaje escrito |
| 9 | Click en "Enviar Mensaje" | Mensaje enviado |
| 10 | Logout y login como cliente | Cambio de usuario |
| 11 | Verificar respuesta en inbox | Mensaje recibido |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-019: Filtrar Mensajes por Estado

**Prioridad:** Media  
**Precondiciones:** Múltiples mensajes (leídos y no leídos)

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a `/mensajes/` | Inbox carga (filtro: Todos) |
| 2 | Contar mensajes totales | N mensajes |
| 3 | Click en tab "Recibidos" | Filtra solo recibidos |
| 4 | Verificar solo mensajes recibidos | Badge "Recibido" en todos |
| 5 | Click en tab "Enviados" | Filtra solo enviados |
| 6 | Verificar solo mensajes enviados | Badge "Enviado" en todos |
| 7 | Click en tab "Sin Leer" | Filtra solo no leídos |
| 8 | Verificar solo mensajes no leídos | Badge "Nuevo" en todos |
| 9 | Verificar contador en cada tab | Números correctos |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-020: Buscar Mensajes

**Prioridad:** Media  
**Precondiciones:** Múltiples mensajes con diferentes asuntos

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a inbox | Mensajes listados |
| 2 | En barra de búsqueda, escribir: `proyecto` | Texto ingresado |
| 3 | Click en "Buscar" | Resultados filtrados |
| 4 | Verificar solo mensajes que contienen "proyecto" | Resultados correctos |
| 5 | Limpiar búsqueda | Todos los mensajes vuelven |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-021: Eliminar Mensaje

**Prioridad:** Media  
**Precondiciones:** Usuario con mensajes

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a inbox | Mensajes listados |
| 2 | Hover sobre mensaje | Botón de eliminar visible |
| 3 | Click en botón eliminar (ícono basura) | Modal de confirmación |
| 4 | Click en "Eliminar" en modal | Mensaje eliminado |
| 5 | Verificar mensaje ya no aparece | Listado actualizado |
| 6 | Intentar acceder al mensaje eliminado por URL | Error 404 |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 5. INTERFAZ DE USUARIO

### TC-022: Navegación en Home Público

**Prioridad:** Media  
**Precondiciones:** Proyectos publicados existentes

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir navegador en `/` | Home carga correctamente |
| 2 | Verificar hero section | Banner principal visible con CTA |
| 3 | Scroll down | Listado de proyectos visible |
| 4 | Verificar tarjetas de proyectos | Imagen, título, categoría, descripción |
| 5 | Hover sobre tarjeta | Efecto visual (sombra, zoom, etc.) |
| 6 | Verificar sección de proyectos destacados | Proyectos con badge "Destacado" |
| 7 | Click en filtro de categoría | Proyectos filtrados |
| 8 | Verificar footer | Información de contacto, enlaces |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-023: Responsive Design - Mobile

**Prioridad:** Alta  
**Precondiciones:** Ninguna

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir DevTools (F12) | Panel de desarrollador abierto |
| 2 | Click en ícono de responsive (Ctrl+Shift+M) | Vista responsive activa |
| 3 | Seleccionar dispositivo: iPhone 12 Pro | Viewport cambia a 390x844 |
| 4 | Navegar a home | Página responsive |
| 5 | Verificar navbar colapsado | Menú hamburguesa visible |
| 6 | Click en menú hamburguesa | Menú se expande |
| 7 | Verificar tarjetas de proyectos en columna única | Layout vertical |
| 8 | Probar scroll | Smooth scrolling |
| 9 | Verificar formularios | Inputs adaptados a mobile |
| 10 | Probar orientación horizontal | Layout se adapta |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-024: Tema Oscuro

**Prioridad:** Baja  
**Precondiciones:** Implementación de tema oscuro

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a cualquier página | Página en tema claro |
| 2 | Click en toggle de tema (navbar) | Tema cambia a oscuro |
| 3 | Verificar colores invertidos | Fondo oscuro, texto claro |
| 4 | Navegar entre páginas | Tema persiste |
| 5 | Verificar legibilidad | Contraste adecuado |
| 6 | Recargar página | Preferencia guardada |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-025: Validación de Formularios en Tiempo Real

**Prioridad:** Media  
**Precondiciones:** Formulario de registro o creación

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a formulario de registro | Formulario visible |
| 2 | Ingresar email inválido: `emailinvalido` | Error mostrado debajo del campo |
| 3 | Mensaje: "Ingrese un email válido" | Mensaje de error claro |
| 4 | Corregir email: `email@valido.com` | Error desaparece, check verde |
| 5 | Ingresar contraseña corta: `123` | Error: "Mínimo 8 caracteres" |
| 6 | Verificar que submit está deshabilitado | Botón en gris, no clickeable |
| 7 | Corregir todos los errores | Botón se habilita |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 6. DASHBOARDS POR ROL

### TC-026: Dashboard de Administrador

**Prioridad:** Alta  
**Precondiciones:** Usuario admin creado y logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Login como admin | Logueado exitosamente |
| 2 | Navegar a `/dashboard/` | Dashboard admin carga |
| 3 | Verificar estadísticas generales:<br>- Total usuarios<br>- Total proyectos<br>- Total mensajes<br>- Total vistas | Cards con números correctos |
| 4 | Verificar sección "Usuarios Recientes" | Tabla con últimos usuarios registrados |
| 5 | Verificar sección "Proyectos Recientes" | Listado con últimos proyectos creados |
| 6 | Verificar sección "Mensajes Recientes" | Mensajes del sistema |
| 7 | Click en "Admin Django" | Abre panel de admin de Django |
| 8 | Verificar sidebar con opciones de admin | Enlaces a gestión de usuarios, proyectos |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-027: Dashboard de Arquitecto

**Prioridad:** Alta  
**Precondiciones:** Usuario arquitecto con proyectos

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Login como arquitecto | Logueado exitosamente |
| 2 | Navegar a `/dashboard/` | Dashboard arquitecto carga |
| 3 | Verificar estadísticas personales:<br>- Mis proyectos<br>- Clientes<br>- Vistas totales<br>- Mensajes nuevos | Cards con datos del arquitecto |
| 4 | Verificar sección "Acciones Rápidas" | Botones: Crear Proyecto, Ver Mensajes, Editar Perfil |
| 5 | Verificar listado "Mis Proyectos" | Proyectos del arquitecto listados |
| 6 | Probar filtros de proyectos:<br>- Todos<br>- Publicados<br>- Borradores<br>- En Progreso<br>- Completados | Filtros funcionan correctamente |
| 7 | Verificar botones de acción en proyectos:<br>- Ver<br>- Editar<br>- Eliminar | Todos los botones presentes |
| 8 | Click en "Crear Proyecto" | Redirige a formulario de creación |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-028: Dashboard de Cliente

**Prioridad:** Alta  
**Precondiciones:** Usuario cliente con proyectos asignados

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Login como cliente | Logueado exitosamente |
| 2 | Navegar a `/dashboard/` | Dashboard cliente carga |
| 3 | Verificar estadísticas:<br>- Proyectos asignados<br>- Arquitectos<br>- Mensajes nuevos<br>- Proyectos favoritos | Cards con datos |
| 4 | Verificar sección "Mis Proyectos" | Proyectos donde está asignado |
| 5 | Verificar sección "Proyectos Destacados" | Proyectos públicos destacados |
| 6 | Click en proyecto | Redirige a detalle |
| 7 | Verificar botón "Contactar Arquitecto" | Botón visible en proyectos asignados |
| 8 | Click en "Explorar Proyectos" | Redirige a home |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 7. SEGURIDAD

### TC-029: Protección CSRF

**Prioridad:** Crítica  
**Precondiciones:** Ninguna

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir formulario de login | Formulario visible |
| 2 | Abrir DevTools → Elements | Panel de elementos abierto |
| 3 | Buscar input con name="csrfmiddlewaretoken" | Token CSRF presente |
| 4 | Verificar token tiene valor único | Valor no vacío |
| 5 | Intentar enviar formulario sin token CSRF (usar cURL o Postman) | Error 403 Forbidden |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-030: Inyección SQL

**Prioridad:** Crítica  
**Precondiciones:** Formulario de búsqueda o filtro

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a página con búsqueda | Campo de búsqueda visible |
| 2 | Ingresar: `' OR '1'='1` | Búsqueda ejecutada |
| 3 | Verificar que no retorna todos los registros | Solo resultados legítimos o vacío |
| 4 | Ingresar: `'; DROP TABLE vulcano_project; --` | Búsqueda falla o retorna vacío |
| 5 | Verificar que tablas siguen existiendo | Base de datos intacta |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-031: XSS (Cross-Site Scripting)

**Prioridad:** Crítica  
**Precondiciones:** Formulario que acepta texto

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a formulario de proyecto | Formulario visible |
| 2 | En descripción, ingresar: `<script>alert('XSS')</script>` | Texto ingresado |
| 3 | Guardar proyecto | Proyecto creado |
| 4 | Ver detalle del proyecto | Script NO se ejecuta |
| 5 | Verificar en HTML renderizado | Caracteres escapados: `&lt;script&gt;` |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-032: Acceso Directo a URLs Protegidas

**Prioridad:** Crítica  
**Precondiciones:** Usuario NO logueado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | En navegador privado/incógnito, navegar a `/dashboard/` | Redirige a login |
| 2 | Navegar a `/proyectos/crear/` | Redirige a login |
| 3 | Navegar a `/mensajes/` | Redirige a login |
| 4 | Navegar a `/admin/` | Página de login de admin |
| 5 | Verificar que ninguna retorna contenido protegido | Todas redirigen |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-033: Sesión Expira Correctamente

**Prioridad:** Media  
**Precondiciones:** Usuario logueado, configuración de timeout de sesión

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Login | Sesión activa |
| 2 | Esperar tiempo de expiración (configurado en settings) | Tiempo transcurrido |
| 3 | Intentar navegar a página protegida | Redirige a login |
| 4 | Verificar mensaje de sesión expirada | Mensaje informativo |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 8. RENDIMIENTO

### TC-034: Tiempo de Carga de Home

**Prioridad:** Media  
**Precondiciones:** 20+ proyectos publicados

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir DevTools → Network | Panel de red abierto |
| 2 | Limpiar log (Clear) | Log vacío |
| 3 | Navegar a home | Página carga |
| 4 | Verificar "Load" time en footer de DevTools | < 2 segundos |
| 5 | Verificar "DOMContentLoaded" | < 1 segundo |
| 6 | Contar requests | < 50 requests |

**Resultado:** ✅ PASS / ❌ FAIL  
**Tiempo de carga:** _______ segundos  
**Notas:** _______________________

---

### TC-035: Número de Queries a BD

**Prioridad:** Media  
**Precondiciones:** Django Debug Toolbar instalado

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Habilitar DEBUG=True en settings | Debug activo |
| 2 | Instalar Django Debug Toolbar | Toolbar visible |
| 3 | Navegar a home | Página carga |
| 4 | Abrir panel de SQL en toolbar | Queries listadas |
| 5 | Verificar número de queries | < 50 queries |
| 6 | Identificar queries duplicadas | Optimizar con select_related/prefetch_related |

**Resultado:** ✅ PASS / ❌ FAIL  
**Número de queries:** _______  
**Notas:** _______________________

---

### TC-036: Carga de Galería de Imágenes

**Prioridad:** Media  
**Precondiciones:** Proyecto con múltiples imágenes

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a proyecto con 10+ imágenes | Detalle carga |
| 2 | Verificar lazy loading de imágenes | Solo imágenes visibles cargan inicialmente |
| 3 | Scroll down | Imágenes adicionales cargan dinámicamente |
| 4 | Verificar tamaño de imágenes | Imágenes optimizadas (< 500KB) |
| 5 | Verificar uso de thumbnails | Thumbnails más pequeños que originales |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

### TC-037: Paginación de Proyectos

**Prioridad:** Media  
**Precondiciones:** 50+ proyectos publicados

| Paso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Navegar a home | Primera página de proyectos |
| 2 | Verificar número de proyectos mostrados | 12 proyectos (o configurado) |
| 3 | Verificar controles de paginación | Botones prev/next, números de página |
| 4 | Click en página 2 | Carga página 2 |
| 5 | Verificar URL actualizada | ?page=2 en URL |
| 6 | Verificar tiempo de carga | Similar a página 1 |

**Resultado:** ✅ PASS / ❌ FAIL  
**Notas:** _______________________

---

## 📊 RESUMEN DE EJECUCIÓN

### Información de Ejecución

- **Fecha de Ejecución:** _______________
- **Ejecutado por:** _______________
- **Entorno:** _______________
- **Versión del Sistema:** _______________

### Resultados Globales

| Categoría | Total Tests | Passed | Failed | N/A |
|-----------|-------------|--------|--------|-----|
| Configuración | 4 | ___ | ___ | ___ |
| Autenticación | 6 | ___ | ___ | ___ |
| CRUD Proyectos | 6 | ___ | ___ | ___ |
| Mensajería | 5 | ___ | ___ | ___ |
| UI | 4 | ___ | ___ | ___ |
| Dashboards | 3 | ___ | ___ | ___ |
| Seguridad | 5 | ___ | ___ | ___ |
| Rendimiento | 4 | ___ | ___ | ___ |
| **TOTAL** | **37** | **___** | **___** | **___** |

### Tasa de Éxito

**Porcentaje de Tests Exitosos:** _______%

### Issues Encontrados

| ID | Severidad | Descripción | Estado |
|----|-----------|-------------|--------|
| 1 | ___ | ___ | ___ |
| 2 | ___ | ___ | ___ |
| 3 | ___ | ___ | ___ |

### Recomendaciones

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Firma

**QA Lead:** _______________  
**Fecha:** _______________

---

**Fin del Documento de Pruebas Manuales**