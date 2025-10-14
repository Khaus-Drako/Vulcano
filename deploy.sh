#!/bin/bash

echo "Desplegando Vulcano en producción..."

# 1. Activar entorno virtual (ajusta según tu configuración)
# source /ruta/a/tu/entorno/virtual/bin/activate

# 2. Instalar o actualizar dependencias
pip install -r requirements.txt

# 3. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 4. Aplicar migraciones de base de datos
python manage.py migrate

# 5. Reiniciar servicios
# Ajusta estos comandos según tu configuración de servidor
# sudo systemctl restart gunicorn
# sudo systemctl restart nginx

echo "Despliegue completado."