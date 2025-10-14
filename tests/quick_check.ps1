<#
.SYNOPSIS
    Verificación Rápida del Sistema Vulcano

.DESCRIPTION
    Script de verificación rápida para validar configuración básica
    y estado del sistema antes de ejecutar tests completos.

.NOTES
    Autor: QA Team - Vulcano
    Versión: 1.0
    Duración estimada: 2-3 minutos
#>

# Configuración
$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ManagePy = Join-Path $ProjectRoot "manage.py"

# Colores
function Write-Success($msg) { Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Info($msg) { Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "⚠ $msg" -ForegroundColor Yellow }

# Banner
Clear-Host
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        VULCANO - VERIFICACIÓN RÁPIDA DEL SISTEMA      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$checks = @{
    Total = 0
    Passed = 0
    Failed = 0
    Warnings = 0
}

# 1. Verificar Python
Write-Info "1. Verificando Python..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.") {
        Write-Success "Python instalado: $pythonVersion"
        $checks.Passed++
    } else {
        Write-Fail "Python no encontrado o versión incorrecta"
        $checks.Failed++
    }
} catch {
    Write-Fail "Python no encontrado"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 2. Verificar Django
Write-Info "2. Verificando Django..."
try {
    $djangoVersion = python -c "import django; print(django.get_version())" 2>&1
    if ($djangoVersion -match "\d+\.\d+") {
        Write-Success "Django instalado: $djangoVersion"
        $checks.Passed++
    } else {
        Write-Fail "Django no instalado"
        $checks.Failed++
    }
} catch {
    Write-Fail "Django no instalado"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 3. Verificar archivo .env
Write-Info "3. Verificando archivo .env..."
$envFile = Join-Path $ProjectRoot ".env"
if (Test-Path $envFile) {
    Write-Success "Archivo .env encontrado"
    $checks.Passed++
    
    # Verificar variables críticas
    $envContent = Get-Content $envFile -Raw
    $criticalVars = @("SECRET_KEY", "DB_NAME", "DB_USER", "DB_PASSWORD")
    $missingVars = @()
    
    foreach ($var in $criticalVars) {
        if ($envContent -notmatch $var) {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Warn "Variables faltantes en .env: $($missingVars -join ', ')"
        $checks.Warnings++
    }
} else {
    Write-Fail "Archivo .env no encontrado"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 4. Verificar manage.py
Write-Info "4. Verificando manage.py..."
if (Test-Path $ManagePy) {
    Write-Success "manage.py encontrado"
    $checks.Passed++
} else {
    Write-Fail "manage.py no encontrado en $ProjectRoot"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 5. Verificar conexión a Base de Datos
Write-Info "5. Verificando conexión a Oracle..."
try {
    $dbCheck = python $ManagePy check --database default 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Conexión a Oracle exitosa"
        $checks.Passed++
    } else {
        Write-Fail "Error de conexión a Oracle"
        Write-Host $dbCheck -ForegroundColor Yellow
        $checks.Failed++
    }
} catch {
    Write-Fail "No se pudo verificar conexión a BD"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 6. Verificar migraciones
Write-Info "6. Verificando migraciones..."
try {
    $migrations = python $ManagePy showmigrations --plan 2>&1
    if ($LASTEXITCODE -eq 0) {
        $unapplied = ($migrations | Select-String "\[ \]").Count
        if ($unapplied -eq 0) {
            Write-Success "Todas las migraciones aplicadas"
            $checks.Passed++
        } else {
            Write-Warn "$unapplied migraciones pendientes"
            $checks.Warnings++
            $checks.Passed++
        }
    } else {
        Write-Fail "Error al verificar migraciones"
        $checks.Failed++
    }
} catch {
    Write-Fail "Error al verificar migraciones"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 7. Verificar estructura de directorios
Write-Info "7. Verificando estructura de directorios..."
$requiredDirs = @(
    "vulcano",
    "vulcano/templates",
    "vulcano/static",
    "vulcano/tests",
    "media"
)
$missingDirs = @()
foreach ($dir in $requiredDirs) {
    $fullPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $fullPath)) {
        $missingDirs += $dir
    }
}
if ($missingDirs.Count -eq 0) {
    Write-Success "Estructura de directorios correcta"
    $checks.Passed++
} else {
    Write-Fail "Directorios faltantes: $($missingDirs -join ', ')"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 8. Verificar archivos estáticos
Write-Info "8. Verificando archivos estáticos..."
$staticFiles = @(
    "vulcano/static/css/main.css",
    "vulcano/static/js/main.js"
)
$missingStatic = @()
foreach ($file in $staticFiles) {
    $fullPath = Join-Path $ProjectRoot $file
    if (-not (Test-Path $fullPath)) {
        $missingStatic += $file
    }
}
if ($missingStatic.Count -eq 0) {
    Write-Success "Archivos estáticos encontrados"
    $checks.Passed++
} else {
    Write-Warn "Archivos estáticos faltantes: $($missingStatic -join ', ')"
    $checks.Warnings++
    $checks.Passed++
}
$checks.Total++
Write-Host ""

# 9. Verificar templates
Write-Info "9. Verificando templates..."
$templates = @(
    "vulcano/templates/base.html",
    "vulcano/templates/home.html"
)
$missingTemplates = @()
foreach ($template in $templates) {
    $fullPath = Join-Path $ProjectRoot $template
    if (-not (Test-Path $fullPath)) {
        $missingTemplates += $template
    }
}
if ($missingTemplates.Count -eq 0) {
    Write-Success "Templates principales encontrados"
    $checks.Passed++
} else {
    Write-Fail "Templates faltantes: $($missingTemplates -join ', ')"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 10. Verificar dependencias
Write-Info "10. Verificando dependencias críticas..."
$dependencies = @("django", "oracledb", "pillow", "python-dotenv")
$missingDeps = @()
foreach ($dep in $dependencies) {
    $check = python -c "import $($dep.Replace('-', '_'))" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingDeps += $dep
    }
}
if ($missingDeps.Count -eq 0) {
    Write-Success "Todas las dependencias instaladas"
    $checks.Passed++
} else {
    Write-Fail "Dependencias faltantes: $($missingDeps -join ', ')"
    Write-Info "Ejecutar: pip install $($missingDeps -join ' ')"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 11. Verificar configuración de Django
Write-Info "11. Verificando configuración de Django..."
try {
    $djangoCheck = python $ManagePy check 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Configuración de Django válida"
        $checks.Passed++
    } else {
        Write-Fail "Errores en configuración de Django:"
        Write-Host $djangoCheck -ForegroundColor Yellow
        $checks.Failed++
    }
} catch {
    Write-Fail "Error al verificar configuración"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# 12. Test rápido de importación
Write-Info "12. Verificando importación de modelos..."
try {
    $importCheck = python -c "from vulcano.models import Project, UserProfile, Message; print('OK')" 2>&1
    if ($importCheck -match "OK") {
        Write-Success "Modelos importan correctamente"
        $checks.Passed++
    } else {
        Write-Fail "Error al importar modelos"
        Write-Host $importCheck -ForegroundColor Yellow
        $checks.Failed++
    }
} catch {
    Write-Fail "Error al importar modelos"
    $checks.Failed++
}
$checks.Total++
Write-Host ""

# RESUMEN
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "RESUMEN DE VERIFICACIÓN" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Host "Total de verificaciones: " -NoNewline
Write-Host $checks.Total -ForegroundColor Cyan

Write-Host "Verificaciones exitosas: " -NoNewline
Write-Host $checks.Passed -ForegroundColor Green

Write-Host "Verificaciones fallidas:  " -NoNewline
Write-Host $checks.Failed -ForegroundColor Red

Write-Host "Advertencias:            " -NoNewline
Write-Host $checks.Warnings -ForegroundColor Yellow

Write-Host ""

$successRate = [math]::Round(($checks.Passed / $checks.Total) * 100, 2)
Write-Host "Tasa de éxito: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

Write-Host ""

# Resultado final
if ($checks.Failed -eq 0) {
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║       ✓ SISTEMA LISTO PARA EJECUTAR TESTS ✓           ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Info "Ejecutar: .\tests\test_runner.ps1"
    exit 0
} elseif ($checks.Failed -le 2) {
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║    ⚠ SISTEMA CON ADVERTENCIAS - REVISAR ERRORES ⚠    ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║     ✗ SISTEMA NO LISTO - CORREGIR ERRORES ✗          ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Red
    exit 1
}