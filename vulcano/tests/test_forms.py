"""
Test Forms - Vulcano Platform
Tests para todos los formularios de la aplicación
"""

from django.test import TestCase
from django.contrib.auth.models import User
from vulcano.forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProjectForm,
    MessageForm,
    UserProfileForm
)
from vulcano.models import Project, Message
from datetime import date, timedelta
from decimal import Decimal


class CustomUserCreationFormTest(TestCase):
    """Tests para formulario de registro"""
    
    def test_registration_form_valid_data(self):
        """Verificar formulario válido"""
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente',
            'phone': '+52 55 1234 5678',
            'company': 'Test Company'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_registration_form_password_mismatch(self):
        """Verificar error cuando contraseñas no coinciden"""
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_registration_form_duplicate_username(self):
        """Verificar error con username duplicado"""
        User.objects.create_user(
            username='existinguser',
            email='existing@test.com',
            password='pass123'
        )
        
        form_data = {
            'username': 'existinguser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_registration_form_duplicate_email(self):
        """Verificar error con email duplicado"""
        User.objects.create_user(
            username='user1',
            email='existing@test.com',
            password='pass123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_registration_form_invalid_email(self):
        """Verificar error con email inválido"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_registration_form_missing_required_fields(self):
        """Verificar error con campos requeridos faltantes"""
        form_data = {
            'username': 'newuser',
            # Falta email, password, first_name, last_name, role
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('first_name', form.errors)
    
    def test_registration_form_invalid_role(self):
        """Verificar error con rol inválido"""
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'invalid_role'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
    
    def test_registration_form_weak_password(self):
        """Verificar error con contraseña débil"""
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': '123',  # Contraseña muy corta
            'password2': '123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class CustomAuthenticationFormTest(TestCase):
    """Tests para formulario de login"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_login_form_valid_credentials(self):
        """Verificar formulario válido con credenciales correctas"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_login_form_missing_fields(self):
        """Verificar error con campos faltantes"""
        form_data = {
            'username': 'testuser'
            # Falta password
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
    
    def test_login_form_empty_username(self):
        """Verificar error con username vacío"""
        form_data = {
            'username': '',
            'password': 'testpass123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class ProjectFormTest(TestCase):
    """Tests para formulario de proyecto"""
    
    def setUp(self):
        """Configuración inicial"""
        self.arquitecto = User.objects.create_user(
            username='arquitecto',
            email='arq@test.com',
            password='pass123'
        )
        self.arquitecto.profile.role = 'arquitecto'
        self.arquitecto.profile.save()
        
        self.cliente = User.objects.create_user(
            username='cliente',
            email='cli@test.com',
            password='pass123'
        )
    
    def test_project_form_valid_data(self):
        """Verificar formulario válido"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test description for the project',
            'category': 'residential',
            'status': 'draft',
            'location': 'Ciudad de México, México',
            'area': Decimal('350.50'),
            'budget': Decimal('5000000.00'),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=180),
            'is_published': True,
            'is_featured': False
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_project_form_missing_required_fields(self):
        """Verificar error con campos requeridos faltantes"""
        form_data = {
            'title': 'Test Project'
            # Faltan campos requeridos
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)
        self.assertIn('category', form.errors)
        self.assertIn('status', form.errors)
    
    def test_project_form_invalid_category(self):
        """Verificar error con categoría inválida"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': 'invalid_category',
            'status': 'draft',
            'location': 'Test Location'
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
    
    def test_project_form_invalid_status(self):
        """Verificar error con estado inválido"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': 'residential',
            'status': 'invalid_status',
            'location': 'Test Location'
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
    
    def test_project_form_end_date_before_start_date(self):
        """Verificar validación de fechas"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': 'residential',
            'status': 'draft',
            'location': 'Test Location',
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=30)  # Antes de start_date
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Debería haber error en clean()
    
    def test_project_form_negative_area(self):
        """Verificar error con área negativa"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': 'residential',
            'status': 'draft',
            'location': 'Test Location',
            'area': Decimal('-100.00')
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_project_form_negative_budget(self):
        """Verificar error con presupuesto negativo"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': 'residential',
            'status': 'draft',
            'location': 'Test Location',
            'budget': Decimal('-5000000.00')
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_project_form_clients_field(self):
        """Verificar campo de clientes"""
        form_data = {
            'title': 'Test Project',
            'description': 'Test description',
            'category': 'residential',
            'status': 'draft',
            'location': 'Test Location',
            'clients': [self.cliente.id]
        }
        form = ProjectForm(data=form_data)
        if form.is_valid():
            project = form.save(commit=False)
            project.arquitecto = self.arquitecto
            project.save()
            form.save_m2m()
            self.assertIn(self.cliente, project.clients.all())


class MessageFormTest(TestCase):
    """Tests para formulario de mensaje"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear arquitecto
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass123'
        )
        self.sender.profile.role = 'arquitecto'
        self.sender.profile.save()
        
        # Crear cliente
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='pass123'
        )
        self.recipient.profile.role = 'cliente'
        self.recipient.profile.save()
        
        # Crear proyecto y asociar cliente
        self.project = Project.objects.create(
            title='Test Project',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.sender
        )
        self.project.clients.add(self.recipient)
    
    def test_message_form_valid_data(self):
        """Verificar formulario válido"""
        form_data = {
            'recipient': self.recipient.id,
            'subject': 'Test Subject',
            'body': 'Test message body',
            'project': self.project.id
        }
        form = MessageForm(data=form_data, user=self.sender)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_message_form_without_project(self):
        """Verificar mensaje sin proyecto asociado"""
        form_data = {
            'recipient': self.recipient.id,
            'subject': 'Test Subject',
            'body': 'Test message body'
        }
        form = MessageForm(data=form_data, user=self.sender)
        self.assertTrue(form.is_valid())
    
    def test_message_form_missing_required_fields(self):
        """Verificar error con campos requeridos faltantes"""
        form_data = {
            'subject': 'Test Subject'
            # Falta recipient y body
        }
        form = MessageForm(data=form_data, user=self.sender)
        self.assertFalse(form.is_valid())
        self.assertIn('recipient', form.errors)
        self.assertIn('body', form.errors)
    
    def test_message_form_empty_subject(self):
        """Verificar error con asunto vacío"""
        form_data = {
            'recipient': self.recipient.id,
            'subject': '',
            'body': 'Test body'
        }
        form = MessageForm(data=form_data, user=self.sender)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)
    
    def test_message_form_empty_body(self):
        """Verificar error con cuerpo vacío"""
        form_data = {
            'recipient': self.recipient.id,
            'subject': 'Test Subject',
            'body': ''
        }
        form = MessageForm(data=form_data, user=self.sender)
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)
    
    def test_message_form_invalid_recipient(self):
        """Verificar error con destinatario inválido"""
        form_data = {
            'recipient': 99999,  # ID que no existe
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        form = MessageForm(data=form_data, user=self.sender)
        self.assertFalse(form.is_valid())
        self.assertIn('recipient', form.errors)
    
    def test_message_form_send_to_self(self):
        """Verificar validación de no enviar mensaje a sí mismo"""
        form_data = {
            'recipient': self.sender.id,  # Mismo que sender
            'subject': 'Test Subject',
            'body': 'Test body'
        }
        form = MessageForm(data=form_data, user=self.sender)
        # Debería fallar en clean()
        self.assertFalse(form.is_valid())


class UserProfileFormTest(TestCase):
    """Tests para formulario de perfil de usuario"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_profile_form_valid_data(self):
        """Verificar formulario válido"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'phone': '+52 55 9876 5432',
            'company': 'Updated Company',
            'bio': 'Updated bio'
        }
        form = UserProfileForm(data=form_data, instance=self.user.profile)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_profile_form_update_user(self):
        """Verificar actualización de usuario"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com',
            'phone': '+52 55 9876 5432',
            'company': 'Updated Company',
            'bio': 'Updated bio'
        }
        form = UserProfileForm(data=form_data, instance=self.user.profile)
        if form.is_valid():
            form.save()
            self.user.refresh_from_db()
            self.assertEqual(self.user.first_name, 'Updated')
            self.assertEqual(self.user.email, 'updated@test.com')
    
    def test_profile_form_missing_required_fields(self):
        """Verificar error con campos requeridos faltantes"""
        form_data = {
            'first_name': '',  # Vacío
            'last_name': '',
            'email': ''
        }
        form = UserProfileForm(data=form_data, instance=self.user.profile)
        self.assertFalse(form.is_valid())
    
    def test_profile_form_invalid_email(self):
        """Verificar error con email inválido"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'invalid-email'
        }
        form = UserProfileForm(data=form_data, instance=self.user.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_forms'])