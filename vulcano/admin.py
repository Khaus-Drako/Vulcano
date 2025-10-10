"""
Configuración del panel de administración de Django para Vulcano.
Personaliza la interfaz administrativa con filtros, búsquedas y acciones.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserProfile, Project, ProjectImage, Message


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Administración de perfiles de usuario.
    """
    list_display = [
        'user_info',
        'role_badge',
        'phone',
        'company',
        'created_at',
    ]
    list_filter = ['role', 'created_at']
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'company',
        'phone',
    ]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user', 'role')
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'company')
        }),
        ('Información Adicional', {
            'fields': ('bio', 'avatar')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        """Muestra información completa del usuario."""
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_info.short_description = 'Usuario'
    
    def role_badge(self, obj):
        """Muestra el rol con badge de color."""
        colors = {
            'admin': 'danger',
            'arquitecto': 'primary',
            'cliente': 'success',
        }
        color = colors.get(obj.role, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Rol'


class ProjectImageInline(admin.TabularInline):
    """
    Inline para gestionar imágenes dentro del proyecto.
    """
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'is_main', 'order']
    readonly_fields = ['uploaded_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Administración de proyectos arquitectónicos.
    """
    list_display = [
        'title',
        'category_badge',
        'status_badge',
        'arquitecto_link',
        'location',
        'is_published',
        'is_featured',
        'views_count',
        'created_at',
    ]
    list_filter = [
        'category',
        'status',
        'is_published',
        'is_featured',
        'created_at',
    ]
    search_fields = [
        'title',
        'description',
        'location',
        'arquitecto__username',
        'arquitecto__first_name',
        'arquitecto__last_name',
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['slug', 'views_count', 'created_at', 'updated_at']
    filter_horizontal = ['clients']
    inlines = [ProjectImageInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'title',
                'slug',
                'short_description',
                'description',
            )
        }),
        ('Clasificación', {
            'fields': (
                'category',
                'status',
                'arquitecto',
                'clients',
            )
        }),
        ('Detalles del Proyecto', {
            'fields': (
                'location',
                'area',
                'budget',
                'start_date',
                'end_date',
            )
        }),
        ('Configuración de Publicación', {
            'fields': (
                'is_published',
                'is_featured',
            )
        }),
        ('Estadísticas', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_published', 'make_unpublished', 'make_featured', 'make_unfeatured']
    
    def category_badge(self, obj):
        """Muestra la categoría con badge."""
        return format_html(
            '<span class="badge badge-info">{}</span>',
            obj.get_category_display()
        )
    category_badge.short_description = 'Categoría'
    
    def status_badge(self, obj):
        """Muestra el estado con badge de color."""
        colors = {
            'draft': 'secondary',
            'in_progress': 'warning',
            'completed': 'success',
            'archived': 'dark',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def arquitecto_link(self, obj):
        """Crea un enlace al perfil del arquitecto."""
        url = reverse('admin:auth_user_change', args=[obj.arquitecto.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.arquitecto.get_full_name() or obj.arquitecto.username
        )
    arquitecto_link.short_description = 'Arquitecto'
    
    def make_published(self, request, queryset):
        """Acción para publicar proyectos."""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} proyecto(s) publicado(s).')
    make_published.short_description = 'Publicar proyectos seleccionados'
    
    def make_unpublished(self, request, queryset):
        """Acción para despublicar proyectos."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} proyecto(s) despublicado(s).')
    make_unpublished.short_description = 'Despublicar proyectos seleccionados'
    
    def make_featured(self, request, queryset):
        """Acción para destacar proyectos."""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} proyecto(s) destacado(s).')
    make_featured.short_description = 'Destacar proyectos seleccionados'
    
    def make_unfeatured(self, request, queryset):
        """Acción para quitar destacado."""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} proyecto(s) sin destacar.')
    make_unfeatured.short_description = 'Quitar destacado de proyectos'


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    """
    Administración de imágenes de proyectos.
    """
    list_display = [
        'image_thumbnail',
        'project_link',
        'caption',
        'is_main',
        'order',
        'uploaded_at',
    ]
    list_filter = ['is_main', 'uploaded_at']
    search_fields = ['project__title', 'caption']
    readonly_fields = ['image_preview', 'uploaded_at']
    list_editable = ['is_main', 'order']
    
    fieldsets = (
        ('Información', {
            'fields': ('project', 'image', 'image_preview', 'caption')
        }),
        ('Configuración', {
            'fields': ('is_main', 'order')
        }),
        ('Fechas', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def image_thumbnail(self, obj):
        """Muestra miniatura de la imagen."""
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="75" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    image_thumbnail.short_description = 'Vista previa'
    
    def image_preview(self, obj):
        """Muestra vista previa más grande de la imagen."""
        if obj.image:
            return format_html(
                '<img src="{}" width="400" style="max-height: 400px; object-fit: contain;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Vista previa'
    
    def project_link(self, obj):
        """Crea enlace al proyecto."""
        url = reverse('admin:vulcano_project_change', args=[obj.project.id])
        return format_html('<a href="{}">{}</a>', url, obj.project.title)
    project_link.short_description = 'Proyecto'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Administración de mensajes.
    """
    list_display = [
        'subject',
        'sender_link',
        'recipient_link',
        'project_link',
        'is_read_badge',
        'created_at',
    ]
    list_filter = ['is_read', 'created_at']
    search_fields = [
        'subject',
        'body',
        'sender__username',
        'recipient__username',
        'project__title',
    ]
    readonly_fields = ['created_at', 'read_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Remitente y Destinatario', {
            'fields': ('sender', 'recipient')
        }),
        ('Contenido del Mensaje', {
            'fields': ('subject', 'body', 'project')
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at')
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def sender_link(self, obj):
        """Enlace al remitente."""
        url = reverse('admin:auth_user_change', args=[obj.sender.id])
        return format_html('<a href="{}">{}</a>', url, obj.sender.username)
    sender_link.short_description = 'Remitente'
    
    def recipient_link(self, obj):
        """Enlace al destinatario."""
        url = reverse('admin:auth_user_change', args=[obj.recipient.id])
        return format_html('<a href="{}">{}</a>', url, obj.recipient.username)
    recipient_link.short_description = 'Destinatario'
    
    def project_link(self, obj):
        """Enlace al proyecto relacionado."""
        if obj.project:
            url = reverse('admin:vulcano_project_change', args=[obj.project.id])
            return format_html('<a href="{}">{}</a>', url, obj.project.title)
        return '-'
    project_link.short_description = 'Proyecto'
    
    def is_read_badge(self, obj):
        """Badge de estado de lectura."""
        if obj.is_read:
            return format_html('<span class="badge badge-success">Leído</span>')
        return format_html('<span class="badge badge-warning">No leído</span>')
    is_read_badge.short_description = 'Estado'


# Personalización del sitio de administración
admin.site.site_header = "Vulcano - Administración"
admin.site.site_title = "Vulcano Admin"
admin.site.index_title = "Panel de Control"