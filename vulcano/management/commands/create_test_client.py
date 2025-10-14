from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from vulcano.models import UserProfile

class Command(BaseCommand):
    help = 'Crea un usuario cliente de prueba'

    def handle(self, *args, **kwargs):
        # Datos del usuario
        username = 'clienteprueba'
        email = 'cliente@test.com'
        password = 'cliente123'
        first_name = 'Cliente'
        last_name = 'Prueba'

        try:
            # Crear usuario si no existe
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True
                }
            )

            if created:
                user.set_password(password)
                user.save()

                # Crear o actualizar perfil
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.role = 'cliente'
                profile.phone = '999888777'
                profile.address = 'Av. Test 123'
                profile.description = 'Cliente de prueba para testing'
                profile.save()

                self.stdout.write(self.style.SUCCESS(
                    f'Usuario cliente creado exitosamente:\n'
                    f'Username: {username}\n'
                    f'Password: {password}\n'
                    f'Role: {profile.role}'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'El usuario {username} ya existe.\n'
                    f'Password: {password}'
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))