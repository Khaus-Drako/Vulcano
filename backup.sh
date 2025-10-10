#!/bin/bash

# Configuración
BACKUP_DIR="/path/to/backups"
APP_DIR="/path/to/vulcano"
DB_NAME="vulcano"
DB_USER="vulcano"
KEEP_DAYS=30

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR/database"
mkdir -p "$BACKUP_DIR/media"

# Timestamp para los nombres de archivo
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup de la base de datos
echo "Creando backup de la base de datos..."
pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/database/db_backup_$TIMESTAMP.sql"
gzip "$BACKUP_DIR/database/db_backup_$TIMESTAMP.sql"

# Backup de archivos media
echo "Creando backup de archivos media..."
tar -czf "$BACKUP_DIR/media/media_backup_$TIMESTAMP.tar.gz" -C "$APP_DIR" media/

# Eliminar backups antiguos (más de 30 días)
echo "Eliminando backups antiguos..."
find "$BACKUP_DIR/database" -name "db_backup_*.sql.gz" -type f -mtime +$KEEP_DAYS -delete
find "$BACKUP_DIR/media" -name "media_backup_*.tar.gz" -type f -mtime +$KEEP_DAYS -delete

echo "Backup completado exitosamente."

# Verificar espacio en disco
df -h "$BACKUP_DIR"