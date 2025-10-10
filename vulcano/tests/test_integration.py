"""
Test Integration - Vulcano Platform
Tests de integración del sistema completo
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from vulcano.models import Project, Message, ProjectImage
from datetime import date, timedelta
from decimal import Decimal
import tempfile
from PIL import Image
import os


class CompleteUserJourneyTest(TestCase):
    """Tests del recorrido completo de usuario"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
    
    def test_arquitecto_complete_journey(self):
        """Verificar recorrido completo de arquitecto"""
        # 1. Registro
        response = self.client.post(reverse('vulcano:register'), {
            'username': 'arquitecto_test',
            'email': 'arq@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'Arquitecto',
            'last_name': 'Test',
            'role': 'arquitecto'
        })
        self.assertRedirects(response, reverse('vulcano:login'))
        
        # 2. Login
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'arquitecto_test',
            'password': 'ComplexPass123!'
        })
        self.assertRedirects(response, reverse('vulcano:dashboard'))
        
        # 3. Acceder a dashboard
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_arquitecto.html')
        
        # 4. Crear proyecto
        response = self.client.post(reverse('vulcano:project_create'), {
            'title': 'Casa Moderna',
            'description': 'Proyecto de casa moderna con diseño minimalista',
            'category': 'residential',
            'status': 'draft',
            'location': 'Ciudad de México, México',
            'area': Decimal('250.00'),
            'budget': Decimal('3000000.00'),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=180),
            'is_published': True
        })
        
        # 5. Verificar proyecto creado
        project = Project.objects.get(title='Casa Moderna')
        self.assertEqual(project.arquitecto.username, 'arquitecto_test')
        
        # 6. Editar proyecto
        response = self.client.post(
            reverse('vulcano:project_edit', kwargs={'slug': project.slug}),
            {
                'title': 'Casa Moderna Actualizada',
                'description': 'Descripción actualizada',
                'category': 'residential',
                'status': 'in_progress',
                'location': 'Ciudad de México, México',
                'is_published': True
            }
        )
        
        # 7. Ver perfil
        response = self.client.get(reverse('vulcano:profile'))
        self.assertEqual(response.status_code, 200)
        
        # 8. Logout
        response = self.client.get(reverse('vulcano:logout'))
        self.assertRedirects(response, reverse('vulcano:home'))
    
    def test_cliente_complete_journey(self):
        """Verificar recorrido completo de cliente"""
        # 1. Registro como cliente
        response = self.client.post(reverse('vulcano:register'), {
            'username': 'cliente_test',
            'email': 'cli@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'Cliente',
            'last_name': 'Test',
            'role': 'cliente'
        })
        
        # 2. Login
        self.client.post(reverse('vulcano:login'), {
            'username': 'cliente_test',
            'password': 'ComplexPass123!'
        })
        
        # 3. Acceder a dashboard
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_cliente.html')
        
        # 4. Ver proyectos públicos
        response = self.client.get(reverse('vulcano:home'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Acceder a inbox
        response = self.client.get(reverse('vulcano:inbox'))
        self.assertEqual(response.status_code, 200)


class ProjectWorkflowTest(TestCase):
    """Tests del flujo de trabajo de proyectos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
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
    
    def test_project_lifecycle(self):
        """Verificar ciclo de vida completo de proyecto"""
        self.client.login(username='arquitecto', password='pass123')
        
        # 1. Crear proyecto en draft
        project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            category='residential',
            status='draft',
            location='Test Location',
            arquitecto=self.arquitecto,
            is_published=False
        )
        
        self.assertEqual(project.status, 'draft')
        self.assertFalse(project.is_published)
        
        # 2. Actualizar a in_progress
        project.status = 'in_progress'
        project.save()
        self.assertEqual(project.status, 'in_progress')
        
        # 3. Publicar proyecto
        project.is_published = True
        project.save()
        self.assertTrue(project.is_published)
        
        # 4. Asignar cliente
        project.clients.add(self.cliente)
        self.assertIn(self.cliente, project.clients.all())
        
        # 5. Completar proyecto
        project.status = 'completed'
        project.save()
        self.assertEqual(project.status, 'completed')


class MessageWorkflowTest(TestCase):
    """Tests del flujo de mensajería"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
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
        
        self.project = Project.objects.create(
            title='Test Project',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.arquitecto
        )
    
    def test_complete_message_conversation(self):
        """Verificar conversación completa por mensajes"""
        # 1. Configurar proyecto y permisos
        self.project.is_published = True
        self.project.save()
        self.project.clients.add(self.cliente)
        
        # 2. Cliente envía mensaje inicial
        self.client.login(username='cliente', password='pass123')
        
        # Verificar que el mensaje no existe
        self.assertFalse(Message.objects.filter(subject='Consulta sobre proyecto').exists())
        
        post_data = {
            'recipient': self.arquitecto.id,
            'subject': 'Consulta sobre proyecto',
            'body': 'Hola, me interesa el proyecto',
            'project': self.project.id
        }
        
        response = self.client.post(reverse('vulcano:message_compose'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirección después de enviar
        
        # Ahora sí intentamos obtener el mensaje
        message1 = Message.objects.get(subject='Consulta sobre proyecto')
        self.assertEqual(message1.sender, self.cliente)
        self.assertEqual(message1.recipient, self.arquitecto)
        self.assertFalse(message1.is_read)
        
        # 2. Arquitecto recibe y lee el mensaje
        self.client.login(username='arquitecto', password='pass123')
        
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': message1.id})
        )
        
        message1.refresh_from_db()
        self.assertTrue(message1.is_read)
        
        # 3. Arquitecto responde
        response = self.client.post(reverse('vulcano:message_compose'), {
            'recipient': self.cliente.id,
            'subject': 'Re: Consulta sobre proyecto',
            'body': 'Gracias por tu interés, te contacto pronto',
            'project': self.project.id
        })
        
        message2 = Message.objects.get(subject='Re: Consulta sobre proyecto')
        self.assertEqual(message2.sender, self.arquitecto)
        self.assertEqual(message2.recipient, self.cliente)
        
        # 4. Cliente lee la respuesta
        self.client.login(username='cliente', password='pass123')
        
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': message2.id})
        )
        
        message2.refresh_from_db()
        self.assertTrue(message2.is_read)


class DatabaseIntegrityTest(TestCase):
    """Tests de integridad de base de datos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
    
    def test_cascade_delete_user(self):
        """Verificar eliminación en cascada al eliminar usuario"""
        # Crear proyecto
        project = Project.objects.create(
            title='Test',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user
        )
        
        project_id = project.id
        
        # Eliminar usuario
        self.user.delete()
        
        # Verificar que el proyecto también se eliminó (o se actualizó según configuración)
        # Dependiendo de on_delete configurado en el modelo
        self.assertFalse(Project.objects.filter(id=project_id).exists())
    
    def test_many_to_many_integrity(self):
        """Verificar integridad de relaciones ManyToMany"""
        arquitecto = User.objects.create_user(
            username='arq',
            email='arq@test.com',
            password='pass123'
        )
        
        project = Project.objects.create(
            title='Test',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=arquitecto
        )
        
        cliente = User.objects.create_user(
            username='cliente',
            email='cli@test.com',
            password='pass123'
        )
        
        # Asignar cliente
        project.clients.add(cliente)
        self.assertEqual(project.clients.count(), 1)
        
        # Eliminar cliente
        cliente.delete()
        
        # Verificar que la relación se eliminó
        self.assertEqual(project.clients.count(), 0)


class PerformanceTest(TestCase):
    """Tests de rendimiento básicos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.arquitecto = User.objects.create_user(
            username='arquitecto',
            email='arq@test.com',
            password='pass123'
        )
        self.arquitecto.profile.role = 'arquitecto'
        self.arquitecto.profile.save()
    
    def test_bulk_project_creation(self):
        """Verificar creación masiva de proyectos"""
        projects = []
        for i in range(50):
            projects.append(Project(
                title=f'Project {i}',
                description='Test',
                category='residential',
                status='draft',
                location='Test',
                arquitecto=self.arquitecto
            ))
        
        # Bulk create
        Project.objects.bulk_create(projects)
        
        # Verificar
        self.assertEqual(Project.objects.count(), 50)
    
    def test_home_page_load_with_many_projects(self):
        """Verificar carga de home con muchos proyectos"""
        # Crear múltiples proyectos
        for i in range(20):
            Project.objects.create(
                title=f'Project {i}',
                description='Test',
                category='residential',
                status='completed',
                location='Test',
                arquitecto=self.arquitecto,
                is_published=True
            )
        
        # Cargar home
        import time
        start_time = time.time()
        response = self.client.get(reverse('vulcano:home'))
        end_time = time.time()
        
        # Verificar que carga correctamente
        self.assertEqual(response.status_code, 200)
        
        # Verificar tiempo de carga (debe ser menor a 3 segundos)
        load_time = end_time - start_time
        self.assertLess(load_time, 3.0)


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_integration'])