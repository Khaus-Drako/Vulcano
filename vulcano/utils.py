"""
Funciones de utilidad para la aplicación Vulcano.
Incluye helpers para imágenes, estadísticas y operaciones comunes.
"""

from django.core.cache import cache
from django.db.models import Count, Q, Avg
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import logging

logger = logging.getLogger('vulcano')


def optimize_image(image_field, max_size=(1920, 1080), quality=85):
    """
    Optimiza una imagen redimensionándola y comprimiéndola.
    
    Args:
        image_field: Campo de imagen de Django
        max_size: Tupla con tamaño máximo (ancho, alto)
        quality: Calidad de compresión (1-100)
    
    Returns:
        InMemoryUploadedFile optimizado
    """
    try:
        img = Image.open(image_field)
        
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Redimensionar manteniendo proporción
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Guardar en memoria
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Crear nuevo archivo
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image_field.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    except Exception as e:
        logger.error(f"Error al optimizar imagen: {str(e)}")
        return image_field


def get_user_statistics(user):
    """
    Obtiene estadísticas del usuario según su rol.
    Utiliza caché para mejorar rendimiento.
    
    Args:
        user: Instancia de User
    
    Returns:
        dict con estadísticas relevantes
    """
    cache_key = f"user_stats_{user.id}"
    stats = cache.get(cache_key)
    
    if stats is None:
        from .models import Project, Message
        
        profile = user.profile
        stats = {
            'role': profile.get_role_display(),
            'member_since': user.date_joined,
        }
        
        if profile.is_admin():
            stats.update({
                'total_users': profile.__class__.objects.count(),
                'total_projects': Project.objects.count(),
                'published_projects': Project.objects.filter(is_published=True).count(),
                'total_messages': Message.objects.count(),
                'unread_messages': Message.objects.filter(
                    recipient=user,
                    is_read=False
                ).count(),
            })
        elif profile.is_arquitecto():
            # Obtener todos los proyectos del arquitecto
            projects = Project.objects.filter(arquitecto=user)
            
            # Calcular estadísticas
            stats.update({
                'total_projects': projects.count(),
                'published_projects': projects.filter(is_published=True).count(),
                'draft_projects': projects.filter(is_published=False).count(),
                'in_progress_projects': projects.filter(status='in_progress').count(),
                'completed_projects': projects.filter(status='completed').count(),
                'total_clients': projects.values('clients').distinct().count(),
                'unread_messages': Message.objects.filter(
                    recipient=user,
                    is_read=False
                ).count(),
                'total_views': projects.aggregate(
                    total=Count('views_count')
                )['total'] or 0,
                'new_projects_month': projects.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
            })
        elif profile.is_cliente():
            stats.update({
                'assigned_projects': user.assigned_projects.count(),
                'completed_projects': user.assigned_projects.filter(
                    status='completed'
                ).count(),
                'in_progress_projects': user.assigned_projects.filter(
                    status='in_progress'
                ).count(),
                'unread_messages': Message.objects.filter(
                    recipient=user,
                    is_read=False
                ).count(),
            })
        
        # Cachear por 5 minutos
        cache.set(cache_key, stats, 300)
    
    return stats


def clear_user_cache(user):
    """
    Limpia el caché de estadísticas de un usuario.
    
    Args:
        user: Instancia de User
    """
    cache_key = f"user_stats_{user.id}"
    cache.delete(cache_key)


def get_recent_projects(limit=6, published_only=True):
    """
    Obtiene los proyectos más recientes.
    
    Args:
        limit: Número de proyectos a retornar
        published_only: Si True, solo proyectos publicados
    
    Returns:
        QuerySet de proyectos
    """
    from .models import Project
    
    queryset = Project.objects.select_related('arquitecto').prefetch_related('images')
    
    if published_only:
        queryset = queryset.filter(is_published=True)
    
    return queryset.order_by('-created_at')[:limit]


def get_featured_projects(limit=3):
    """
    Obtiene proyectos destacados.
    
    Args:
        limit: Número de proyectos a retornar
    
    Returns:
        QuerySet de proyectos destacados
    """
    from .models import Project
    
    return Project.objects.filter(
        is_published=True,
        is_featured=True
    ).select_related('arquitecto').prefetch_related('images').order_by('-created_at')[:limit]


def get_projects_by_category():
    """
    Obtiene conteo de proyectos por categoría.
    
    Returns:
        dict con categorías y conteos
    """
    from .models import Project
    
    cache_key = "projects_by_category"
    data = cache.get(cache_key)
    
    if data is None:
        data = Project.objects.filter(
            is_published=True
        ).values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Cachear por 10 minutos
        cache.set(cache_key, list(data), 600)
    
    return data


def send_notification(user, message, notification_type='info'):
    """
    Envía una notificación al usuario (para futuras implementaciones).
    
    Args:
        user: Usuario destinatario
        message: Mensaje de notificación
        notification_type: Tipo de notificación (info, success, warning, error)
    """
    # TODO: Implementar sistema de notificaciones push o email
    logger.info(f"Notificación [{notification_type}] para {user.username}: {message}")


def format_currency(amount):
    """
    Formatea una cantidad como moneda mexicana.
    
    Args:
        amount: Cantidad numérica
    
    Returns:
        String formateado
    """
    if amount is None:
        return "N/A"
    return f"${amount:,.2f} MXN"


def calculate_project_progress(project):
    """
    Calcula el progreso estimado de un proyecto basado en fechas.
    
    Args:
        project: Instancia de Project
    
    Returns:
        int: Porcentaje de progreso (0-100)
    """
    if not project.start_date or not project.end_date:
        return 0
    
    today = timezone.now().date()
    total_days = (project.end_date - project.start_date).days
    
    if total_days <= 0:
        return 100
    
    elapsed_days = (today - project.start_date).days
    
    if elapsed_days < 0:
        return 0
    elif elapsed_days > total_days:
        return 100
    
    return int((elapsed_days / total_days) * 100)


def log_user_activity(user, action, details=''):
    """
    Registra actividad del usuario en los logs.
    
    Args:
        user: Usuario que realiza la acción
        action: Descripción de la acción
        details: Detalles adicionales
    """
    logger.info(
        f"Actividad de usuario | "
        f"Usuario: {user.username} | "
        f"Acción: {action} | "
        f"Detalles: {details} | "
        f"IP: {user.last_login}"
    )