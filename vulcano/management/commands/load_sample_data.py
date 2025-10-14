"""
Management Command para cargar datos de ejemplo en Vulcano.
Crea usuarios, proyectos, imágenes y mensajes de prueba.

Uso:
    python manage.py load_sample_data
    python manage.py load_sample_data --clear  # Limpia datos anteriores
"""

import os
import requests
from io import BytesIO
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone
from vulcano.models import UserProfile, Project, ProjectImage, Message
import random


class Command(BaseCommand):
    help = 'Carga datos de ejemplo para el proyecto Vulcano'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Elimina todos los datos existentes antes de cargar nuevos',
        )
        parser.add_argument(
            '--no-images',
            action='store_true',
            help='No descarga imágenes reales (más rápido para pruebas)',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('  VULCANO - Carga de Datos de Ejemplo'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('🗑️  Limpiando datos existentes...'))
            self.clear_data()
        
        self.download_images = not options['no_images']
        
        try:
            with transaction.atomic():
                self.stdout.write('👥 Creando usuarios...')
                users = self.create_users()
                
                self.stdout.write('🏗️  Creando proyectos...')
                projects = self.create_projects(users)
                
                if self.download_images:
                    self.stdout.write('📸 Descargando y asociando imágenes...')
                    self.create_project_images(projects)
                else:
                    self.stdout.write(self.style.WARNING('⚠️  Omitiendo descarga de imágenes'))
                
                self.stdout.write('💬 Creando mensajes...')
                self.create_messages(users, projects)
                
            self.stdout.write(self.style.SUCCESS('' + '=' * 70))
            self.stdout.write(self.style.SUCCESS('✅ Datos de ejemplo cargados exitosamente'))
            self.stdout.write(self.style.SUCCESS('=' * 70))
            
            self.display_summary(users, projects)
            
        except Exception as e:
            raise CommandError(f'Error al cargar datos: {str(e)}')
    
    def clear_data(self):
        """Elimina todos los datos de prueba."""
        Message.objects.all().delete()
        ProjectImage.objects.all().delete()
        Project.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('   ✓ Datos eliminados'))
    
    def create_users(self):
        """Crea usuarios de ejemplo con diferentes roles."""
        users = {}

        # Administrador
        admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@ihman.com',
                    'first_name': 'Jhonny Juan',
                    'last_name': 'Rugel Guevara',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
        if created:
                admin_user.set_password('admin123')
                admin_user.save()

        profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        profile.role = 'admin'
        profile.phone = '+51 997 937 653'
        profile.company = 'Ihman'
        profile.bio = 'Administrador principal de la plataforma Ihman.'
        profile.save()

        users['admin'] = admin_user
        self.stdout.write(f'   ✓ Admin: {admin_user.username}')
        
        # Arquitectos
        arquitectos_data = [
            {
                'username': 'jhilariop',
                'email': 'Jhostyn.Hilario@ihman.com',
                'first_name': 'Jhostyn Alfredo',
                'last_name': 'Hilario Peves',
                'phone': '+51 941 016 940',
                'company': 'López Arquitectos',
                'bio': 'Arquitecta especializada en diseño de interiores con más de 5 años de experiencia. Enfoque en sostenibilidad y espacios minimalistas.'
            },
        ]

        users['arquitectos'] = []

        for data in arquitectos_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                }
            )

            if created:
                user.set_password('arquitecto123')
                user.save()

            # Evita duplicar perfiles (gracias a la señal post_save)
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'arquitecto',
                    'phone': data['phone'],
                    'company': data['company'],
                    'bio': data['bio']
                }
            )

            # Si ya existía, actualiza los campos por consistencia
            profile.role = 'arquitecto'
            profile.phone = data['phone']
            profile.company = data['company']
            profile.bio = data['bio']
            profile.save()

            users['arquitectos'].append(user)
            self.stdout.write(f'   ✓ Arquitecto: {user.username}')
        
        # Clientes
        clientes_data = [
            {
                'username': 'cliente1',
                'email': 'roberto.garcia@email.com',
                'first_name': 'Roberto',
                'last_name': 'García Pérez',
                'phone': '+52 55 5678 9012',
                'company': 'Inversiones RGP',
            },
            {
                'username': 'cliente2',
                'email': 'laura.mendez@empresa.com',
                'first_name': 'Laura',
                'last_name': 'Méndez Ortiz',
                'phone': '+52 55 6789 0123',
                'company': 'Constructora LMO',
            },
            {
                'username': 'cliente3',
                'email': 'carlos.rivera@inversiones.mx',
                'first_name': 'Carlos',
                'last_name': 'Rivera Domínguez',
                'phone': '+52 55 7890 1234',
                'company': 'Grupo Rivera',
            },
            {
                'username': 'cliente4',
                'email': 'sofia.morales@corporativo.com',
                'first_name': 'Sofía',
                'last_name': 'Morales Castro',
                'phone': '+52 55 8901 2345',
                'company': 'Corporativo SMC',
            }
        ]

        users['clientes'] = []

        for data in clientes_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                }
            )

            if created:
                user.set_password('cliente123')
                user.save()

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'cliente',
                    'phone': data['phone'],
                    'company': data['company'],
                    'bio': f'Cliente de Vulcano desde {random.randint(2020, 2024)}'
                }
            )

            # Actualiza datos si ya existía
            profile.role = 'cliente'
            profile.phone = data['phone']
            profile.company = data['company']
            profile.bio = f'Cliente de Vulcano desde {random.randint(2020, 2024)}'
            profile.save()

            users['clientes'].append(user)
            self.stdout.write(f'   ✓ Cliente: {user.username}')

        return users
    
    def create_projects(self, users):
        """Crea proyectos de ejemplo."""
        projects = []
        
        proyectos_data = [
            {
                'title': 'Casa Minimalista Vista al Mar',
                'description': '''Proyecto residencial de lujo ubicado en la costa del Pacífico. 
                
Diseño arquitectónico contemporáneo que integra espacios amplios y abiertos con una conexión directa con el entorno natural. La casa cuenta con grandes ventanales de piso a techo que maximizan las vistas panorámicas al océano.

Características principales:
- Diseño bioclimático con orientación estratégica
- Materiales locales y sostenibles (piedra volcánica, madera certificada)
- Sistema de captación de agua pluvial
- Paneles solares integrados en la cubierta
- Terrazas escalonadas con jardines nativos
- Piscina infinity con borde visual hacia el mar
- Sistema de domótica avanzada

El proyecto busca un equilibrio perfecto entre modernidad, confort y respeto al medio ambiente, creando un espacio de vida único que celebra la arquitectura local contemporánea.''',
                'category': 'residential',
                'status': 'completed',
                'location': 'Puerto Vallarta, Jalisco, México',
                'area': 450.00,
                'budget': 12500000.00,
                'start_date': datetime(2022, 3, 15).date(),
                'end_date': datetime(2023, 8, 20).date(),
                'is_featured': True,
                'is_published': True,
            },
            {
                'title': 'Centro Cultural Metropolitano',
                'description': '''Complejo cultural de última generación diseñado para albergar múltiples disciplinas artísticas y promover la interacción comunitaria.

El diseño arquitectónico se caracteriza por:
- Fachada dinámica con paneles móviles que se adaptan a las condiciones climáticas
- Salas de exposición modulares con iluminación natural controlada
- Auditorio principal con capacidad para 800 personas
- Talleres y espacios de creación colaborativa
- Biblioteca multimedia de acceso público
- Plaza exterior con esculturas y áreas de descanso
- Accesibilidad universal en todos los niveles

Este proyecto representa un hito en la arquitectura cultural contemporánea de México, combinando funcionalidad, estética y compromiso social.''',
                'category': 'cultural',
                'status': 'in_progress',
                'location': 'Guadalajara, Jalisco, México',
                'area': 8500.00,
                'budget': 85000000.00,
                'start_date': datetime(2023, 6, 1).date(),
                'end_date': datetime(2025, 12, 31).date(),
                'is_featured': True,
                'is_published': True,
            },
            {
                'title': 'Edificio Corporativo Sustentable',
                'description': '''Torre de oficinas LEED Platinum con enfoque en sostenibilidad y bienestar laboral.

Características innovadoras:
- 18 pisos con certificación ambiental máxima
- Fachada de doble piel con ventilación natural
- Jardines verticales en cada nivel
- Sistema de recolección y tratamiento de aguas grises
- Estacionamiento subterráneo con cargadores para vehículos eléctricos
- Terrazas verdes con áreas de descanso y huertos urbanos
- Iluminación LED con sensores de presencia y luz natural
- Sistema HVAC de alta eficiencia energética

El edificio establece un nuevo estándar en arquitectura comercial sostenible en América Latina.''',
                'category': 'commercial',
                'status': 'in_progress',
                'location': 'Monterrey, Nuevo León, México',
                'area': 15000.00,
                'budget': 120000000.00,
                'start_date': datetime(2023, 1, 10).date(),
                'end_date': datetime(2025, 6, 30).date(),
                'is_featured': True,
                'is_published': True,
            },
            {
                'title': 'Residencia Familiar Contemporánea',
                'description': '''Casa unifamiliar que reinterpreta la arquitectura tradicional mexicana con un lenguaje contemporáneo.

Elementos destacados:
- Patio central como eje articulador de los espacios
- Muros de adobe revestidos con acabados modernos
- Celosías de madera que regulan la entrada de luz
- Cocina integrada al comedor y sala familiar
- 4 recámaras con baños completos
- Estudio con vista al jardín
- Alberca natural con sistema de filtración biológica
- Jardín con especies nativas de bajo mantenimiento

Un proyecto que honra las raíces arquitectónicas mexicanas mientras abraza la modernidad.''',
                'category': 'residential',
                'status': 'completed',
                'location': 'San Miguel de Allende, Guanajuato, México',
                'area': 380.00,
                'budget': 9500000.00,
                'start_date': datetime(2022, 9, 1).date(),
                'end_date': datetime(2023, 11, 15).date(),
                'is_featured': False,
                'is_published': True,
            },
            {
                'title': 'Hotel Boutique Ecoturístico',
                'description': '''Desarrollo hotelero de bajo impacto ambiental integrado al paisaje selvático de Chiapas.

Concepto y características:
- 24 suites independientes con diseño vernáculo contemporáneo
- Construcción con materiales locales (bambú, madera, piedra)
- Techos verdes y sistemas de captación pluvial
- Restaurante farm-to-table con huerto orgánico propio
- Spa con tratamientos naturales
- Miradores hacia la selva y cascadas
- Senderos ecológicos señalizados
- Planta de tratamiento de aguas residuales
- Energía solar y eólica

El proyecto busca un equilibrio entre confort turístico y preservación ambiental.''',
                'category': 'hospitality',
                'status': 'in_progress',
                'location': 'Palenque, Chiapas, México',
                'area': 5200.00,
                'budget': 45000000.00,
                'start_date': datetime(2023, 9, 15).date(),
                'end_date': datetime(2025, 3, 30).date(),
                'is_featured': False,
                'is_published': True,
            },
            {
                'title': 'Escuela Primaria Modelo',
                'description': '''Centro educativo diseñado bajo principios pedagógicos contemporáneos y sostenibilidad ambiental.

Espacios educativos innovadores:
- 12 aulas flexibles con mobiliario adaptable
- Biblioteca multimedia interactiva
- Laboratorios de ciencias y tecnología
- Talleres de artes y música
- Gimnasio multiusos
- Patio central con áreas verdes sombreadas
- Huerto escolar didáctico
- Sistema de captación de agua pluvial para uso educativo
- Paneles solares visibles como elemento pedagógico

Arquitectura que educa y inspira a las nuevas generaciones.''',
                'category': 'educational',
                'status': 'completed',
                'location': 'Querétaro, Querétaro, México',
                'area': 4500.00,
                'budget': 32000000.00,
                'start_date': datetime(2021, 8, 1).date(),
                'end_date': datetime(2023, 1, 20).date(),
                'is_featured': False,
                'is_published': True,
            },
            {
                'title': 'Restaurante de Autor',
                'description': '''Espacio gastronómico que fusiona diseño interior vanguardista con cocina de alta gama.

Diseño interior:
- Concepto de cocina abierta como elemento escénico central
- Iluminación diseñada específicamente para resaltar texturas y colores
- Materiales naturales: madera, piedra y cobre
- Mobiliario diseñado a medida
- Cava climatizada visible
- Área de terraza con jardín vertical comestible
- Acústica optimizada para conversación íntima
- Paleta de colores terrosos y cálidos

Un proyecto que eleva la experiencia gastronómica a través de la arquitectura interior.''',
                'category': 'interior',
                'status': 'completed',
                'location': 'Ciudad de México, CDMX, México',
                'area': 280.00,
                'budget': 4200000.00,
                'start_date': datetime(2023, 2, 1).date(),
                'end_date': datetime(2023, 7, 15).date(),
                'is_featured': False,
                'is_published': True,
            },
            {
                'title': 'Parque Urbano Lineal',
                'description': '''Proyecto de recuperación de espacio público que transforma un antiguo corredor ferroviario en un parque lineal de 2.5 km.

Elementos del diseño paisajístico:
- Ciclovía y senderos peatonales accesibles
- Áreas de descanso con pérgolas y mobiliario urbano
- Jardines temáticos (jardín de mariposas, jardín sensorial, jardín de lluvia)
- Plaza cívica con foro al aire libre
- Áreas de juegos infantiles inclusivos
- Zonas de ejercicio al aire libre
- Iluminación LED con paneles solares
- Sistema de riego con agua tratada
- Señalética educativa sobre flora nativa

Un pulmón verde que reconecta a la comunidad con la naturaleza urbana.''',
                'category': 'landscape',
                'status': 'in_progress',
                'location': 'Puebla, Puebla, México',
                'area': 85000.00,
                'budget': 65000000.00,
                'start_date': datetime(2023, 5, 1).date(),
                'end_date': datetime(2025, 10, 30).date(),
                'is_featured': False,
                'is_published': True,
            },
            {
                'title': 'Clínica de Especialidades',
                'description': '''Instalación médica de última generación con enfoque humanista y tecnología de punta.

Distribución funcional:
- 8 consultorios especializados
- Área de diagnóstico con equipamiento avanzado
- Quirófano menor para procedimientos ambulatorios
- Sala de recuperación
- Farmacia integrada
- Áreas de espera diferenciadas por especialidad
- Jardín terapéutico interior
- Estacionamiento con acceso directo para pacientes con movilidad reducida
- Sistema de aire purificado HEPA
- Iluminación natural optimizada para reducir estrés

Arquitectura que promueve la sanación y el bienestar integral.''',
                'category': 'healthcare',
                'status': 'completed',
                'location': 'León, Guanajuato, México',
                'area': 1800.00,
                'budget': 18000000.00,
                'start_date': datetime(2022, 4, 1).date(),
                'end_date': datetime(2023, 3, 30).date(),
                'is_featured': False,
                'is_published': True,
            },
            {
                'title': 'Complejo Industrial Logístico',
                'description': '''Centro de distribución y almacenamiento de última generación con automatización integral.

Especificaciones técnicas:
- 35,000 m² de área de almacenaje
- Sistema de estanterías de alta densidad
- Muelles de carga con niveladoras hidráulicas
- Oficinas administrativas climatizadas
- Área de servicios para operadores
- Patio de maniobras para tractocamiones
- Sistema contra incendios automatizado
- Techumbre con aislamiento térmico de alta eficiencia
- Iluminación natural mediante domos translúcidos
- Celdas solares en cubierta para autoconsumo

Infraestructura industrial que establece nuevos estándares de eficiencia operativa.''',
                'category': 'industrial',
                'status': 'draft',
                'location': 'Silao, Guanajuato, México',
                'area': 35000.00,
                'budget': 95000000.00,
                'start_date': datetime(2024, 2, 1).date(),
                'end_date': datetime(2025, 8, 31).date(),
                'is_featured': False,
                'is_published': False,
            }
        ]
        
        for i, data in enumerate(proyectos_data):
            # Seleccionar arquitecto de manera rotativa
            arquitecto = users['arquitectos'][i % len(users['arquitectos'])]
            
            # Seleccionar clientes aleatorios
            num_clientes = random.randint(1, 3)
            clientes_seleccionados = random.sample(users['clientes'], num_clientes)
            
            project = Project.objects.create(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                status=data['status'],
                location=data['location'],
                area=data['area'],
                budget=data['budget'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                arquitecto=arquitecto,
                is_featured=data['is_featured'],
                is_published=data['is_published'],
                views_count=random.randint(50, 500)
            )
            
            # Asignar clientes
            project.clients.set(clientes_seleccionados)
            project.save()
            
            projects.append(project)
            self.stdout.write(f'   ✓ Proyecto: {project.title[:50]}...')
        
        return projects
    
    def create_project_images(self, projects):
        """Descarga y asocia imágenes a los proyectos."""
        
        # URLs de imágenes de arquitectura de Unsplash (acceso directo)
        # Estas URLs son de la API de Unsplash con imágenes relacionadas a arquitectura
        image_urls = [
            # Arquitectura residencial
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200',
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=1200',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1200',
            'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=1200',
            # Arquitectura moderna
            'https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=1200',
            'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=1200',
            'https://images.unsplash.com/photo-1600607688066-890987a57781?w=1200',
            'https://images.unsplash.com/photo-1600566752355-35792bedcfea?w=1200',
            # Interiores
            'https://images.unsplash.com/photo-1600210492493-0946911123ea?w=1200',
            'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1200',
            'https://images.unsplash.com/photo-1600210491369-e753d80a41f3?w=1200',
            'https://images.unsplash.com/photo-1600210491892-03d54c0aaf87?w=1200',
            # Comercial y corporativo
            'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200',
            'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200',
            'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1200',
            'https://images.unsplash.com/photo-1497366412874-3415097a27e7?w=1200',
            # Espacios públicos
            'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=1200',
            'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200',
            'https://images.unsplash.com/photo-1582407947304-fd86f028f716?w=1200',
            'https://images.unsplash.com/photo-1571055107559-3e67626fa8be?w=1200',
        ]
        
        for project in projects:
            # Número aleatorio de imágenes por proyecto (3-5)
            num_images = random.randint(3, 5)
            
            # Seleccionar URLs aleatorias para este proyecto
            project_image_urls = random.sample(image_urls, min(num_images, len(image_urls)))
            
            for index, url in enumerate(project_image_urls):
                try:
                    # Descargar imagen
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    # Crear nombre de archivo único
                    filename = f"{project.slug}_{index + 1}.jpg"
                    
                    # Crear objeto ProjectImage
                    project_image = ProjectImage(
                        project=project,
                        caption=f'Vista {index + 1} - {project.title}',
                        is_main=(index == 0),  # Primera imagen como principal
                        order=index
                    )
                    
                    # Guardar imagen descargada
                    project_image.image.save(
                        filename,
                        ContentFile(response.content),
                        save=True
                    )
                    
                    self.stdout.write(f'     ✓ Imagen {index + 1}/{num_images} para: {project.title[:40]}...')
                    
                except requests.RequestException as e:
                    self.stdout.write(
                        self.style.WARNING(f'     ⚠ Error descargando imagen para {project.title}: {str(e)}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'     ⚠ Error procesando imagen: {str(e)}')
                    )
    
    def create_messages(self, users, projects):
        """Crea mensajes de ejemplo entre usuarios."""
        messages_data = [
            {
                'sender': users['clientes'][0],
                'recipient': users['arquitectos'][0],
                'project': projects[0],
                'subject': 'Consulta sobre avances del proyecto',
                'body': 'Buen día María, me gustaría saber el estado actual del proyecto y si podemos agendar una visita al sitio esta semana. Quedo atento a tus comentarios.'
            },
            {
                'sender': users['arquitectos'][0],
                'recipient': users['clientes'][0],
                'project': projects[0],
                'subject': 'RE: Consulta sobre avances del proyecto',
                'body': 'Hola Roberto, el proyecto va muy bien. Ya terminamos la estructura principal y estamos iniciando con los acabados. Podemos agendar la visita para el jueves a las 10 AM. Te enviaré las últimas fotografías por separado.'
            },
            {
                'sender': users['clientes'][1],
                'recipient': users['arquitectos'][0],
                'project': projects[1],
                'subject': 'Modificación en diseño de la fachada',
                'body': 'Juan, después de revisar los renders, nos gustaría proponer algunos cambios en los materiales de la fachada. ¿Podríamos agendar una videollamada para discutir las opciones?'
            },
            {
                'sender': users['arquitectos'][0],
                'recipient': users['clientes'][1],
                'project': projects[1],
                'subject': 'RE: Modificación en diseño de la fachada',
                'body': 'Por supuesto Laura, estaré encantado de revisar las propuestas. Te envío mi disponibilidad para esta semana. También prepararé algunas alternativas de materiales que podrían interesarte.'
            },
            {
                'sender': users['clientes'][2],
                'recipient': users['arquitectos'][0],
                'project': projects[2],
                'subject': 'Presupuesto adicional para certificación LEED',
                'body': 'Ana, nos interesa obtener la certificación LEED Platinum. ¿Podrías enviarnos un presupuesto detallado de los cambios necesarios y el cronograma actualizado?'
            },
            {
                'sender': users['admin'],
                'recipient': users['arquitectos'][0],
                'project': None,
                'subject': 'Bienvenida a la plataforma Vulcano',
                'body': 'Bienvenida María a Vulcano. Tu cuenta de arquitecto ha sido activada. Puedes comenzar a crear proyectos y gestionar tus clientes desde el dashboard. Si tienes alguna duda, estamos para ayudarte.'
            },
        ]
        
        for data in messages_data:
            Message.objects.create(
                sender=data['sender'],
                recipient=data['recipient'],
                project=data['project'],
                subject=data['subject'],
                body=data['body'],
                is_read=random.choice([True, False])
            )
            self.stdout.write(f'   ✓ Mensaje: {data["subject"][:50]}...')
    
    def display_summary(self, users, projects):
        """Muestra un resumen de los datos creados."""
        self.stdout.write('📊 Resumen de datos creados:')
        self.stdout.write(f'   • Usuarios totales: {User.objects.count()}')
        self.stdout.write(f'     - Administradores: 1')
        self.stdout.write(f'     - Arquitectos: {len(users["arquitectos"])}')
        self.stdout.write(f'     - Clientes: {len(users["clientes"])}')
        self.stdout.write(f'   • Proyectos: {len(projects)}')
        self.stdout.write(f'   • Imágenes: {ProjectImage.objects.count()}')
        self.stdout.write(f'   • Mensajes: {Message.objects.count()}')
        self.stdout.write('🔐 Credenciales de acceso:')
        self.stdout.write('   Admin:')
        self.stdout.write('     Usuario: admin')
        self.stdout.write('     Contraseña: admin123')
        self.stdout.write('   Arquitectos:')
        self.stdout.write('     Usuario: arquitecto1, arquitecto2, arquitecto3')
        self.stdout.write('     Contraseña: arquitecto123')
        self.stdout.write('   Clientes:')
        self.stdout.write('     Usuario: cliente1, cliente2, cliente3, cliente4')
        self.stdout.write('     Contraseña: cliente123')
        self.stdout.write('🚀 Accede a la plataforma en: http://127.0.0.1:8000/')