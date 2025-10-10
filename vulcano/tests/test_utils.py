"""
Test Utils - Vulcano Platform
Tests de utilidades y funciones auxiliares
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.text import slugify
from vulcano.models import Project
from datetime import date, timedelta
import re


class SlugGenerationTest(TestCase):
    """Tests de generación de slugs"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
    
    def test_slug_generation_simple_title(self):
        """Verificar generación de slug con título simple"""
        project = Project.objects.create(
            title='Casa Moderna',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user
        )
        
        self.assertIsNotNone(project.slug)
        self.assertIn('casa-moderna', project.slug)
    
    def test_slug_generation_with_special_characters(self):
        """Verificar generación de slug con caracteres especiales"""
        project = Project.objects.create(
            title='Casa Moderna (Diseño 2024) - Versión Final',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user
        )
        
        # El slug debe limpiar caracteres especiales
        self.assertNotIn('(', project.slug)
        self.assertNotIn(')', project.slug)
        self.assertNotIn('-', project.slug[-1])  # No debe terminar en guion
    
    def test_slug_uniqueness(self):
        """Verificar unicidad de slugs"""
        project1 = Project.objects.create(
            title='Casa Moderna',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user
        )
        
        # Crear otro usuario para probar unicidad de slugs
        other_user = User.objects.create_user(
            username='other_architect',
            email='other@test.com',
            password='pass123'
        )
        project2 = Project.objects.create(
            title='Casa Moderna',
            description='Test', 
            category='residential',
            status='draft',
            location='Test',
            arquitecto=other_user
        )
        
        # Los slugs deben ser diferentes
        self.assertNotEqual(project1.slug, project2.slug)
    
    def test_slug_with_unicode_characters(self):
        """Verificar slug con caracteres unicode"""
        project = Project.objects.create(
            title='Casa México Diseño',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user
        )
        
        # Debe manejar caracteres acentuados
        self.assertIsNotNone(project.slug)


class DateValidationTest(TestCase):
    """Tests de validación de fechas"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
    
    def test_end_date_after_start_date(self):
        """Verificar que end_date es posterior a start_date"""
        project = Project.objects.create(
            title='Test',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        
        self.assertGreater(project.end_date, project.start_date)
    
    def test_project_duration(self):
        """Verificar cálculo de duración de proyecto"""
        start = date.today()
        end = start + timedelta(days=180)
        
        project = Project.objects.create(
            title='Test',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user,
            start_date=start,
            end_date=end
        )
        
        duration = (project.end_date - project.start_date).days
        self.assertEqual(duration, 180)


class StringRepresentationTest(TestCase):
    """Tests de representación en string de modelos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_str(self):
        """Verificar __str__ de UserProfile"""
        expected = "Test User (Cliente)"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_project_str(self):
        """Verificar __str__ de Project"""
        project = Project.objects.create(
            title='Casa Moderna',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.user
        )
        
        self.assertEqual(str(project), 'Casa Moderna')
    
    def test_message_str(self):
        """Verificar __str__ de Message"""
        from vulcano.models import Message
        
        other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
        
        message = Message.objects.create(
            sender=self.user,
            recipient=other_user,
            subject='Test Subject',
            body='Test'
        )
        
        expected = f"testuser → other: Test Subject"
        self.assertEqual(str(message), expected)


class ValidationUtilsTest(TestCase):
    """Tests de utilidades de validación"""
    
    def test_email_validation(self):
        """Verificar validación de emails"""
        valid_emails = [
            'test@example.com',
            'user.name@example.com',
            'user+tag@example.co.uk'
        ]
        
        invalid_emails = [
            'invalid',
            '@example.com',
            'user@',
            'user @example.com'
        ]
        
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        for email in valid_emails:
            try:
                validate_email(email)
            except ValidationError:
                self.fail(f"Email {email} debería ser válido")
        
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                validate_email(email)
    
    def test_phone_number_format(self):
        """Verificar formato de números telefónicos"""
        valid_phones = [
            '+52 55 1234 5678',
            '+1 555 123 4567',
            '5551234567'
        ]
        
        # Aquí implementarías validación de teléfono si la tienes
        for phone in valid_phones:
            # Verificar que el formato es aceptable
            self.assertIsInstance(phone, str)


class QueryOptimizationTest(TestCase):
    """Tests de optimización de queries"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
        
        # Crear varios proyectos
        for i in range(10):
            Project.objects.create(
                title=f'Project {i}',
                description='Test',
                category='residential',
                status='draft',
                location='Test',
                arquitecto=self.user
            )
    
    def test_select_related_optimization(self):
        """Verificar uso de select_related"""
        from django.test.utils import override_settings, CaptureQueriesContext
        from django.db import connection
        
        # Contamos queries sin select_related
        with CaptureQueriesContext(connection) as ctx_without:
            projects = Project.objects.all()
            for project in projects:
                _ = project.arquitecto.username
                
        queries_without = len(ctx_without)
            
        # Contamos queries con select_related
        with CaptureQueriesContext(connection) as ctx_with:
            projects = Project.objects.select_related('arquitecto').all()
            for project in projects:
                _ = project.arquitecto.username
                
        queries_with = len(ctx_with)
        
        # La versión optimizada debe hacer menos queries
        self.assertLess(queries_with, queries_without, 
                       f"select_related no optimizó las queries: sin={queries_without}, con={queries_with}")


class SecurityUtilsTest(TestCase):
    """Tests de utilidades de seguridad"""
    
    def test_password_hashing(self):
        """Verificar hash de contraseñas"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='plaintext123'
        )
        
        # La contraseña no debe estar en texto plano
        self.assertNotEqual(user.password, 'plaintext123')
        
        # Debe poder verificarse
        self.assertTrue(user.check_password('plaintext123'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_sql_injection_protection(self):
        """Verificar protección contra SQL injection"""
        # Django ORM protege automáticamente, pero verificar
        malicious_input = "'; DROP TABLE vulcano_project; --"
        
        # Intentar crear proyecto con input malicioso
        try:
            project = Project.objects.create(
                title=malicious_input,
                description='Test',
                category='residential',
                status='draft',
                location='Test',
                arquitecto=User.objects.create_user(
                    username='test',
                    email='test@test.com',
                    password='pass123'
                )
            )
            
            # Si llega aquí, el input fue escapado correctamente
            self.assertEqual(project.title, malicious_input)
        except Exception as e:
            self.fail(f"Error inesperado: {e}")


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_utils'])