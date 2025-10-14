from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vulcano.models import UserProfile

class Command(BaseCommand):
    help = 'Verifica y muestra los roles de usuarios'

    def handle(self, *args, **options):
        users = User.objects.all()
        self.stdout.write(self.style.SUCCESS(f'Total usuarios: {users.count()}'))
        
        for user in users:
            profile = UserProfile.objects.filter(user=user).first()
            if profile:
                self.stdout.write(f'Usuario: {user.username} | Email: {user.email} | Rol: {profile.role} | Activo: {user.is_active}')
            else:
                self.stdout.write(self.style.WARNING(f'Usuario sin perfil: {user.username}'))