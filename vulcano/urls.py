"""
Configuración de URLs para la aplicación Vulcano.
Define todas las rutas de la plataforma organizadas por funcionalidad.
"""

from django.urls import path
from . import views

app_name = 'vulcano'

urlpatterns = [
    # ==================== VISTAS PÚBLICAS ====================
    path('', views.home, name='home'),
    path('proyecto/<slug:slug>/', views.project_detail, name='project_detail'),
    
    # ==================== AUTENTICACIÓN ====================
    path('registro/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==================== DASHBOARD Y PORTALES ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('portal/admin/', views.portal_admin, name='portal_admin'),
    path('portal/arquitecto/', views.portal_arquitecto, name='portal_arquitecto'),
    path('portal/cliente/', views.portal_cliente, name='portal_cliente'),
    
    # ==================== PERFIL DE USUARIO ====================
    path('perfil/', views.profile_view, name='profile'),
    
    # ==================== CRUD DE PROYECTOS ====================
    path('proyectos/crear/', views.project_create, name='project_create'),
    path('proyectos/editar/<slug:slug>/', views.project_edit, name='project_edit'),
    path('proyectos/eliminar/<slug:slug>/', views.project_delete, name='project_delete'),
    
    # ==================== GESTIÓN DE IMÁGENES ====================
    path(
        'proyectos/<slug:slug>/imagen/<int:image_id>/eliminar/',
        views.project_image_delete,
        name='project_image_delete'
    ),
    
    # ==================== MENSAJERÍA ====================
    path('mensajes/', views.inbox, name='inbox'),
    path('mensajes/<int:pk>/', views.message_detail, name='message_detail'),
    path('mensajes/nuevo/', views.message_compose, name='message_compose'),
    path('mensajes/<int:pk>/eliminar/', views.message_delete, name='message_delete'),
    
    # ==================== VISTAS AJAX ====================
    path(
        'ajax/mensaje/<int:message_id>/marcar-leido/',
        views.ajax_mark_message_read,
        name='ajax_mark_message_read'
    ),
    path(
        'ajax/proyecto/<int:project_id>/destacar/',
        views.ajax_project_toggle_featured,
        name='ajax_project_toggle_featured'
    ),

    # ==================== GESTIÓN DE CONTRASEÑA ====================
    path(
        'cambiar-password/',
        views.password_change,
        name='password_change'
    ),
]