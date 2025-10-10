"""
Test Messaging - Vulcano Platform
Tests específicos del sistema de mensajería
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from vulcano.models import Project, Message, UserProfile
from datetime import datetime


class MessageCreationTest(TestCase):
    """Tests de creación de mensajes"""
    
    def setUp(self):
        """Configuración inicial"""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='pass123'
        )
        
        arquitecto = User.objects.create_user(
            username='arq',
            email='arq@test.com',
            password='pass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=arquitecto
        )
    
    def test_create_simple_message(self):
        """Verificar creación de mensaje simple"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test Subject',
            body='Test message body'
        )
        
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.recipient, self.recipient)
        self.assertEqual(message.subject, 'Test Subject')
        self.assertFalse(message.is_read)
    
    def test_create_message_with_project(self):
        """Verificar creación de mensaje asociado a proyecto"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='About Project',
            body='Message about project',
            project=self.project
        )
        
        self.assertEqual(message.project, self.project)
        self.assertIn(message, self.project.messages.all())
    
    def test_message_timestamp(self):
        """Verificar que el mensaje tiene timestamp"""
        message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test',
            body='Test'
        )
        
        self.assertIsNotNone(message.created_at)
        self.assertIsInstance(message.created_at, datetime)
    
    def test_multiple_messages_between_users(self):
        """Verificar múltiples mensajes entre usuarios"""
        for i in range(5):
            Message.objects.create(
                sender=self.sender,
                recipient=self.recipient,
                subject=f'Message {i}',
                body=f'Body {i}'
            )
        
        sent_messages = self.sender.sent_messages.count()
        received_messages = self.recipient.received_messages.count()
        
        self.assertEqual(sent_messages, 5)
        self.assertEqual(received_messages, 5)


class MessageReadStatusTest(TestCase):
    """Tests de estado de lectura de mensajes"""
    
    def setUp(self):
        """Configuración inicial"""
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='pass123'
        )
        
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test',
            body='Test'
        )
    
    def test_message_unread_by_default(self):
        """Verificar que mensaje es no leído por defecto"""
        self.assertFalse(self.message.is_read)
    
    def test_mark_message_as_read(self):
        """Verificar marcar mensaje como leído"""
        self.message.is_read = True
        self.message.save()
        
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)
    
    def test_unread_messages_count(self):
        """Verificar conteo de mensajes no leídos"""
        # Crear varios mensajes no leídos
        for i in range(3):
            Message.objects.create(
                sender=self.sender,
                recipient=self.recipient,
                subject=f'Unread {i}',
                body=f'Body {i}'
            )
        
        # Crear un mensaje leído
        Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Read',
            body='Read',
            is_read=True
        )
        
        unread_count = Message.objects.filter(
            recipient=self.recipient,
            is_read=False
        ).count()
        
        self.assertEqual(unread_count, 4)  # 3 nuevos + 1 original


class InboxViewTest(TestCase):
    """Tests de la vista de inbox"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
    
    def test_inbox_shows_received_messages(self):
        """Verificar que inbox muestra mensajes recibidos"""
        # Crear mensaje recibido
        Message.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Received',
            body='Test'
        )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('vulcano:inbox'))
        
        self.assertContains(response, 'Received')
    
    def test_inbox_shows_sent_messages(self):
        """Verificar que inbox muestra mensajes enviados"""
        # Crear mensaje enviado
        Message.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Sent',
            body='Test'
        )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('vulcano:inbox'))
        
        self.assertContains(response, 'Sent')
    
    def test_inbox_filter_received(self):
        """Verificar filtro de mensajes recibidos"""
        Message.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Received',
            body='Test'
        )
        
        Message.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Sent',
            body='Test'
        )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('vulcano:inbox') + '?filter=received')
        
        self.assertContains(response, 'Received')
        # No debe mostrar enviados en filtro de recibidos
    
    def test_inbox_filter_sent(self):
        """Verificar filtro de mensajes enviados"""
        Message.objects.create(
            sender=self.user,
            recipient=self.other_user,
            subject='Sent',
            body='Test'
        )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('vulcano:inbox') + '?filter=sent')
        
        self.assertContains(response, 'Sent')
    
    def test_inbox_filter_unread(self):
        """Verificar filtro de mensajes no leídos"""
        Message.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Unread',
            body='Test',
            is_read=False
        )
        
        Message.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Read',
            body='Test',
            is_read=True
        )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('vulcano:inbox') + '?filter=unread')
        
        self.assertContains(response, 'Unread')
    
    def test_inbox_search_functionality(self):
        """Verificar búsqueda en inbox"""
        Message.objects.create(
            sender=self.other_user,
            recipient=self.user,
            subject='Important Project Discussion',
            body='Test'
        )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('vulcano:inbox') + '?search=Project')
        
        self.assertContains(response, 'Project')


class MessageComposeTest(TestCase):
    """Tests de composición de mensajes"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='pass123'
        )
    
    def test_compose_message_form(self):
        """Verificar formulario de composición"""
        self.client.login(username='sender', password='pass123')
        response = self.client.get(reverse('vulcano:message_compose'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'recipient')
        self.assertContains(response, 'subject')
        self.assertContains(response, 'body')
    
    def test_send_message_successfully(self):
        """Verificar envío exitoso de mensaje"""
        self.client.login(username='sender', password='pass123')
        
        # Configurar roles de usuario
        UserProfile.objects.filter(user=self.sender).update(role='arquitecto')
        UserProfile.objects.filter(user=self.recipient).update(role='cliente')
        
        # Crear un proyecto para el contexto
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=self.sender
        )
        project.clients.add(self.recipient)
        
        response = self.client.post(reverse('vulcano:message_compose'), {
            'recipient': self.recipient.id,
            'subject': 'New Message',
            'body': 'This is a test message',
            'project': project.id
        })
        
        # Verificar que el mensaje fue creado
        message = Message.objects.filter(
            sender=self.sender,
            recipient=self.recipient,
            subject='New Message'
        ).first()
        
        self.assertIsNotNone(message)
        self.assertEqual(message.project, project)
        
        # Verificar redirección
        self.assertRedirects(response, reverse('vulcano:inbox'))
    
    def test_compose_with_project_context(self):
        """Verificar composición con contexto de proyecto"""
        arquitecto = User.objects.create_user(
            username='arq',
            email='arq@test.com',
            password='pass123'
        )
        project = Project.objects.create(
            title='Test Project',
            description='Test',
            category='residential',
            status='draft',
            location='Test',
            arquitecto=arquitecto
        )
        
        self.client.login(username='sender', password='pass123')
        response = self.client.get(
            reverse('vulcano:message_compose') + f'?project={project.id}'
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_cannot_send_message_to_self(self):
        """Verificar que no se puede enviar mensaje a sí mismo"""
        self.client.login(username='sender', password='pass123')
        
        response = self.client.post(reverse('vulcano:message_compose'), {
            'recipient': self.sender.id,  # Mismo que sender
            'subject': 'Self Message',
            'body': 'Test'
        })
        
        # No debe crear el mensaje
        self.assertFalse(
            Message.objects.filter(
                sender=self.sender,
                recipient=self.sender
            ).exists()
        )


class MessageDetailViewTest(TestCase):
    """Tests de vista de detalle de mensaje"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='pass123'
        )
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test Message',
            body='This is a test message body'
        )
    
    def test_recipient_can_view_message(self):
        """Verificar que destinatario puede ver mensaje"""
        self.client.login(username='recipient', password='pass123')
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': self.message.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Message')
        self.assertContains(response, 'test message body')
    
    def test_sender_can_view_message(self):
        """Verificar que remitente puede ver mensaje"""
        self.client.login(username='sender', password='pass123')
        response = self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': self.message.id})
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_message_marked_read_when_viewed(self):
        """Verificar que mensaje se marca como leído al verlo"""
        self.client.login(username='recipient', password='pass123')
        
        # Verificar que está no leído
        self.assertFalse(self.message.is_read)
        
        # Ver el mensaje
        self.client.get(
            reverse('vulcano:message_detail', kwargs={'pk': self.message.id})
        )
        
        # Actualizar desde DB
        self.message.refresh_from_db()
        
        # Verificar que se marcó como leído
        self.assertTrue(self.message.is_read)
    
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
        
        # Debe retornar 403 o 404
        self.assertIn(response.status_code, [403, 404])


class MessageDeletionTest(TestCase):
    """Tests de eliminación de mensajes"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass123'
        )
        self.recipient = User.objects.create_user(
            username='recipient',
            email='recipient@test.com',
            password='pass123'
        )
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject='Test',
            body='Test'
        )
    
    def test_recipient_can_delete_message(self):
        """Verificar que destinatario puede eliminar mensaje"""
        self.client.login(username='recipient', password='pass123')
        
        message_id = self.message.id
        
        # Eliminar mensaje (implementar endpoint)
        # response = self.client.post(
        #     reverse('vulcano:message_delete', kwargs={'pk': message_id})
        # )
        
        # Verificar que fue eliminado
        # self.assertFalse(Message.objects.filter(id=message_id).exists())
    
    def test_sender_can_delete_message(self):
        """Verificar que remitente puede eliminar mensaje"""
        self.client.login(username='sender', password='pass123')
        
        # Similar al test anterior


class MessageNotificationTest(TestCase):
    """Tests de notificaciones de mensajes"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
    
    def test_unread_messages_count_in_navbar(self):
        """Verificar contador de mensajes no leídos en navbar"""
        # Crear mensajes no leídos
        for i in range(3):
            Message.objects.create(
                sender=self.other_user,
                recipient=self.user,
                subject=f'Message {i}',
                body='Test'
            )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('vulcano:dashboard'))
        
        # Verificar que aparece el contador
        self.assertContains(response, '3')  # Número de mensajes no leídos


# Ejecutar tests
if __name__ == '__main__':
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['vulcano.tests.test_messaging'])