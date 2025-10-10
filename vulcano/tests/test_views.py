"""
Test Views - Vulcano Platform
Tests para todas las vistas de la aplicación
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from vulcano.models import Project, Message, ProjectImage
from decimal import Decimal
from datetime import date, timedelta


class HomeViewTest(TestCase):
    """Tests para la vista home"""
    
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
    
    def test_home_view_status_code(self):
        """Verificar que home carga correctamente"""
        response = self.client.get(reverse('vulcano:home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_view_uses_correct_template(self):
        """Verificar template correcto"""
        response = self.client.get(reverse('vulcano:home'))
        self.assertTemplateUsed(response, 'home.html')
    
    def test_home_view_context_projects(self):
        """Verificar contexto con proyectos"""
        project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            category='residential',
            status='completed',
            location='Test Location',
            arquitecto=self.arquitecto,
            is_published=True
        )
        
        response = self.client.get(reverse('vulcano:home'))
        self.assertIn('projects', response.context)
        self.assertIn(project, response.context['projects'])
    
    def test_home_view_only_published_projects(self):
        """Verificar que solo muestra proyectos publicados"""
        published = Project.objects.create(
            title='Published',
            description='Test',
            category='residential',
            status='completed',
            location='Test',
            arquitecto=self.arquitecto,
            is_published=True
        )
        
        draft = Project.objects.create(
            title='Draft',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.arquitecto,
            is_published=False
        )
        
        response = self.client.get(reverse('vulcano:home'))
        projects = response.context['projects']
        
        self.assertIn(published, projects)
        self.assertNotIn(draft, projects)
    
    def test_home_view_featured_projects(self):
        """Verificar proyectos destacados"""
        featured = Project.objects.create(
            title='Featured',
            description='Test',
            category='residential',
            status='completed',
            location='Test',
            arquitecto=self.arquitecto,
            is_published=True,
            is_featured=True
        )
        
        response = self.client.get(reverse('vulcano:home'))
        self.assertIn('featured_projects', response.context)
        self.assertIn(featured, response.context['featured_projects'])


class ProjectDetailViewTest(TestCase):
    """Tests para la vista de detalle de proyecto"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.arquitecto = User.objects.create_user(
            username='arquitecto',
            email='arq@test.com',
            password='pass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            category='residential',
            status='completed',
            location='Test Location',
            arquitecto=self.arquitecto,
            is_published=True
        )
    
    def test_project_detail_status_code(self):
        """Verificar que detalle carga correctamente"""
        response = self.client.get(
            reverse('vulcano:project_detail', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_project_detail_uses_correct_template(self):
        """Verificar template correcto"""
        response = self.client.get(
            reverse('vulcano:project_detail', kwargs={'slug': self.project.slug})
        )
        self.assertTemplateUsed(response, 'projects/project_detail.html')
    
    def test_project_detail_404_for_invalid_slug(self):
        """Verificar 404 para slug inválido"""
        response = self.client.get(
            reverse('vulcano:project_detail', kwargs={'slug': 'invalid-slug'})
        )
        self.assertEqual(response.status_code, 404)
    
    def test_project_detail_increment_views(self):
        """Verificar que incrementa el contador de vistas"""
        initial_views = self.project.views_count
        self.client.get(
            reverse('vulcano:project_detail', kwargs={'slug': self.project.slug})
        )
        self.project.refresh_from_db()
        self.assertEqual(self.project.views_count, initial_views + 1)
    
    def test_project_detail_context_data(self):
        """Verificar datos en contexto"""
        response = self.client.get(
            reverse('vulcano:project_detail', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.context['project'], self.project)
        self.assertIn('project_images', response.context)
        self.assertIn('related_projects', response.context)


class AuthenticationViewsTest(TestCase):
    """Tests para vistas de autenticación"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_login_view_get(self):
        """Verificar que login GET carga correctamente"""
        response = self.client.get(reverse('vulcano:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')
    
    def test_login_view_post_valid(self):
        """Verificar login exitoso"""
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('vulcano:dashboard'))
    
    def test_login_view_post_invalid(self):
        """Verificar login fallido con credenciales incorrectas"""
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')
    
    def test_logout_view(self):
        """Verificar logout"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('vulcano:logout'))
        self.assertRedirects(response, reverse('vulcano:home'))
    
    def test_register_view_get(self):
        """Verificar que registro GET carga correctamente"""
        response = self.client.get(reverse('vulcano:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')
    
    def test_register_view_post_valid(self):
        """Verificar registro exitoso"""
        response = self.client.post(reverse('vulcano:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente'
        })
        
        # Verificar que el usuario fue creado
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Verificar redirección
        self.assertRedirects(response, reverse('vulcano:login'))


class DashboardViewsTest(TestCase):
    """Tests para vistas de dashboard"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Usuario administrador
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123'
        )
        self.admin.profile.role = 'admin'
        self.admin.profile.save()
        
        # Usuario arquitecto
        self.arquitecto = User.objects.create_user(
            username='arquitecto',
            email='arq@test.com',
            password='pass123'
        )
        self.arquitecto.profile.role = 'arquitecto'
        self.arquitecto.profile.save()
        
        # Usuario cliente
        self.cliente = User.objects.create_user(
            username='cliente',
            email='cli@test.com',
            password='pass123'
        )
        self.cliente.profile.role = 'cliente'
        self.cliente.profile.save()
    
    def test_dashboard_requires_login(self):
        """Verificar que dashboard requiere autenticación"""
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertRedirects(
            response,
            f"{reverse('vulcano:login')}?next={reverse('vulcano:dashboard')}"
        )
    
    def test_dashboard_admin_redirect(self):
        """Verificar redirección correcta para admin"""
        self.client.login(username='admin', password='pass123')
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_admin.html')
    
    def test_dashboard_arquitecto_redirect(self):
        """Verificar redirección correcta para arquitecto"""
        self.client.login(username='arquitecto', password='pass123')
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_arquitecto.html')
    
    def test_dashboard_cliente_redirect(self):
        """Verificar redirección correcta para cliente"""
        self.client.login(username='cliente', password='pass123')
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/portal_cliente.html')


class ProjectCRUDViewsTest(TestCase):
    """Tests para vistas CRUD de proyectos"""
    
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
            description='Test Description',
            category='residential',
            status='draft',
            location='Test Location',
            arquitecto=self.arquitecto
        )
    
    def test_project_create_requires_login(self):
        """Verificar que crear proyecto requiere login"""
        response = self.client.get(reverse('vulcano:project_create'))
        self.assertRedirects(
            response,
            f"{reverse('vulcano:login')}?next={reverse('vulcano:project_create')}"
        )
    
    def test_project_create_requires_arquitecto(self):
        """Verificar que solo arquitectos pueden crear proyectos"""
        self.client.login(username='cliente', password='pass123')
        response = self.client.get(reverse('vulcano:project_create'))
        # Debe redirigir o mostrar error 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_project_create_get_arquitecto(self):
        """Verificar que arquitecto puede acceder a formulario de creación"""
        self.client.login(username='arquitecto', password='pass123')
        response = self.client.get(reverse('vulcano:project_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_form.html')
    
    def test_project_edit_requires_owner(self):
        """Verificar que solo el arquitecto dueño puede editar"""
        other_arq = User.objects.create_user(
            username='other_arq',
            email='other@test.com',
            password='pass123'
        )
        other_arq.profile.role = 'arquitecto'
        other_arq.profile.save()
        
        self.client.login(username='other_arq', password='pass123')
        response = self.client.get(
            reverse('vulcano:project_edit', kwargs={'slug': self.project.slug})
        )
        # Debe retornar 403 o redirigir
        self.assertIn(response.status_code, [302, 403])
    
    def test_project_delete_requires_owner(self):
        """Verificar que solo el dueño puede eliminar"""
        self.client.login(username='arquitecto', password='pass123')
        response = self.client.get(
            reverse('vulcano:project_delete', kwargs={'slug': self.project.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_delete.html')


class MessagingViewsTest(TestCase):
    """Tests para vistas de mensajería"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
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
    
    def test_inbox_requires_login(self):
        """Verificar que inbox requiere login"""
        response = self.client.get(reverse('vulcano:inbox'))
        self.assertRedirects(
            response,
            f"{reverse('vulcano:login')}?next={reverse('vulcano:inbox')}"
        )
    
    def test_inbox_view_authenticated(self):
        """Verificar inbox para usuario autenticado"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('vulcano:inbox'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'messaging/inbox.html')
    
    def test_compose_message_requires_login(self):
        """Verificar que enviar mensaje requiere login"""
        response = self.client.get(reverse('vulcano:message_compose'))
        self.assertRedirects(
            response,
            f"{reverse('vulcano:login')}?next={reverse('vulcano:message_compose')}"
        )
    
    def test_compose_message_get(self):
        """Verificar GET de formulario de mensaje"""
        self.client.login(username='user1', password='pass123')
        response = self.client.get(reverse('vulcano:message_compose'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'messaging/compose.html')
    
    def test_message_detail_requires_login(self):
        """Verificar que detalle de mensaje requiere login"""
        message = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            subject='Test',
            body='Test body'
        )
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': message.id})
        )
        self.assertEqual(response.status_code, 302)


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_views'])