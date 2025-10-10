# Lista de comprobación de seguridad para Vulcano

1. Configuración de Django:
   - DEBUG = False en producción
   - SECRET_KEY única y segura
   - ALLOWED_HOSTS configurado correctamente
   - SESSION_COOKIE_SECURE = True
   - CSRF_COOKIE_SECURE = True
   - SECURE_SSL_REDIRECT = True
   - SECURE_HSTS_SECONDS = 31536000
   - SECURE_HSTS_INCLUDE_SUBDOMAINS = True
   - SECURE_HSTS_PRELOAD = True
   - SECURE_CONTENT_TYPE_NOSNIFF = True
   - SECURE_BROWSER_XSS_FILTER = True
   - X_FRAME_OPTIONS = 'DENY'

2. Configuración del Servidor:
   - Certificados SSL instalados y actualizados
   - Firewall configurado (permitir solo puertos 80, 443)
   - Fail2ban instalado y configurado
   - SELinux/AppArmor habilitado
   - Permisos de archivos restringidos
   - Backups automáticos configurados

3. Base de Datos:
   - Contraseñas seguras
   - Acceso restringido por IP
   - Backups regulares
   - Conexiones SSL habilitadas

4. Monitoreo:
   - Sistema de logs configurado
   - Alertas configuradas
   - Monitoreo de recursos
   - Registro de accesos sospechosos

5. Mantenimiento Regular:
   - Actualizaciones de seguridad automáticas
   - Rotación de logs
   - Revisión de logs de acceso
   - Pruebas de restauración de backups