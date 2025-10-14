from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vulcano.models import Project
from django.utils import timezone

class Command(BaseCommand):
    help = 'Crea un proyecto de prueba para un arquitecto'

    def handle(self, *args, **options):
        # Buscar un arquitecto
        arquitecto = User.objects.filter(profile__role='arquitecto').first()
        
        if not arquitecto:
            self.stdout.write(self.style.ERROR('No se encontró ningún arquitecto'))
            return
            
        # Crear proyecto de prueba
        project = Project.objects.create(
            title='Proyecto de Prueba',
            description='Este es un proyecto de prueba para verificar la funcionalidad.',
            slug='proyecto-de-prueba',
            arquitecto=arquitecto,
            category='residential',
            status='in_progress',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            budget=50000.00,
            area=150.00,
            location='Lima, Perú',
            is_published=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Proyecto creado exitosamente: {project.title}'))
        self.stdout.write(f'ID: {project.id}')
        self.stdout.write(f'Arquitecto: {project.arquitecto.username}')
        self.stdout.write(f'Estado: {project.status}')
        self.stdout.write(f'Publicado: {project.is_published}')