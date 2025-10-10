"""
Decoradores personalizados para control de acceso por roles.
Implementa verificación de permisos basada en el rol del usuario.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import logging

logger = logging.getLogger('vulcano')


def role_required(*roles):
    """
    Decorador que verifica si el usuario tiene uno de los roles especificados.
    
    Uso:
        @role_required('admin', 'arquitecto')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                next_url = request.path
                messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
                if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                if hasattr(request, 'test_mode'):
                    raise PermissionDenied('Authentication required')
                return redirect(f'/login/?next={next_url}')
            
            try:
                if not hasattr(request.user, 'profile'):
                    logger.error(f"Usuario {request.user.username} no tiene perfil")
                    messages.error(request, 'Error: Perfil de usuario no encontrado.')
                    return redirect('vulcano:home')
                
                user_role = request.user.profile.role
                if user_role not in roles:
                    logger.warning(
                        f"Acceso denegado: Usuario {request.user.username} "
                        f"con rol {user_role} intentó acceder a vista que requiere {roles}"
                    )
                    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                        return JsonResponse({'error': 'Permission denied'}, status=403)
                    if hasattr(request, 'test_mode'):
                        raise PermissionDenied('Permission denied')
                    messages.error(
                        request,
                        'No tienes permisos suficientes para acceder a esta página.'
                    )
                    return redirect('vulcano:dashboard')
                
                return view_func(request, *args, **kwargs)
                
            except Exception as e:
                logger.error(f"Error al verificar rol de usuario: {str(e)}")
                messages.error(request, 'Error al verificar permisos.')
                return redirect('vulcano:home')
            
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorador simplificado para vistas que solo pueden acceder administradores.
    """
    return role_required('admin')(view_func)


def arquitecto_or_admin_required(view_func):
    """
    Decorador para vistas accesibles por arquitectos y administradores.
    """
    return role_required('admin', 'arquitecto')(view_func)


def project_owner_required(view_func):
    """
    Decorador que verifica si el usuario es propietario del proyecto o administrador.
    El proyecto debe ser accesible mediante kwargs['slug'] o kwargs['pk'].
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('vulcano:login')
        
        from .models import Project
        
        try:
            # Intentar obtener el proyecto por slug o pk
            project_identifier = kwargs.get('slug') or kwargs.get('pk')
            if kwargs.get('slug'):
                project = Project.objects.get(slug=project_identifier)
            else:
                project = Project.objects.get(pk=project_identifier)
            
            # Verificar si es el propietario o administrador
            user_profile = request.user.profile
            
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                if user_profile.is_admin() or project.arquitecto == request.user:
                    return view_func(request, *args, **kwargs)
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            if hasattr(request, 'test_mode'):
                if user_profile.role == 'admin' or project.arquitecto == request.user:
                    return view_func(request, *args, **kwargs)
                raise PermissionDenied('Permission denied')
            
            if user_profile.is_admin() or project.arquitecto == request.user:
                return view_func(request, *args, **kwargs)
            
            logger.warning(
                f"Acceso denegado: Usuario {request.user.username} "
                f"intentó acceder al proyecto {project.title} sin ser propietario"
            )
            messages.error(request, 'No tienes permisos para gestionar este proyecto.')
            return redirect('vulcano:dashboard')
            
        except Project.DoesNotExist:
            messages.error(request, 'El proyecto no existe.')
            return redirect('vulcano:dashboard')
        except Exception as e:
            logger.error(f"Error en verificación de propietario: {str(e)}")
            messages.error(request, 'Error al verificar permisos.')
            return redirect('vulcano:dashboard')
    
    return wrapper