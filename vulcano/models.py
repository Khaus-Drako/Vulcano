"""
Modelos de datos para la plataforma Vulcano.
Define la estructura de proyectos, imágenes, perfiles de usuario y mensajería.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.urls import reverse
import os


class UserProfile(models.Model):
    """
    Perfil extendido de usuario con información adicional y roles.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('arquitecto', 'Arquitecto'),
        ('cliente', 'Cliente'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='cliente',
        verbose_name='Rol'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono',
        help_text='Formato: +51 999 888 666'
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Empresa'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Biografía'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name='Avatar'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        db_table = 'vulcano_user_profile'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.role == 'admin'
    
    def is_arquitecto(self):
        """Verifica si el usuario es arquitecto."""
        return self.role == 'arquitecto'
    
    def is_cliente(self):
        """Verifica si el usuario es cliente."""
        return self.role == 'cliente'


class Project(models.Model):
    """
    Modelo principal para proyectos arquitectónicos.
    Incluye información completa del proyecto y relación con arquitecto.
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('archived', 'Archivado'),
    ]
    
    CATEGORY_CHOICES = [
        ('residential', 'Residencial'),
        ('commercial', 'Comercial'),
        ('industrial', 'Industrial'),
        ('cultural', 'Cultural'),
        ('educational', 'Educacional'),
        ('healthcare', 'Salud'),
        ('hospitality', 'Hospitalidad'),
        ('urban', 'Urbanismo'),
        ('interior', 'Diseño Interior'),
        ('landscape', 'Paisajismo'),
    ]
    
    title = models.CharField(
        max_length=100,
        verbose_name='Título'
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        verbose_name='Slug'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='Descripción corta'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='residential',
        verbose_name='Categoría'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Estado'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Ubicación'
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Área (m²)'
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Presupuesto'
    )
    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de inicio'
    )
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de finalización'
    )
    arquitecto = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Arquitecto'
    )
    clients = models.ManyToManyField(
        User,
        related_name='assigned_projects',
        blank=True,
        verbose_name='Clientes asignados'
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacado'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Publicado'
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Visualizaciones'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        db_table = 'vulcano_project'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['is_published']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['arquitecto', 'title'],
                name='unique_architect_project_title'
            )
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Genera slug automáticamente si no existe."""
        if not self.slug:
            from django.utils import timezone
            timestamp = timezone.now().strftime('%Y%m%d-%H%M%S')
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{timestamp}"
        
        # Genera descripción corta si no existe
        if not self.short_description and self.description:
            self.short_description = self.description[:297] + '...' if len(self.description) > 300 else self.description
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Retorna la URL absoluta del proyecto."""
        return reverse('vulcano:project_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Incrementa el contador de visualizaciones."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_main_image(self):
        """Retorna la imagen principal del proyecto."""
        return self.images.filter(is_main=True).first() or self.images.first()


class ProjectImage(models.Model):
    """
    Modelo para imágenes de proyectos arquitectónicos.
    Soporta múltiples imágenes por proyecto con imagen principal.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Proyecto'
    )
    image = models.ImageField(
        upload_to='projects/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name='Imagen'
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Imagen principal'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de subida'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    class Meta:
        db_table = 'vulcano_project_image'
        verbose_name = 'Imagen de Proyecto'
        verbose_name_plural = 'Imágenes de Proyectos'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.project.title} - {self.caption}" if self.caption else f"Imagen de {self.project.title}"
    
    def save(self, *args, **kwargs):
        """Asegura que solo exista una imagen principal por proyecto."""
        if self.is_main:
            ProjectImage.objects.filter(
                project=self.project,
                is_main=True
            ).update(is_main=False)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Elimina el archivo físico al eliminar el registro."""
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)


class Message(models.Model):
    """
    Sistema de mensajería interna entre usuarios.
    Permite comunicación asincrónica entre clientes y arquitectos.
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Remitente'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Destinatario'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages',
        verbose_name='Proyecto relacionado'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='Asunto'
    )
    body = models.TextField(
        verbose_name='Mensaje'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Leído'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de lectura'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de envío'
    )
    
    class Meta:
        db_table = 'vulcano_message'
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.sender.username} → {self.recipient.username}: {self.subject}"
    
    def mark_as_read(self):
        """Marca el mensaje como leído."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])