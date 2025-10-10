"""
Configuración de la aplicación Vulcano.
Define el nombre y carga automática de señales.
"""

from django.apps import AppConfig


class VulcanoConfig(AppConfig):
    """
    Configuración principal de la aplicación Vulcano.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vulcano'
    verbose_name = 'Vulcano - Gestión de Proyectos Arquitectónicos'
    
    def ready(self):
        """
        Se ejecuta cuando la aplicación está lista.
        Importa las señales para que se registren automáticamente.
        """
        import vulcano.signals