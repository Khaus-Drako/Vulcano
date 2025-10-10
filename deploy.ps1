# deploy.ps1
# Script de despliegue automatizado para Vulcano - Windows 11
# Ejecutar como: .\deploy.ps1

param(
    [switch]$Full,
    [switch]$Migrate,
    [switch]$Static,
    [switch]$Run,
    [switch]$Production
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   VULCANO - DESPLIEGUE AUTOMATIZADO   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------
# [1] Verificar instalación de Python
# ---------------------------------------------------------
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python detectado: $pythonVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Python no encontrado. Por favor, instala Python 3.13.x" -ForegroundColor Red
        return $false
    }
}

# ---------------------------------------------------------
# [2] Crear entorno virtual
# ---------------------------------------------------------
function New-VirtualEnv {
    Write-Host "`n[1/7] Creando entorno virtual..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        Write-Host "Entorno virtual ya existe. Eliminando..." -ForegroundColor Gray
        Remove-Item -Recurse -Force venv
    }
    
    python -m venv venv
    
    if ($?) {
        Write-Host "Entorno virtual creado exitosamente" -ForegroundColor Green
    } else {
        Write-Host "Error al crear entorno virtual" -ForegroundColor Red
        exit 1
    }
}

# ---------------------------------------------------------
# [3] Activar entorno virtual
# ---------------------------------------------------------
function Enable-VirtualEnv {
    Write-Host "`n[2/7] Activando entorno virtual..." -ForegroundColor Yellow
    
    & .\venv\Scripts\Activate.ps1
    
    if ($?) {
        Write-Host "Entorno virtual activado" -ForegroundColor Green
    } else {
        Write-Host "Error al activar entorno virtual" -ForegroundColor Red
        exit 1
    }
}

# ---------------------------------------------------------
# [4] Instalar dependencias
# ---------------------------------------------------------
function Install-Dependencies {
    Write-Host "`n[3/7] Instalando dependencias..." -ForegroundColor Yellow
    
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    if ($?) {
        Write-Host "Dependencias instaladas correctamente" -ForegroundColor Green
    } else {
        Write-Host "Error al instalar dependencias" -ForegroundColor Red
        exit 1
    }
}

# ---------------------------------------------------------
# [5] Verificar archivo .env
# ---------------------------------------------------------
function Test-EnvFile {
    Write-Host "`n[4/7] Verificando configuración..." -ForegroundColor Yellow
    
    if (-not (Test-Path ".env")) {
        Write-Host "Archivo .env no encontrado" -ForegroundColor Yellow
        
        if (Test-Path ".env.example") {
            Write-Host " → Copiando .env.example a .env" -ForegroundColor Gray
            Copy-Item .env.example .env
            Write-Host "IMPORTANTE: Edita el archivo .env con tus credenciales" -ForegroundColor Yellow
            Write-Host "Presiona Enter cuando hayas configurado .env..." -ForegroundColor Yellow
            Read-Host
        } else {
            Write-Host "Archivo .env.example no encontrado" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "Archivo .env configurado" -ForegroundColor Green
}

# ---------------------------------------------------------
# [6] Migraciones
# ---------------------------------------------------------
function Invoke-Migrations {
    Write-Host "`n[5/7] Ejecutando migraciones..." -ForegroundColor Yellow
    
    python manage.py makemigrations
    python manage.py migrate
    
    if ($?) {
        Write-Host "Migraciones aplicadas correctamente" -ForegroundColor Green
    } else {
        Write-Host "Error al aplicar migraciones" -ForegroundColor Red
        Write-Host "Verifica la conexión a Oracle Database" -ForegroundColor Yellow
        exit 1
    }
}

# ---------------------------------------------------------
# [7] Archivos estáticos
# ---------------------------------------------------------
function Invoke-CollectStatic {
    Write-Host "`n[6/7] Recolectando archivos estáticos..." -ForegroundColor Yellow
    
    python manage.py collectstatic --noinput
    
    if ($?) {
        Write-Host "Archivos estáticos recolectados" -ForegroundColor Green
    } else {
        Write-Host "Error al recolectar archivos estáticos (no crítico)" -ForegroundColor Yellow
    }
}

# ---------------------------------------------------------
# [8] Crear superusuario
# ---------------------------------------------------------
function New-Superuser {
    Write-Host "`n[OPCIONAL] Crear superusuario..." -ForegroundColor Yellow
    $create = Read-Host "¿Deseas crear un superusuario ahora? (s/n)"
    
    if ($create -eq "s" -or $create -eq "S") {
        python manage.py createsuperuser
    }
}

# ---------------------------------------------------------
# [9] Iniciar servidor desarrollo
# ---------------------------------------------------------
function Start-Server {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   INICIANDO SERVIDOR DE DESARROLLO    " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Servidor disponible en: http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "Panel de administración: http://127.0.0.1:8000/admin" -ForegroundColor Green
    Write-Host ""
    Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
    Write-Host ""
    
    python manage.py runserver
}

# ---------------------------------------------------------
# [10] Iniciar servidor producción
# ---------------------------------------------------------
function Start-ProductionServer {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   INICIANDO SERVIDOR DE PRODUCCIÓN    " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Verificar Gunicorn
    Write-Host "Verificando Gunicorn..." -ForegroundColor Yellow
    $gunicornInstalled = pip list | Select-String -Pattern "gunicorn"
    
    if (-not $gunicornInstalled) {
        Write-Host "Instalando Gunicorn..." -ForegroundColor Gray
        pip install gunicorn
        if (-not $?) {
            Write-Host "Error al instalar Gunicorn" -ForegroundColor Red
            exit 1
        }
    }

    # Copiar archivo de producción
    if (Test-Path ".env.production") {
        Write-Host "Copiando configuración de producción..." -ForegroundColor Yellow
        Copy-Item .env.production .env -Force
        Write-Host "Archivo .env configurado para producción" -ForegroundColor Green
    } else {
        Write-Host "Advertencia: No se encontró .env.production" -ForegroundColor Yellow
    }

    # Recolectar estáticos y migrar por seguridad
    Write-Host "`nPreparando entorno de producción..." -ForegroundColor Yellow
    python manage.py collectstatic --noinput
    python manage.py migrate
    python manage.py check --deploy

    # Configurar logs
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs"
    }

    $env:DJANGO_SETTINGS_MODULE = "webVulcano.settings"
    
    Write-Host "`nIniciando Gunicorn..." -ForegroundColor Green
    Write-Host "Servidor disponible en: http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
    Write-Host ""

    # Iniciar Gunicorn con configuración de producción
    python -m gunicorn webVulcano.wsgi:application `
        --workers 3 `
        --bind 0.0.0.0:8000 `
        --access-logfile logs/access.log `
        --error-logfile logs/error.log `
        --capture-output `
        --enable-stdio-inheritance
}

# ---------------------------------------------------------
# FLUJO PRINCIPAL
# ---------------------------------------------------------
Write-Host "Directorio de trabajo: $PWD" -ForegroundColor Gray
Write-Host ""

if (-not (Test-Python)) { exit 1 }

if ($Migrate) { Enable-VirtualEnv; Invoke-Migrations; exit 0 }
if ($Static) { Enable-VirtualEnv; Invoke-CollectStatic; exit 0 }
if ($Run) { Enable-VirtualEnv; Start-Server; exit 0 }
if ($Production) { Enable-VirtualEnv; Start-ProductionServer; exit 0 }

# Despliegue completo
if ($Full -or (-not $Migrate -and -not $Static -and -not $Run -and -not $Production)) {
    New-VirtualEnv
    Enable-VirtualEnv
    Install-Dependencies
    Test-EnvFile
    Invoke-Migrations
    Invoke-CollectStatic
    New-Superuser

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "   DESPLIEGUE COMPLETADO EXITOSAMENTE  " -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Para iniciar el servidor de desarrollo:" -ForegroundColor Green
    Write-Host "  .\deploy.ps1 -Run" -ForegroundColor White
    Write-Host ""
    Write-Host "Para iniciar el servidor de producción:" -ForegroundColor Green
    Write-Host "  .\deploy.ps1 -Production" -ForegroundColor White
    Write-Host ""

    $startType = Read-Host "¿Deseas iniciar el servidor ahora? (d=desarrollo, p=producción, n=no)"
    if ($startType -eq "d" -or $startType -eq "D") { Start-Server }
    elseif ($startType -eq "p" -or $startType -eq "P") { Start-ProductionServer }
}