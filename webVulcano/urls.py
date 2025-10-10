"""
Configuración de URLs principal del proyecto Vulcano.
Define las rutas principales y delega a la aplicación vulcano.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Rutas de la aplicación principal
    path('', include('vulcano.urls', namespace='vulcano')),
]

# Servir archivos multimedia en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = "Vulcano - Panel de Administración"
admin.site.site_title = "Vulcano Admin"
admin.site.index_title = "Gestión de Proyectos Arquitectónicos"