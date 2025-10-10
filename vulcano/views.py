"""
Vistas principales de la aplicación Vulcano.
Implementa toda la lógica de negocio para autenticación, proyectos y portales.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import (
    login, logout, authenticate,
    update_session_auth_hash
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.contrib.auth.models import User
import logging

from .models import Project, ProjectImage, UserProfile, Message
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, ProjectForm,
    ProjectImageForm, MultipleImageUploadForm, MessageForm, UserProfileForm
)
from .decorators import (
    role_required, admin_required, arquitecto_or_admin_required,
    project_owner_required
)
from .utils import (
    get_user_statistics, clear_user_cache, get_recent_projects,
    get_featured_projects, optimize_image, log_user_activity,
    calculate_project_progress
)

logger = logging.getLogger('vulcano')


# ==================== VISTAS PÚBLICAS ====================

def home(request):
    """
    Página principal pública con proyectos destacados y filtros.
    """
    # Obtener parámetros de filtrado
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset de proyectos publicados
    projects = Project.objects.filter(
        is_published=True
    ).select_related('arquitecto__profile').prefetch_related(
        Prefetch('images', queryset=ProjectImage.objects.order_by('order'))
    )
    
    # Aplicar filtros
    if category:
        projects = projects.filter(category=category)
    
    if search:
        projects = projects.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Aplicar ordenamiento
    valid_sorts = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'popular': '-views_count',
        'title': 'title',
    }
    sort_field = valid_sorts.get(sort_by, '-created_at')
    projects = projects.order_by(sort_field)
    
    # Paginación
    paginator = Paginator(projects, 12)
    page = request.GET.get('page', 1)
    
    try:
        projects_page = paginator.page(page)
    except PageNotAnInteger:
        projects_page = paginator.page(1)
    except EmptyPage:
        projects_page = paginator.page(paginator.num_pages)
    
    # Proyectos destacados
    featured_projects = get_featured_projects(3)
    
    # Categorías con conteo
    categories = Project.objects.filter(
        is_published=True
    ).values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'projects': projects_page,
        'featured_projects': featured_projects,
        'categories': categories,
        'current_category': category,
        'search_query': search,
        'current_sort': sort_by,
        'total_projects': projects.count(),
    }
    
    return render(request, 'home.html', context)


def project_detail(request, slug):
    """
    Vista de detalle de proyecto con galería de imágenes.
    Incrementa contador de visualizaciones.
    """
    project = get_object_or_404(
        Project.objects.select_related(
            'arquitecto__profile'
        ).prefetch_related('images', 'clients'),
        slug=slug
    )
    
    # Verificar permisos de visualización
    if not project.is_published:
        if not request.user.is_authenticated:
            messages.error(request, 'Este proyecto no está disponible.')
            return redirect('vulcano:home')
        
        # Solo el arquitecto, clientes asignados o admin pueden ver proyectos no publicados
        user_profile = request.user.profile
        if not (user_profile.is_admin() or 
                project.arquitecto == request.user or
                request.user in project.clients.all()):
            messages.error(request, 'No tienes permisos para ver este proyecto.')
            return redirect('vulcano:home')
    
    # Incrementar contador de vistas (solo para visitantes únicos por sesión)
    session_key = f"viewed_project_{project.id}"
    if not request.session.get(session_key):
        project.increment_views()
        request.session[session_key] = True
    
    # Proyectos relacionados de la misma categoría
    related_projects = Project.objects.filter(
        category=project.category,
        is_published=True
    ).exclude(id=project.id).select_related(
        'arquitecto'
    ).prefetch_related('images')[:3]
    
    # Calcular progreso si es proyecto activo
    progress = None
    if project.status == 'in_progress':
        progress = calculate_project_progress(project)
    
    context = {
        'project': project,
        'project_images': project.images.all(),
        'related_projects': related_projects,
        'progress': progress,
        'can_edit': (request.user.is_authenticated and 
                    (request.user.profile.is_admin() or 
                     project.arquitecto == request.user)),
    }
    
    return render(request, 'projects/project_detail.html', context)


# ==================== AUTENTICACIÓN ====================

def register_view(request):
    """
    Vista de registro de nuevos usuarios.
    """
    if request.user.is_authenticated:
        return redirect('vulcano:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                '¡Cuenta creada exitosamente! Por favor, inicia sesión para continuar.'
            )
            log_user_activity(user, 'Registro', f'Nuevo usuario con rol {user.profile.role}')
            return redirect('vulcano:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """
    Vista de inicio de sesión.
    """
    if request.user.is_authenticated:
        return redirect('vulcano:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.get_full_name()}!')
                log_user_activity(user, 'Inicio de sesión', 'Login exitoso')
                
                # Redirigir a la página solicitada o al dashboard
                next_url = request.GET.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('vulcano:dashboard')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'auth/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


@login_required
def logout_view(request):
    """
    Vista de cierre de sesión.
    """
    username = request.user.username
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    logger.info(f"Usuario {username} cerró sesión")
    return redirect('vulcano:home')


# ==================== DASHBOARD Y PORTALES ====================

@login_required
def dashboard(request):
    """
    Dashboard principal que redirige al portal según el rol del usuario.
    """
    try:
        user_profile = request.user.profile
        
        if user_profile.is_admin() or user_profile.role == 'admin':
            return render(request, 'dashboard/portal_admin.html')
        elif user_profile.is_arquitecto():
            return render(request, 'dashboard/portal_arquitecto.html')
        elif user_profile.is_cliente():
            return render(request, 'dashboard/portal_cliente.html')
        
        messages.error(request, 'Rol de usuario no reconocido.')
        return redirect('vulcano:home')
    except Exception as e:
        logger.error(f"Error en dashboard: {str(e)}")
        messages.error(request, 'Error al cargar el dashboard.')
        return redirect('vulcano:home')


@login_required
@admin_required
def portal_admin(request):
    """
    Portal de administrador con gestión completa del sistema.
    """
    stats = get_user_statistics(request.user)
    
    # Obtener datos recientes
    recent_projects = Project.objects.select_related(
        'arquitecto'
    ).order_by('-created_at')[:5]
    
    recent_users = User.objects.select_related(
        'profile'
    ).order_by('-date_joined')[:5]
    
    recent_messages = Message.objects.select_related(
        'sender', 'recipient'
    ).order_by('-created_at')[:5]
    
    # Estadísticas por categoría
    projects_by_status = Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    projects_by_category = Project.objects.filter(
        is_published=True
    ).values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'stats': stats,
        'recent_projects': recent_projects,
        'recent_users': recent_users,
        'recent_messages': recent_messages,
        'projects_by_status': projects_by_status,
        'projects_by_category': projects_by_category,
    }
    
    return render(request, 'dashboard/portal_admin.html', context)


@login_required
@role_required('arquitecto')
def portal_arquitecto(request):
    """
    Portal de arquitecto con gestión de proyectos propios.
    """
    stats = get_user_statistics(request.user)
    
    # Proyectos del arquitecto
    my_projects = Project.objects.filter(
        arquitecto=request.user
    ).prefetch_related('images').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        my_projects = my_projects.filter(status=status_filter)
    
    # Paginación
    paginator = Paginator(my_projects, 9)
    page = request.GET.get('page', 1)
    
    try:
        projects_page = paginator.page(page)
    except PageNotAnInteger:
        projects_page = paginator.page(1)
    except EmptyPage:
        projects_page = paginator.page(paginator.num_pages)
    
    # Mensajes recientes
    recent_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).select_related('sender', 'recipient').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'projects': projects_page,
        'recent_messages': recent_messages,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/portal_arquitecto.html', context)


@login_required
@role_required('cliente')
def portal_cliente(request):
    """
    Portal de cliente con proyectos asignados.
    """
    stats = get_user_statistics(request.user)
    
    # Proyectos asignados al cliente
    assigned_projects = request.user.assigned_projects.select_related(
        'arquitecto__profile'
    ).prefetch_related('images').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        assigned_projects = assigned_projects.filter(status=status_filter)
    
    # Mensajes recientes
    recent_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).select_related('sender', 'recipient').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'projects': assigned_projects,
        'recent_messages': recent_messages,
        'status_filter': status_filter,
    }
    
    return render(request, 'dashboard/portal_cliente.html', context)


# ==================== CRUD DE PROYECTOS ====================

@login_required
@arquitecto_or_admin_required
def project_create(request):
    """
    Vista para crear un nuevo proyecto.
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            project = form.save(commit=False)
            
            # Asignar arquitecto automáticamente si no es admin
            if not request.user.profile.is_admin():
                project.arquitecto = request.user
            else:
                # Admin debe seleccionar un arquitecto
                if not project.arquitecto:
                    messages.error(request, 'Debes seleccionar un arquitecto para el proyecto.')
                    return render(request, 'projects/project_form.html', {
                        'form': form,
                        'image_form': image_form
                    })
            
            project.save()
            form.save_m2m()  # Guardar relaciones many-to-many (clientes)
            
            # Procesar imágenes si se subieron
            if image_form.is_valid() and request.FILES.getlist('images'):
                images = request.FILES.getlist('images')
                for i, image in enumerate(images):
                    ProjectImage.objects.create(
                        project=project,
                        image=image,
                        is_main=(i == 0),  # Primera imagen como principal
                        order=i
                    )
            
            messages.success(request, f'Proyecto "{project.title}" creado exitosamente.')
            log_user_activity(request.user, 'Crear proyecto', f'Proyecto: {project.title}')
            clear_user_cache(request.user)
            
            return redirect('vulcano:project_detail', slug=project.slug)
    else:
        form = ProjectForm()
        image_form = MultipleImageUploadForm()
        
        # Pre-asignar arquitecto si no es admin
        if not request.user.profile.is_admin():
            form.initial['arquitecto'] = request.user
    
    context = {
        'form': form,
        'image_form': image_form,
        'action': 'Crear',
    }
    
    return render(request, 'projects/project_form.html', context)


@login_required
@project_owner_required
def project_edit(request, slug):
    """
    Vista para editar un proyecto existente.
    """
    project = get_object_or_404(Project, slug=slug)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        image_form = MultipleImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            project = form.save()
            
            # Procesar nuevas imágenes
            if image_form.is_valid() and request.FILES.getlist('images'):
                images = request.FILES.getlist('images')
                current_max_order = project.images.count()
                
                for i, image in enumerate(images):
                    ProjectImage.objects.create(
                        project=project,
                        image=image,
                        order=current_max_order + i
                    )
            
            messages.success(request, f'Proyecto "{project.title}" actualizado exitosamente.')
            log_user_activity(request.user, 'Editar proyecto', f'Proyecto: {project.title}')
            clear_user_cache(request.user)
            
            return redirect('vulcano:project_detail', slug=project.slug)
    else:
        form = ProjectForm(instance=project)
        image_form = MultipleImageUploadForm()
    
    context = {
        'form': form,
        'image_form': image_form,
        'project': project,
        'action': 'Editar',
    }
    
    return render(request, 'projects/project_form.html', context)


@login_required
@project_owner_required
def project_delete(request, slug):
    """
    Vista para eliminar un proyecto.
    """
    project = get_object_or_404(Project, slug=slug)
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f'Proyecto "{project_title}" eliminado exitosamente.')
        log_user_activity(request.user, 'Eliminar proyecto', f'Proyecto: {project_title}')
        clear_user_cache(request.user)
        return redirect('vulcano:dashboard')
    
    context = {'project': project}
    return render(request, 'projects/project_delete.html', context)


@login_required
@project_owner_required
def project_image_delete(request, slug, image_id):
    """
    Elimina una imagen específica de un proyecto (AJAX).
    """
    if request.method == 'POST':
        project = get_object_or_404(Project, slug=slug)
        image = get_object_or_404(ProjectImage, id=image_id, project=project)
        
        image.delete()
        messages.success(request, 'Imagen eliminada exitosamente.')
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


# ==================== MENSAJERÍA ====================

@login_required
def inbox(request):
    """
    Vista de bandeja de entrada de mensajes.
    """
    # Obtener mensajes según el filtro
    filter_type = request.GET.get('filter', 'all')
    
    if filter_type == 'sent':
        messages_list = Message.objects.filter(
            sender=request.user
        ).select_related('recipient', 'project').order_by('-created_at')
    else:
        messages_list = Message.objects.filter(
            recipient=request.user
        ).select_related('sender', 'project').order_by('-created_at')
    
    # Aplicar filtros adicionales
    if filter_type == 'unread':
        messages_list = messages_list.filter(is_read=False)
    elif filter_type == 'read':
        messages_list = messages_list.filter(is_read=True)
    
    # Paginación
    paginator = Paginator(messages_list, 20)
    page = request.GET.get('page', 1)
    
    try:
        messages_page = paginator.page(page)
    except PageNotAnInteger:
        messages_page = paginator.page(1)
    except EmptyPage:
        messages_page = paginator.page(paginator.num_pages)
    
    # Contar mensajes no leídos
    unread_count = Message.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    context = {
        'messages': messages_page,
        'unread_count': unread_count,
        'filter_type': filter_type,
    }
    
    return render(request, 'messaging/inbox.html', context)


@login_required
def message_detail(request, pk):
    """
    Vista de detalle de mensaje individual.
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'recipient', 'project'),
        id=pk
    )
    
    # Verificar que el usuario es el destinatario o remitente
    if message.recipient != request.user and message.sender != request.user:
        return HttpResponseForbidden('No tienes permiso para ver este mensaje.')
    
    # Marcar como leído si es el destinatario
    if message.recipient == request.user:
        message.mark_as_read()
    
    # Determinar el otro usuario en la conversación
    other_user = message.sender if message.recipient == request.user else message.recipient
    
    context = {
        'message': message,
        'other_user': other_user,
    }
    return render(request, 'messaging/message_detail.html', context)


@login_required
def message_compose(request):
    """
    Vista para redactar nuevo mensaje.
    """
    # Crear el formulario con el usuario actual
    if request.method == 'POST':
        form = MessageForm(user=request.user, data=request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            messages.success(request, 'Mensaje enviado exitosamente.')
            log_user_activity(
                request.user,
                'Enviar mensaje',
                f'A: {message.recipient.username}'
            )
            
            # Limpiar caché después de enviar mensaje
            clear_user_cache(request.user)
            clear_user_cache(message.recipient)
            
            return redirect('vulcano:inbox')
    else:
        form = MessageForm(user=request.user)
        
        # Pre-llenar destinatario si se pasa por parámetro
        recipient_id = request.GET.get('to')
        if recipient_id:
            try:
                recipient = User.objects.get(id=recipient_id)
                form.initial['recipient'] = recipient.id
            except User.DoesNotExist:
                pass
        
        # Pre-llenar proyecto si se pasa por parámetro
        project_id = request.GET.get('project')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                form.initial['project'] = project.id
            except Project.DoesNotExist:
                pass
    
    context = {'form': form}
    return render(request, 'messaging/compose.html', context)


@login_required
def message_delete(request, pk):
    """
    Elimina un mensaje (solo el destinatario).
    """
    if request.method == 'POST':
        message = get_object_or_404(Message, id=pk, recipient=request.user)
        message.delete()
        messages.success(request, 'Mensaje eliminado exitosamente.')
        return redirect('vulcano:inbox')
    
    return HttpResponseForbidden()


# ==================== GESTIÓN DE CONTRASEÑA ====================

@login_required
def password_change(request):
    """
    Vista para cambiar la contraseña del usuario.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Tu contraseña ha sido actualizada exitosamente.')
            return redirect('vulcano:profile')
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'auth/password_change.html', {'form': form})


# ==================== PERFIL DE USUARIO ====================

@login_required
def profile_view(request):
    """
    Vista y edición del perfil de usuario.
    """
    profile = request.user.profile
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            clear_user_cache(request.user)
            return redirect('vulcano:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'dashboard/profile.html', context)


# ==================== VISTAS AJAX ====================

@login_required
def ajax_mark_message_read(request, pk):
    """
    Marca un mensaje como leído vía AJAX.
    """
    if request.method == 'POST':
        message = get_object_or_404(Message, id=pk, recipient=request.user)
        message.mark_as_read()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


@login_required
def ajax_project_toggle_featured(request, project_id):
    """
    Alterna el estado de proyecto destacado (solo admin).
    """
    if not request.user.profile.is_admin():
        return JsonResponse({'success': False, 'error': 'Permisos insuficientes'}, status=403)
    
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        project.is_featured = not project.is_featured
        project.save()
        
        return JsonResponse({
            'success': True,
            'is_featured': project.is_featured
        })
    
    return JsonResponse({'success': False}, status=400)