"""
Test Models - Vulcano Platform
Tests para todos los modelos de la aplicación
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from vulcano.models import UserProfile, Project, ProjectImage, Message


class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@vulcano.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """Verificar creación automática de perfil"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_profile_default_role(self):
        """Verificar rol por defecto"""
        self.assertEqual(self.user.profile.role, 'cliente')
    
    def test_profile_roles(self):
        """Verificar todos los roles disponibles"""
        roles = ['admin', 'arquitecto', 'cliente']
        for role in roles:
            user = User.objects.create_user(
                username=f'user_{role}',
                email=f'{role}@vulcano.com',
                password='pass123'
            )
            user.profile.role = role
            user.profile.save()
            self.assertEqual(user.profile.role, role)
    
    def test_profile_is_methods(self):
        """Verificar métodos is_admin, is_arquitecto, is_cliente"""
        # Admin
        admin_user = User.objects.create_user(username='admin', email='admin@test.com', password='pass')
        admin_user.profile.role = 'admin'
        admin_user.profile.save()
        self.assertTrue(admin_user.profile.is_admin())
        self.assertFalse(admin_user.profile.is_arquitecto())
        self.assertFalse(admin_user.profile.is_cliente())
        
        # Arquitecto
        arq_user = User.objects.create_user(username='arquitecto', email='arq@test.com', password='pass')
        arq_user.profile.role = 'arquitecto'
        arq_user.profile.save()
        self.assertFalse(arq_user.profile.is_admin())
        self.assertTrue(arq_user.profile.is_arquitecto())
        self.assertFalse(arq_user.profile.is_cliente())
        
        # Cliente
        self.assertFalse(self.user.profile.is_admin())
        self.assertFalse(self.user.profile.is_arquitecto())
        self.assertTrue(self.user.profile.is_cliente())
        self.assertFalse(self.user.profile.is_arquitecto())
        self.assertTrue(self.user.profile.is_cliente())
    
    def test_profile_str_method(self):
        """Verificar método __str__"""
        expected = f"{self.user.get_full_name()} ({self.user.profile.get_role_display()})"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_profile_optional_fields(self):
        """Verificar campos opcionales"""
        profile = self.user.profile
        profile.phone = '+52 55 1234 5678'
        profile.company = 'Test Company'
        profile.bio = 'Test bio'
        profile.save()
        
        self.assertEqual(profile.phone, '+52 55 1234 5678')
        self.assertEqual(profile.company, 'Test Company')
        self.assertEqual(profile.bio, 'Test bio')


class ProjectModelTest(TestCase):
    """Tests para el modelo Project"""
    
    def setUp(self):
        """Configuración inicial"""
        self.arquitecto = User.objects.create_user(
            username='arquitecto1',
            email='arq@vulcano.com',
            password='pass123'
        )
        self.arquitecto.profile.role = 'arquitecto'
        self.arquitecto.profile.save()
        
        self.cliente = User.objects.create_user(
            username='cliente1',
            email='cli@vulcano.com',
            password='pass123'
        )
        
        self.project = Project.objects.create(
            title='Casa de Prueba',
            description='Descripción de prueba para casa moderna',
            category='residential',
            status='draft',
            location='Ciudad de México, México',
            arquitecto=self.arquitecto,
            area=Decimal('350.50'),
            budget=Decimal('5000000.00'),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180)
        )
    
    def test_project_creation(self):
        """Verificar creación de proyecto"""
        self.assertIsInstance(self.project, Project)
        self.assertEqual(self.project.title, 'Casa de Prueba')
    
    def test_project_slug_generation(self):
        """Verificar generación automática de slug"""
        self.assertIsNotNone(self.project.slug)
        self.assertTrue(len(self.project.slug) > 0)
        self.assertIn('casa-de-prueba', self.project.slug)
    
    def test_project_unique_slug(self):
        """Verificar slugs únicos para proyectos con mismo título"""
        arquitecto2 = User.objects.create_user(
            username='arquitecto2',
            email='arq2@vulcano.com',
            password='pass123'
        )
        arquitecto2.profile.role = 'arquitecto'
        arquitecto2.profile.save()
        
        project2 = Project.objects.create(
            title='Casa de Prueba',
            description='Otra descripción',
            category='residential',
            status='draft',
            location='Guadalajara, México',
            arquitecto=arquitecto2
        )
        self.assertNotEqual(self.project.slug, project2.slug)
    
    def test_project_categories(self):
        """Verificar todas las categorías disponibles"""
        categories = [
            'residential', 'commercial', 'cultural', 'educational',
            'healthcare', 'industrial', 'hospitality', 'interior', 'landscape'
        ]
        for category in categories:
            project = Project.objects.create(
                title=f'Proyecto {category}',
                description='Test',
                category=category,
                status='draft',
                location='Test Location',
                arquitecto=self.arquitecto
            )
            self.assertEqual(project.category, category)
    
    def test_project_status_choices(self):
        """Verificar estados de proyecto"""
        statuses = ['draft', 'in_progress', 'completed']
        for status in statuses:
            self.project.status = status
            self.project.save()
            self.assertEqual(self.project.status, status)
    
    def test_project_short_description(self):
        """Verificar propiedad short_description"""
        short = self.project.short_description
        self.assertIsInstance(short, str)
        self.assertTrue(len(short) <= 200)
    
    def test_project_clients_relationship(self):
        """Verificar relación ManyToMany con clientes"""
        self.project.clients.add(self.cliente)
        self.assertEqual(self.project.clients.count(), 1)
        self.assertIn(self.cliente, self.project.clients.all())
    
    def test_project_views_count(self):
        """Verificar contador de vistas"""
        initial_views = self.project.views_count
        self.project.views_count += 1
        self.project.save()
        self.assertEqual(self.project.views_count, initial_views + 1)
    
    def test_project_is_published_default(self):
        """Verificar valor por defecto de is_published"""
        self.assertTrue(self.project.is_published)
    
    def test_project_is_featured_default(self):
        """Verificar valor por defecto de is_featured"""
        self.assertFalse(self.project.is_featured)
    
    def test_project_str_method(self):
        """Verificar método __str__"""
        self.assertEqual(str(self.project), 'Casa de Prueba')
    
    def test_project_ordering(self):
        """Verificar ordenamiento por defecto"""
        project2 = Project.objects.create(
            title='Proyecto Z',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.arquitecto
        )
        projects = list(Project.objects.all())
        # Debe estar ordenado por -created_at
        self.assertEqual(projects[0], project2)  # Más reciente primero
    
    def test_project_get_main_image(self):
        """Verificar método get_main_image cuando no hay imágenes"""
        self.assertIsNone(self.project.get_main_image())
    
    def test_project_decimal_fields(self):
        """Verificar campos decimales"""
        self.assertIsInstance(self.project.area, Decimal)
        self.assertIsInstance(self.project.budget, Decimal)
        self.assertEqual(self.project.area, Decimal('350.50'))
    
    def test_project_date_validation(self):
        """Verificar validación de fechas"""
        # End date debe ser después de start date
        self.assertGreater(self.project.end_date, self.project.start_date)


class ProjectImageModelTest(TestCase):
    """Tests para el modelo ProjectImage"""
    
    def setUp(self):
        """Configuración inicial"""
        arquitecto = User.objects.create_user(
            username='arq',
            email='arq@test.com',
            password='pass'
        )
        self.project = Project.objects.create(
            title='Proyecto Test',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=arquitecto
        )
    
    def test_project_image_creation(self):
        """Verificar creación de imagen de proyecto"""
        # No podemos crear archivo real en test, verificamos estructura
        image = ProjectImage(
            project=self.project,
            caption='Test Image',
            is_main=True,
            order=0
        )
        self.assertEqual(image.project, self.project)
        self.assertTrue(image.is_main)
        self.assertEqual(image.order, 0)
    
    def test_project_image_ordering(self):
        """Verificar ordenamiento de imágenes"""
        # La metadata indica ordering por ['order', 'created_at']
        self.assertEqual(ProjectImage._meta.ordering, ['order', 'created_at'])
    
    def test_project_image_str_method(self):
        """Verificar método __str__"""
        image = ProjectImage(
            project=self.project,
            caption='Test Caption'
        )
        expected = f"{self.project.title} - Test Caption"
        self.assertEqual(str(image), expected)


class MessageModelTest(TestCase):
    """Tests para el modelo Message"""
    
    def setUp(self):
        """Configuración inicial"""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='pass'
        )
        
        arquitecto = User.objects.create_user(
            username='arq',
            email='arq@test.com',
            password='pass'
        )
        self.project = Project.objects.create(
            title='Proyecto Test',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=arquitecto
        )
    
    def test_message_creation(self):
        """Verificar creación de mensaje"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test Subject',
            body='Test message body'
        )
        self.assertIsInstance(message, Message)
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.recipient, self.recipient)
    
    def test_message_with_project(self):
        """Verificar mensaje asociado a proyecto"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='About Project',
            body='Message about project',
            project=self.project
        )
        self.assertEqual(message.project, self.project)
    
    def test_message_is_read_default(self):
        """Verificar valor por defecto de is_read"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test',
            body='Test'
        )
        self.assertFalse(message.is_read)
    
    def test_message_str_method(self):
        """Verificar método __str__"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test Subject',
            body='Test'
        )
        expected = f"{self.sender.username} → {self.recipient.username}: Test Subject"
        self.assertEqual(str(message), expected)
    
    def test_message_ordering(self):
        """Verificar ordenamiento por defecto"""
        message1 = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Message 1',
            body='Body 1'
        )
        message2 = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Message 2',
            body='Body 2'
        )
        messages = list(Message.objects.all())
        # Debe estar ordenado por -created_at
        self.assertEqual(messages[0], message2)  # Más reciente primero
    
    def test_message_related_names(self):
        """Verificar related_names para relaciones"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test',
            body='Test'
        )
        
        # Verificar que el sender puede acceder a mensajes enviados
        self.assertIn(message, self.sender.sent_messages.all())
        
        # Verificar que el recipient puede acceder a mensajes recibidos
        self.assertIn(message, self.recipient.received_messages.all())


class ModelValidationTest(TestCase):
    """Tests de validación de modelos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
    
    def test_project_required_fields(self):
        """Verificar campos obligatorios en Project"""
        # Intentar crear proyecto sin campos requeridos debe fallar
        with self.assertRaises(Exception):
            Project.objects.create(
                title='',  # Título vacío
                description='Test'
            )
    
    def test_profile_role_choices(self):
        """Verificar que solo se aceptan roles válidos"""
        profile = self.user.profile
        valid_roles = ['admin', 'arquitecto', 'cliente']
        
        for role in valid_roles:
            profile.role = role
            profile.save()
            self.assertEqual(profile.role, role)
    
    def test_project_title_max_length(self):
        """Verificar longitud máxima de título"""
        long_title = 'A' * 101  # Excede el límite de 100 caracteres
        with self.assertRaises(Exception):
            Project.objects.create(
                title=long_title,
                description='Test',
                category='residential',
                status='draft',
                location='Test',
                arquitecto=self.user
            )


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_models'])