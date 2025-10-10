<#
.SYNOPSIS
    Script de automatización de pruebas para Vulcano Platform

.DESCRIPTION
    Ejecuta todas las pruebas del proyecto incluyendo:
    - Verificación de configuración
    - Tests unitarios
    - Tests de integración
    - Generación de reportes

.NOTES
    Autor: QA Team - Vulcano
    Versión: 1.0
    Fecha: 2024
#>

# Configuración
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$ManagePy = Join-Path $ProjectRoot "manage.py"

# Colores para output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success($message) {
    Write-ColorOutput Green "✓ $message"
}

function Write-Error-Custom($message) {
    Write-ColorOutput Red "✗ $message"
}

function Write-Info($message) {
    Write-ColorOutput Cyan "ℹ $message"
}

function Write-Warning-Custom($message) {
    Write-ColorOutput Yellow "⚠ $message"
}

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          VULCANO PLATFORM - TEST RUNNER               ║" -ForegroundColor Cyan
Write-Host "║              Automated Testing Suite                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path $ManagePy)) {
    Write-Error-Custom "No se encuentra manage.py en $ProjectRoot"
    exit 1
}

# Activar entorno virtual
Write-Info "Activando entorno virtual..."
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    Write-Success "Entorno virtual activado"
} else {
    Write-Warning-Custom "No se encontró entorno virtual, usando Python global"
}

# Verificar Python y Django
Write-Info "Verificando versiones..."
Write-Host ""
python --version
Write-Host ""
python -c "import django; print(f'Django {django.get_version()}')"
Write-Host ""

# 1. VERIFICAR CONFIGURACIÓN
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "1. VERIFICACIÓN DE CONFIGURACIÓN" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Info "Ejecutando check de Django..."
try {
    python $ManagePy check
    Write-Success "Configuración válida"
} catch {
    Write-Error-Custom "Error en configuración del proyecto"
    exit 1
}

Write-Host ""

# 2. VERIFICAR MIGRACIONES
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "2. VERIFICACIÓN DE MIGRACIONES" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

Write-Info "Verificando migraciones pendientes..."
try {
    python $ManagePy makemigrations --dry-run --check
    Write-Success "No hay migraciones pendientes"
} catch {
    Write-Warning-Custom "Hay migraciones pendientes"
}

Write-Host ""

# 3. TESTS UNITARIOS
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "3. TESTS UNITARIOS" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

$TestResults = @{
    Models = $false
    Views = $false
    Forms = $false
    Authentication = $false
    Permissions = $false
    Messaging = $false
    Integration = $false
    Utils = $false
}

# Test Models
Write-Info "Ejecutando tests de modelos..."
try {
    python $ManagePy test vulcano.tests.test_models --verbosity=2
    $TestResults.Models = $true
    Write-Success "Tests de modelos: PASSED"
} catch {
    Write-Error-Custom "Tests de modelos: FAILED"
}
Write-Host ""

# Test Views
Write-Info "Ejecutando tests de vistas..."
try {
    python $ManagePy test vulcano.tests.test_views --verbosity=2
    $TestResults.Views = $true
    Write-Success "Tests de vistas: PASSED"
} catch {
    Write-Error-Custom "Tests de vistas: FAILED"
}
Write-Host ""

# Test Forms
Write-Info "Ejecutando tests de formularios..."
try {
    python $ManagePy test vulcano.tests.test_forms --verbosity=2
    $TestResults.Forms = $true
    Write-Success "Tests de formularios: PASSED"
} catch {
    Write-Error-Custom "Tests de formularios: FAILED"
}
Write-Host ""

# Test Authentication
Write-Info "Ejecutando tests de autenticación..."
try {
    python $ManagePy test vulcano.tests.test_authentication --verbosity=2
    $TestResults.Authentication = $true
    Write-Success "Tests de autenticación: PASSED"
} catch {
    Write-Error-Custom "Tests de autenticación: FAILED"
}
Write-Host ""

# Test Permissions
Write-Info "Ejecutando tests de permisos..."
try {
    python $ManagePy test vulcano.tests.test_permissions --verbosity=2
    $TestResults.Permissions = $true
    Write-Success "Tests de permisos: PASSED"
} catch {
    Write-Error-Custom "Tests de permisos: FAILED"
}
Write-Host ""

# Test Messaging
Write-Info "Ejecutando tests de mensajería..."
try {
    python $ManagePy test vulcano.tests.test_messaging --verbosity=2
    $TestResults.Messaging = $true
    Write-Success "Tests de mensajería: PASSED"
} catch {
    Write-Error-Custom "Tests de mensajería: FAILED"
}
Write-Host ""

# Test Integration
Write-Info "Ejecutando tests de integración..."
try {
    python $ManagePy test vulcano.tests.test_integration --verbosity=2
    $TestResults.Integration = $true
    Write-Success "Tests de integración: PASSED"
} catch {
    Write-Error-Custom "Tests de integración: FAILED"
}
Write-Host ""

# Test Utils
Write-Info "Ejecutando tests de utilidades..."
try {
    python $ManagePy test vulcano.tests.test_utils --verbosity=2
    $TestResults.Utils = $true
    Write-Success "Tests de utilidades: PASSED"
} catch {
    Write-Error-Custom "Tests de utilidades: FAILED"
}
Write-Host ""

# 4. COBERTURA DE CÓDIGO (opcional, requiere coverage)
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "4. COBERTURA DE CÓDIGO" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

$CoverageInstalled = python -c "import coverage" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Info "Generando reporte de cobertura..."
    coverage run --source='vulcano' $ManagePy test vulcano
    coverage report
    coverage html
    Write-Success "Reporte HTML generado en htmlcov/index.html"
} else {
    Write-Warning-Custom "Coverage no instalado. Ejecuta: pip install coverage"
}

Write-Host ""

# 5. RESUMEN FINAL
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "5. RESUMEN DE RESULTADOS" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

$TotalTests = $TestResults.Count
$PassedTests = ($TestResults.Values | Where-Object { $_ -eq $true }).Count
$FailedTests = $TotalTests - $PassedTests

Write-Host "Tests Ejecutados: $TotalTests" -ForegroundColor Cyan
Write-Host "Tests Exitosos:   " -NoNewline
Write-ColorOutput Green "$PassedTests"
Write-Host "Tests Fallidos:   " -NoNewline
Write-ColorOutput Red "$FailedTests"
Write-Host ""

# Detalle de resultados
Write-Host "Detalle de Resultados:" -ForegroundColor Cyan
Write-Host "─────────────────────────────────────────────" -ForegroundColor Gray
foreach ($test in $TestResults.GetEnumerator()) {
    $status = if ($test.Value) { "✓ PASS" } else { "✗ FAIL" }
    $color = if ($test.Value) { "Green" } else { "Red" }
    Write-Host "$($test.Key.PadRight(20))" -NoNewline
    Write-ColorOutput $color $status
}

Write-Host ""

# Porcentaje de éxito
$SuccessRate = [math]::Round(($PassedTests / $TotalTests) * 100, 2)
Write-Host "Tasa de Éxito: $SuccessRate%" -ForegroundColor Cyan

Write-Host ""

# Resultado final
if ($FailedTests -eq 0) {
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║          ✓ TODAS LAS PRUEBAS PASARON ✓                ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
    exit 0
} else {
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║          ✗ ALGUNAS PRUEBAS FALLARON ✗                 ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Red
    exit 1
}