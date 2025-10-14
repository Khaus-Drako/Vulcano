from django.core.management.base import BaseCommand
from vulcano.models import Project
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Verifica los proyectos en la base de datos'

    def handle(self, *args, **options):
        # Verificar arquitecto
        arquitecto = User.objects.get(username='jhilariop')
        self.stdout.write(f"Arquitecto ID: {arquitecto.id}")
        self.stdout.write(f"Arquitecto rol: {arquitecto.profile.role}")
        
        # Verificar todos los proyectos
        self.stdout.write("\nTodos los proyectos:")
        for project in Project.objects.all():
            self.stdout.write(
                f"ID: {project.id} | "
                f"Título: {project.title} | "
                f"Arquitecto: {project.arquitecto.username} | "
                f"Publicado: {project.is_published} | "
                f"Estado: {project.status}"
            )