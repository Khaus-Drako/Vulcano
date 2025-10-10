"""
Señales de Django para automatizar tareas en la aplicación Vulcano.
Gestiona creación automática de perfiles y limpieza de caché.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.cache import cache
from .models import UserProfile, Project, ProjectImage, Message
from .utils import clear_user_cache
import logging

logger = logging.getLogger('vulcano')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crea automáticamente un perfil cuando se crea un nuevo usuario.
    Si el perfil no existe, lo crea con rol 'cliente' por defecto.
    """
    if created:
        try:
            UserProfile.objects.get_or_create(
                user=instance,
                defaults={'role': 'cliente'}
            )
            logger.info(f"Perfil creado automáticamente para usuario: {instance.username}")
        except Exception as e:
            logger.error(f"Error al crear perfil para {instance.username}: {str(e)}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil cuando se guarda el usuario.
    """
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except Exception as e:
        logger.error(f"Error al guardar perfil de {instance.username}: {str(e)}")


@receiver(post_save, sender=Project)
def clear_project_caches(sender, instance, **kwargs):
    """
    Limpia cachés relacionados cuando se crea o actualiza un proyecto.
    """
    try:
        # Limpiar caché del arquitecto
        if instance.arquitecto:
            clear_user_cache(instance.arquitecto)
        
        # Limpiar caché de clientes asignados
        for client in instance.clients.all():
            clear_user_cache(client)
        
        # Limpiar caché de proyectos por categoría
        cache.delete('projects_by_category')
        
        logger.debug(f"Cachés limpiados para proyecto: {instance.title}")
    except Exception as e:
        logger.error(f"Error al limpiar cachés de proyecto: {str(e)}")


@receiver(post_delete, sender=Project)
def clear_project_caches_on_delete(sender, instance, **kwargs):
    """
    Limpia cachés cuando se elimina un proyecto.
    """
    try:
        if instance.arquitecto:
            clear_user_cache(instance.arquitecto)
        
        cache.delete('projects_by_category')
        
        logger.info(f"Proyecto eliminado y cachés limpiados: {instance.title}")
    except Exception as e:
        logger.error(f"Error al limpiar cachés tras eliminar proyecto: {str(e)}")


@receiver(post_save, sender=ProjectImage)
def clear_image_caches(sender, instance, **kwargs):
    """
    Limpia cachés cuando se agrega o actualiza una imagen de proyecto.
    """
    try:
        if instance.project and instance.project.arquitecto:
            clear_user_cache(instance.project.arquitecto)
        
        logger.debug(f"Caché limpiado tras guardar imagen de: {instance.project.title}")
    except Exception as e:
        logger.error(f"Error al limpiar caché de imagen: {str(e)}")


@receiver(post_delete, sender=ProjectImage)
def delete_image_file(sender, instance, **kwargs):
    """
    Elimina el archivo físico cuando se elimina una imagen.
    Django-cleanup también hace esto, pero esto es una red de seguridad.
    """
    try:
        if instance.image:
            import os
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
                logger.debug(f"Archivo de imagen eliminado: {instance.image.path}")
    except Exception as e:
        logger.error(f"Error al eliminar archivo de imagen: {str(e)}")


@receiver(post_save, sender=Message)
def clear_message_caches(sender, instance, **kwargs):
    """
    Limpia cachés de estadísticas cuando se crea o actualiza un mensaje.
    """
    try:
        clear_user_cache(instance.recipient)
        clear_user_cache(instance.sender)
        
        logger.debug(f"Cachés limpiados tras mensaje de {instance.sender} a {instance.recipient}")
    except Exception as e:
        logger.error(f"Error al limpiar cachés de mensaje: {str(e)}")


@receiver(pre_save, sender=ProjectImage)
def set_main_image_logic(sender, instance, **kwargs):
    """
    Asegura que solo exista una imagen principal por proyecto.
    """
    if instance.is_main:
        try:
            # Desmarcar otras imágenes principales del mismo proyecto
            ProjectImage.objects.filter(
                project=instance.project,
                is_main=True
            ).exclude(pk=instance.pk).update(is_main=False)
            
            logger.debug(f"Imagen principal establecida para: {instance.project.title}")
        except Exception as e:
            logger.error(f"Error al establecer imagen principal: {str(e)}")