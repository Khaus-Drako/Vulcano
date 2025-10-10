"""
Test Authentication - Vulcano Platform
Tests avanzados de autenticación y sesiones
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone


class AuthenticationFlowTest(TestCase):
    """Tests del flujo completo de autenticación"""
    
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
    
    def test_complete_login_flow(self):
        """Verificar flujo completo de login"""
        # 1. Usuario no autenticado no puede acceder a dashboard
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 302)
        
        # 2. Usuario intenta login
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # 3. Verificar redirección exitosa
        self.assertRedirects(response, reverse('vulcano:dashboard'))
        
        # 4. Verificar que ahora puede acceder a dashboard
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Verificar que el usuario está en el contexto
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user, self.user)
    
    def test_login_session_creation(self):
        """Verificar creación de sesión al hacer login"""
        # Contar sesiones antes de login
        sessions_before = Session.objects.count()
        
        # Hacer login
        self.client.login(username='testuser', password='testpass123')
        
        # Verificar que se creó una sesión
        sessions_after = Session.objects.count()
        self.assertGreater(sessions_after, sessions_before)
    
    def test_logout_session_deletion(self):
        """Verificar eliminación de sesión al hacer logout"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Verificar que está autenticado
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        
        # Logout
        self.client.logout()
        
        # Verificar que ya no está autenticado
        response = self.client.get(reverse('vulcano:dashboard'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.status_code, 302)
    
    def test_login_with_next_parameter(self):
        """Verificar redirección con parámetro next"""
        # Intentar acceder a una página protegida
        protected_url = reverse('vulcano:profile')
        response = self.client.get(protected_url)
        
        # Debe redirigir a login con next
        expected_url = f"{reverse('vulcano:login')}?next={protected_url}"
        self.assertRedirects(response, expected_url)
        
        # Login
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        }, follow=True)
        
        # Debe redirigir al dashboard (por defecto)
        self.assertEqual(response.status_code, 200)
    
    def test_login_case_sensitive_username(self):
        """Verificar que username es case-sensitive"""
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'TESTUSER',  # Mayúsculas
            'password': 'testpass123'
        })
        
        # Debe fallar porque username no coincide
        self.assertEqual(response.status_code, 200)  # Se queda en página de login
    
    def test_multiple_failed_login_attempts(self):
        """Verificar múltiples intentos de login fallidos"""
        for i in range(5):
            response = self.client.post(reverse('vulcano:login'), {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_inactive_user(self):
        """Verificar que usuario inactivo no puede hacer login"""
        # Desactivar usuario
        self.user.is_active = False
        self.user.save()
        
        # Intentar login
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # No debe poder autenticarse
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RegistrationFlowTest(TestCase):
    """Tests del flujo de registro"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
    
    def test_complete_registration_flow(self):
        """Verificar flujo completo de registro"""
        # 1. Acceder a página de registro
        response = self.client.get(reverse('vulcano:register'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Enviar formulario de registro
        response = self.client.post(reverse('vulcano:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'cliente',
            'phone': '+52 55 1234 5678',
            'company': 'Test Company'
        })
        
        # 3. Verificar redirección a login
        self.assertRedirects(response, reverse('vulcano:login'))
        
        # 4. Verificar que el usuario fue creado
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # 5. Verificar perfil creado
        user = User.objects.get(username='newuser')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'cliente')
        self.assertEqual(user.profile.phone, '+52 55 1234 5678')
        
        # 6. Intentar login con el nuevo usuario
        response = self.client.post(reverse('vulcano:login'), {
            'username': 'newuser',
            'password': 'ComplexPass123!'
        })
        self.assertRedirects(response, reverse('vulcano:dashboard'))
    
    def test_registration_creates_profile_automatically(self):
        """Verificar que el registro crea perfil automáticamente"""
        self.client.post(reverse('vulcano:register'), {
            'username': 'autouser',
            'email': 'auto@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'Auto',
            'last_name': 'User',
            'role': 'arquitecto'
        })
        
        user = User.objects.get(username='autouser')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, 'arquitecto')


class SessionManagementTest(TestCase):
    """Tests de gestión de sesiones"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_session_data_persistence(self):
        """Verificar persistencia de datos en sesión"""
        self.client.login(username='testuser', password='testpass123')
        
        # Agregar datos a la sesión
        session = self.client.session
        session['test_key'] = 'test_value'
        session.save()
        
        # Hacer otra petición
        response = self.client.get(reverse('vulcano:dashboard'))
        
        # Verificar que los datos persisten
        self.assertEqual(response.wsgi_request.session.get('test_key'), 'test_value')
    
    def test_session_expiry(self):
        """Verificar configuración de expiración de sesión"""
        self.client.login(username='testuser', password='testpass123')
        
        # Verificar que la sesión tiene una fecha de expiración
        session = self.client.session
        self.assertIsNotNone(session.get_expiry_date())


class PasswordSecurityTest(TestCase):
    """Tests de seguridad de contraseñas"""
    
    def test_password_hashing(self):
        """Verificar que las contraseñas se almacenan hasheadas"""
        user = User.objects.create_user(
            username='hashtest',
            email='hash@test.com',
            password='plaintextpassword'
        )
        
        # La contraseña no debe estar en texto plano
        self.assertNotEqual(user.password, 'plaintextpassword')
        
        # Debe poder verificar la contraseña
        self.assertTrue(user.check_password('plaintextpassword'))
    
    def test_password_validation(self):
        """Verificar validación de contraseñas débiles"""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        # Contraseña muy corta
        with self.assertRaises(ValidationError):
            validate_password('123')
        
        # Contraseña muy común
        with self.assertRaises(ValidationError):
            validate_password('password')
        
        # Contraseña solo numérica
        with self.assertRaises(ValidationError):
            validate_password('12345678')


class CSRFProtectionTest(TestCase):
    """Tests de protección CSRF"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_csrf_token_required_for_login(self):
        """Verificar que se requiere token CSRF para login"""
        # Intentar login sin CSRF token (usando enforce_csrf_checks)
        from django.test import Client as CSRFClient
        csrf_client = CSRFClient(enforce_csrf_checks=True)
        
        response = csrf_client.post(reverse('vulcano:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Debe fallar por falta de CSRF token
        self.assertEqual(response.status_code, 403)
    
    def test_csrf_token_in_forms(self):
        """Verificar que los formularios incluyen token CSRF"""
        response = self.client.get(reverse('vulcano:login'))
        self.assertContains(response, 'csrfmiddlewaretoken')


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_authentication'])