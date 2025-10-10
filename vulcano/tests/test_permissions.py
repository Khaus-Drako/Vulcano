"""
Test Permissions - Vulcano Platform
Tests de permisos y autorización
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from vulcano.models import Project
from vulcano.tests.utils import TestClient
from vulcano.models import Project
from vulcano.tests.utils import TestClient


class RoleBasedAccessTest(TestCase):
    """Tests de acceso basado en roles"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        
        # Crear usuarios con diferentes roles
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()
        
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
        self.cliente.profile.role = 'cliente'
        self.cliente.profile.save()
        
        # Crear un proyecto del arquitecto
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            category='residential',
            status='draft',
            location='Test Location',
            arquitecto=self.arquitecto
        )
    
    def test_admin_can_access_admin_dashboard(self):
        """Verificar que admin puede acceder a su dashboard"""
        self.client.login(username='admin', password='pass123')
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_admin.html')
    
    def test_arquitecto_can_access_arquitecto_dashboard(self):
        """Verificar que arquitecto puede acceder a su dashboard"""
        self.client.login(username='arquitecto', password='pass123')
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_arquitecto.html')
    
    def test_cliente_can_access_cliente_dashboard(self):
        """Verificar que cliente puede acceder a su dashboard"""
        self.client.login(username='cliente', password='pass123')
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_cliente.html')
    
    def test_cliente_cannot_create_project(self):
        """Verificar que cliente no puede crear proyectos"""
        self.client.login(username='cliente', password='pass123')
        response = self.client.get(reverse('vulcano:project_create'))
        # Debe redirigir o retornar 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_arquitecto_can_create_project(self):
        """Verificar que arquitecto puede crear proyectos"""
        self.client.login(username='arquitecto', password='pass123')
        response = self.client.get(reverse('vulcano:project_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_can_create_project(self):
        """Verificar que admin puede crear proyectos"""
        self.client.login(username='admin', password='pass123')
        response = self.client.get(reverse('vulcano:project_create'))
        self.assertEqual(response.status_code, 200)


class ProjectOwnershipTest(TestCase):
    """Tests de propiedad de proyectos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        
        self.arquitecto1 = User.objects.create_user(
            username='arq1',
            email='arq1@test.com',
            password='pass123'
        )
        self.arquitecto1.profile.role = 'arquitecto'
        self.arquitecto1.profile.save()
        
        self.arquitecto2 = User.objects.create_user(
            username='arq2',
            email='arq2@test.com',
            password='pass123'
        )
        self.arquitecto2.profile.role = 'arquitecto'
        self.arquitecto2.profile.save()
        
        self.project = Project.objects.create(
            title='Test Project',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.arquitecto1
        )
    
    def test_owner_can_edit_project(self):
        """Verificar que el dueño puede editar su proyecto"""
        self.client.login(username='arq1', password='pass123')
        response = self.client.get(
            reverse('vulcano:project_edit', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_non_owner_cannot_edit_project(self):
        """Verificar que otro arquitecto no puede editar el proyecto"""
        self.client.login(username='arq2', password='pass123')
        response = self.client.get(
            reverse('vulcano:project_edit', kwargs={'slug': self.project.slug})
        )
        # Debe retornar 403 o redirigir
        self.assertIn(response.status_code, [302, 403])
    
    def test_owner_can_delete_project(self):
        """Verificar que el dueño puede eliminar su proyecto"""
        self.client.login(username='arq1', password='pass123')
        response = self.client.get(
            reverse('vulcano:project_delete', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_non_owner_cannot_delete_project(self):
        """Verificar que otro arquitecto no puede eliminar el proyecto"""
        self.client.login(username='arq2', password='pass123')
        response = self.client.get(
            reverse('vulcano:project_delete', kwargs={'slug': self.project.slug})
        )
        # Debe retornar 403 o redirigir
        self.assertIn(response.status_code, [302, 403])
    
    def test_admin_can_edit_any_project(self):
        """Verificar que admin puede editar cualquier proyecto"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123'
        )
        admin.profile.role = 'admin'
        admin.profile.save()
        
        self.client.login(username='admin', password='pass123')
        response = self.client.get(
            reverse('vulcano:project_edit', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)


class MessagePermissionsTest(TestCase):
    """Tests de permisos de mensajería"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='pass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='pass123'
        )
        
        from vulcano.models import Message
        self.message = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            subject='Test Message',
            body='Test body'
        )
    
    def test_sender_can_view_sent_message(self):
        """Verificar que el remitente puede ver su mensaje enviado"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': self.message.id})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_recipient_can_view_received_message(self):
        """Verificar que el destinatario puede ver su mensaje recibido"""
        self.client.login(username='user2', password='pass123')
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': self.message.id})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_other_user_cannot_view_message(self):
        """Verificar que otro usuario no puede ver el mensaje"""
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
        
        self.client.login(username='other', password='pass123')
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': self.message.id})
        )
        # Debe retornar 403 o redirigir
        self.assertIn(response.status_code, [302, 403, 404])


class AnonymousUserAccessTest(TestCase):
    """Tests de acceso de usuarios anónimos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = TestClient()
        
        arquitecto = User.objects.create_user(
            username='arq',
            email='arq@test.com',
            password='pass123'
        )
        
        self.project = Project.objects.create(
            title='Public Project',
            description='Test',
            category='residential',
            status='completed',
            location='Test',
            arquitecto=arquitecto,
            is_published=True
        )
    
    def test_anonymous_can_view_home(self):
        """Verificar que usuario anónimo puede ver home"""
        response = self.client.get(reverse('vulcano:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_anonymous_can_view_published_project(self):
        """Verificar que usuario anónimo puede ver proyecto publicado"""
        response = self.client.get(
            reverse('vulcano:project_detail', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_anonymous_cannot_access_dashboard(self):
        """Verificar que usuario anónimo no puede acceder a dashboard"""
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_anonymous_cannot_access_inbox(self):
        """Verificar que usuario anónimo no puede acceder a mensajes"""
        response = self.client.get(reverse('vulcano:inbox'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_anonymous_cannot_create_project(self):
        """Verificar que usuario anónimo no puede crear proyectos"""
        response = self.client.get(reverse('vulcano:project_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_permissions'])