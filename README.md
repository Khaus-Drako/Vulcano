# Documentación de Vulcano

## Descripción General
Vulcano es una plataforma de gestión de proyectos arquitectónicos que permite a arquitectos y clientes conectarse y colaborar en proyectos.

## Requisitos del Sistema
- Python 3.13+
- Django 5.2.6
- Base de datos compatible (SQLite en desarrollo, PostgreSQL recomendado para producción)
- Servidor web Nginx/Apache
- Gunicorn para servir la aplicación
- Certificado SSL para HTTPS

## Instalación

### 1. Clonar el Repositorio
```bash
git clone [URL_DEL_REPOSITORIO]
cd Vulcano
```

### 2. Configurar el Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto con las siguientes variables:
```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
SECRET_KEY=tu-clave-secreta
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/vulcano
```

### 4. Inicializar la Base de Datos
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Recolectar Archivos Estáticos
```bash
python manage.py collectstatic
```

### 6. Configurar el Servidor Web
- Copiar `nginx.conf` a `/etc/nginx/sites-available/`
- Crear enlace simbólico en `sites-enabled`
- Configurar certificados SSL
- Reiniciar Nginx

### 7. Configurar Gunicorn
- Copiar `gunicorn.service` a `/etc/systemd/system/`
- Habilitar e iniciar el servicio

## Mantenimiento

### Backups
- Base de datos: Backups diarios automáticos
- Archivos de medios: Backups semanales
- Logs: Rotación diaria

### Monitoreo
- Revisar logs en `/var/log/vulcano/`
- Monitorear uso de recursos
- Verificar certificados SSL mensualmente

### Actualización
1. Activar modo mantenimiento
2. Realizar backup
3. Actualizar código
4. Aplicar migraciones
5. Recolectar estáticos
6. Reiniciar servicios

## Estructura del Proyecto
```
Vulcano/
├── vulcano/            # Aplicación principal
├── webVulcano/         # Configuración del proyecto
├── media/              # Archivos subidos
├── staticfiles/        # Archivos estáticos
└── requirements.txt    # Dependencias
```

## Características Principales
- Gestión de proyectos arquitectónicos
- Sistema de mensajería interno
- Gestión de usuarios y perfiles
- Galería de proyectos
- Sistema de roles y permisos

## Solución de Problemas
- Revisar logs en `/var/log/vulcano/`
- Verificar permisos de archivos
- Comprobar conexión a la base de datos
- Validar configuración de Nginx/Gunicorn

## Contacto y Soporte
- Email: soporte@vulcano.com
- Documentación: docs.vulcano.com
- Reportar problemas: github.com/vulcano/issues